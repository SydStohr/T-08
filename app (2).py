import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import re
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentiScope · Review Analyser",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #2a2d3e;
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.15em;
    color: #6c6f80 !important;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* Main area */
.main .block-container { padding-top: 2rem; max-width: 1200px; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 50%, #0f1117 100%);
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at 60% 40%, rgba(99,102,241,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    color: #f4f4f5;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.hero .subtitle {
    font-size: 1rem;
    color: #71717a;
    margin: 0;
    font-weight: 300;
}
.hero .badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Metric cards */
.metric-card {
    background: #16181f;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.metric-card .val {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    margin: 0.2rem 0;
}
.metric-card .lbl {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #71717a;
}
.pos  { color: #34d399; }
.neu  { color: #fbbf24; }
.neg  { color: #f87171; }
.acc  { color: #818cf8; }

/* Section headers */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6c6f80;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #2a2d3e;
}

/* Review card */
.review-card {
    background: #16181f;
    border: 1px solid #2a2d3e;
    border-left: 3px solid;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.review-card.pos { border-left-color: #34d399; }
.review-card.neg { border-left-color: #f87171; }
.review-card.neu { border-left-color: #fbbf24; }

/* Live analyser box */
.live-box {
    background: #16181f;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1rem;
}
.score-pill {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    font-weight: 700;
    margin-top: 0.5rem;
}

/* Plotly charts – dark background */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── VADER helpers ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_analyzer():
    return SentimentIntensityAnalyzer()

analyzer = load_analyzer()

STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "he","she","it","they","them","this","that","which","who","whom","what",
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","was","are","were","be","been","being","have","has","had","do","does",
    "did","will","would","could","should","may","might","shall","just","very",
    "so","not","no","nor","too","very","then","than","also","up","down","out",
    "about","from","by","as","into","through","after","before","more","other",
    "some","such","all","each","any","over","own","same","how","when","where",
    "why","here","there","get","got","one","two","even","still","only","now",
    "if","while","these","those","been","its"
}

def score_text(text):
    vs = analyzer.polarity_scores(str(text))
    c  = vs['compound']
    if c >= 0.05:
        label = 'Positive'
    elif c <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'
    return c, label

def run_vader(df, col):
    results = df[col].apply(score_text)
    df = df.copy()
    df['compound_score']  = results.apply(lambda x: x[0])
    df['sentiment_label'] = results.apply(lambda x: x[1])
    return df

def top_words(series, n=20):
    words = []
    for txt in series.astype(str):
        tokens = re.findall(r"[a-z']+", txt.lower())
        words += [w for w in tokens if w not in STOPWORDS and len(w) > 2]
    return Counter(words).most_common(n)

# ── Colour helpers ────────────────────────────────────────────────────────────
LABEL_COLOR = {'Positive': '#34d399', 'Neutral': '#fbbf24', 'Negative': '#f87171'}
LABEL_CSS   = {'Positive': 'pos', 'Neutral': 'neu', 'Negative': 'neg'}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## SentiScope")
    st.markdown("---")

    st.markdown("## Upload")
    uploaded = st.file_uploader(
        "CSV with reviews", type=["csv"],
        help="Your file needs at least one text column."
    )

    st.markdown("## Settings")
    text_col = None
    score_col = None

    if uploaded:
        preview = pd.read_csv(uploaded, nrows=5)
        uploaded.seek(0)
        cols = list(preview.columns)

        text_col = st.selectbox("Review text column", cols,
                                index=cols.index("Text") if "Text" in cols else 0)

        score_col = st.selectbox(
            "Star-rating column (optional)",
            ["— none —"] + cols,
            index=(["— none —"] + cols).index("Score") if "Score" in cols else 0
        )
        if score_col == "— none —":
            score_col = None

    st.markdown("## Filters")
    sentiment_filter = st.multiselect(
        "Show sentiments",
        ["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"]
    )

    st.markdown("---")
    st.markdown(
        "<span style='font-size:0.7rem;color:#4a4d5e;'>Powered by VADER · Streamlit</span>",
        unsafe_allow_html=True
    )

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='badge'>NLP · Sentiment Analysis</div>
    <h1>SentiScope</h1>
    <p class='subtitle'>Upload your customer reviews CSV and instantly surface sentiment insights — no ML training required.</p>
</div>
""", unsafe_allow_html=True)

# ── Live analyser (always visible) ───────────────────────────────────────────
st.markdown("<div class='section-title'>Live Analyser</div>", unsafe_allow_html=True)

custom_text = st.text_area(
    "Paste any review to analyse it instantly:",
    placeholder="e.g. The product quality is great but the delivery was disappointingly slow...",
    height=100,
    label_visibility="collapsed"
)

if custom_text.strip():
    c, lbl = score_text(custom_text)
    color = LABEL_COLOR[lbl]
    st.markdown(f"""
    <div class='live-box'>
        <div style='font-size:0.8rem;color:#71717a;margin-bottom:0.3rem;'>RESULT</div>
        <span class='score-pill' style='background:{color}22;color:{color};border:1px solid {color}55;'>
            {lbl} &nbsp;·&nbsp; {c:+.4f}
        </span>
        <div style='margin-top:1rem;display:flex;gap:1rem;font-size:0.85rem;color:#a1a1aa;'>
            <span>😊 Positive signal: <b style='color:#f4f4f5'>{analyzer.polarity_scores(custom_text)["pos"]:.2f}</b></span>
            <span>😐 Neutral signal: <b style='color:#f4f4f5'>{analyzer.polarity_scores(custom_text)["neu"]:.2f}</b></span>
            <span>😞 Negative signal: <b style='color:#f4f4f5'>{analyzer.polarity_scores(custom_text)["neg"]:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Dataset section ───────────────────────────────────────────────────────────
if uploaded and text_col:
    with st.spinner("Running VADER on your dataset…"):
        df_raw = pd.read_csv(uploaded)
        df = run_vader(df_raw, text_col)

    # Apply sidebar filter
    df_view = df[df['sentiment_label'].isin(sentiment_filter)].copy()

    # ── KPI cards ─────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)

    total   = len(df)
    n_pos   = (df['sentiment_label'] == 'Positive').sum()
    n_neu   = (df['sentiment_label'] == 'Neutral').sum()
    n_neg   = (df['sentiment_label'] == 'Negative').sum()
    mean_sc = df['compound_score'].mean()

    # Accuracy if star col exists
    acc_html = ""
    if score_col:
        def star_label(s):
            try:
                s = int(s)
            except Exception:
                return None
            if s >= 4: return 'Positive'
            if s == 3: return 'Neutral'
            return 'Negative'
        df['score_label'] = df[score_col].apply(star_label)
        valid = df[df['score_label'].notna()]
        acc = (valid['sentiment_label'] == valid['score_label']).mean() if len(valid) else None
        if acc is not None:
            acc_html = f"""
            <div class='metric-card'>
                <div class='lbl'>VADER Accuracy</div>
                <div class='val acc'>{acc:.1%}</div>
                <div class='lbl'>vs star ratings</div>
            </div>"""

    c1, c2, c3, c4, c5 = st.columns(5)
    metric_html = f"""
    <div class='metric-card'>
        <div class='lbl'>Total Reviews</div>
        <div class='val' style='color:#f4f4f5'>{total:,}</div>
    </div>"""
    c1.markdown(metric_html, unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='lbl'>Positive</div><div class='val pos'>{n_pos:,}</div><div class='lbl'>{n_pos/total:.1%}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='lbl'>Neutral</div><div class='val neu'>{n_neu:,}</div><div class='lbl'>{n_neu/total:.1%}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div class='lbl'>Negative</div><div class='val neg'>{n_neg:,}</div><div class='lbl'>{n_neg/total:.1%}</div></div>", unsafe_allow_html=True)
    if acc_html:
        c5.markdown(acc_html, unsafe_allow_html=True)
    else:
        c5.markdown(f"<div class='metric-card'><div class='lbl'>Avg Score</div><div class='val' style='color:#818cf8'>{mean_sc:+.3f}</div></div>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Distributions</div>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)

    with ch1:
        pie = go.Figure(go.Pie(
            labels=['Positive','Neutral','Negative'],
            values=[n_pos, n_neu, n_neg],
            marker_colors=['#34d399','#fbbf24','#f87171'],
            hole=0.55,
            textinfo='percent+label',
            textfont_size=13,
        ))
        pie.update_layout(
            title="Sentiment Split",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#a1a1aa',
            showlegend=False,
            margin=dict(t=50,b=20,l=20,r=20),
        )
        st.plotly_chart(pie, use_container_width=True)

    with ch2:
        hist = go.Figure(go.Histogram(
            x=df['compound_score'],
            nbinsx=60,
            marker_color='#818cf8',
            marker_line_width=0,
            opacity=0.85,
        ))
        hist.add_vline(x=0.05,  line_dash="dash", line_color="#34d399", annotation_text="Pos threshold")
        hist.add_vline(x=-0.05, line_dash="dash", line_color="#f87171", annotation_text="Neg threshold")
        hist.update_layout(
            title="Compound Score Distribution",
            xaxis_title="Compound Score",
            yaxis_title="Count",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#a1a1aa',
            xaxis=dict(gridcolor='#2a2d3e', range=[-1,1]),
            yaxis=dict(gridcolor='#2a2d3e'),
            margin=dict(t=50,b=40,l=50,r=20),
        )
        st.plotly_chart(hist, use_container_width=True)

    # ── Word frequency ──────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Top Words by Sentiment</div>", unsafe_allow_html=True)

    w1, w2, w3 = st.columns(3)
    for col_w, sentiment, color in [
        (w1, 'Positive', '#34d399'),
        (w2, 'Neutral',  '#fbbf24'),
        (w3, 'Negative', '#f87171'),
    ]:
        subset = df[df['sentiment_label'] == sentiment][text_col]
        if len(subset) == 0:
            col_w.info(f"No {sentiment} reviews.")
            continue
        words = top_words(subset, n=15)
        if words:
            wdf = pd.DataFrame(words, columns=['word','count'])
            bar = go.Figure(go.Bar(
                y=wdf['word'], x=wdf['count'],
                orientation='h',
                marker_color=color,
                marker_opacity=0.85,
            ))
            bar.update_layout(
                title=sentiment,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#a1a1aa',
                xaxis=dict(gridcolor='#2a2d3e'),
                yaxis=dict(autorange='reversed', gridcolor='#2a2d3e'),
                margin=dict(t=40,b=20,l=10,r=20),
                height=380,
            )
            col_w.plotly_chart(bar, use_container_width=True)

    # ── Accuracy deep-dive if star col present ──────────────────────────────
    if score_col and 'score_label' in df.columns:
        st.markdown("<div class='section-title'>Accuracy vs Star Ratings</div>", unsafe_allow_html=True)

        from sklearn.metrics import confusion_matrix
        labels = ['Positive','Neutral','Negative']
        valid2 = df[df['score_label'].notna()]
        cm = confusion_matrix(valid2['score_label'], valid2['sentiment_label'], labels=labels)
        cm_df = pd.DataFrame(cm, index=labels, columns=labels)

        hm = go.Figure(go.Heatmap(
            z=cm, x=labels, y=labels,
            colorscale=[[0,'#16181f'],[0.5,'#312e81'],[1,'#818cf8']],
            text=cm, texttemplate='%{text:,}',
            textfont_size=14,
            showscale=False,
        ))
        hm.update_layout(
            title="Confusion Matrix (True=rows · Predicted=cols)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#a1a1aa',
            xaxis_title="VADER Prediction",
            yaxis_title="Star Rating Label",
            margin=dict(t=50,b=40,l=100,r=20),
            height=380,
        )
        st.plotly_chart(hm, use_container_width=True)

    # ── Sample reviews ──────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Sample Reviews</div>", unsafe_allow_html=True)

    n_samples = st.slider("Number of samples per sentiment", 1, 10, 3)

    for sentiment in ["Positive", "Neutral", "Negative"]:
        if sentiment not in sentiment_filter:
            continue
        subset = df_view[df_view['sentiment_label'] == sentiment]
        if len(subset) == 0:
            continue
        st.markdown(f"**{sentiment}**")
        samples = subset.sample(min(n_samples, len(subset)), random_state=42)
        for _, row in samples.iterrows():
            css_cls = LABEL_CSS[sentiment]
            review_text = str(row[text_col])[:400]
            score_badge = f"<span style='font-size:0.8rem;color:{LABEL_COLOR[sentiment]};font-family:monospace'>{row['compound_score']:+.4f}</span>"
            st.markdown(f"""
            <div class='review-card {css_cls}'>
                <div style='font-size:0.85rem;color:#d4d4d8;margin-bottom:0.5rem;'>{review_text}{'…' if len(str(row[text_col])) > 400 else ''}</div>
                {score_badge}
            </div>""", unsafe_allow_html=True)

    # ── Download ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Export</div>", unsafe_allow_html=True)

    export_cols = [text_col, 'compound_score', 'sentiment_label']
    if score_col:
        export_cols += [score_col]
    if 'score_label' in df.columns:
        export_cols += ['score_label']

    csv_buf = io.StringIO()
    df[export_cols].to_csv(csv_buf, index=False)
    st.download_button(
        "⬇ Download scored reviews (CSV)",
        data=csv_buf.getvalue(),
        file_name="sentiment_results.csv",
        mime="text/csv",
    )

else:
    # ── Empty state ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Getting Started</div>", unsafe_allow_html=True)
    st.info(
        "Upload a CSV in the sidebar to analyse your full dataset.  \n"
        "Your file must contain at least one column with review text.  \n"
        "Optionally include a star-rating column (1–5) to measure VADER accuracy."
    )
    st.markdown("""
    **CSV format example:**

    | Text | Score |
    |---|---|
    | This product is amazing! | 5 |
    | Terrible quality, very disappointed. | 1 |
    | It's okay, nothing special. | 3 |

    The app will score every row with VADER and surface interactive charts, word frequency analysis, sample reviews and a downloadable results file.
    """)
