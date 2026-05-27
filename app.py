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
    page_title="FixPart · Review Analyser",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── FixPart Trustpilot reviews (pre-loaded) ──────────────────────────────────
FIXPART_REVIEWS = [
    {"Text": "Donderdag besteld en vrijdag afgeleverd. Snelle bezorging van het juiste product. Top bedrijf!", "Score": 5},
    {"Text": "Ze versturen originele onderdelen, niet zoals andere bedrijven onderdelen van AliExpress. Gewoon een top bedrijf.", "Score": 5},
    {"Text": "Snelle bezorging van het juiste product. Geen 5 sterren, omdat het product niet helemaal de kwaliteit heeft van het origineel.", "Score": 4},
    {"Text": "Maalwerk voor mijn Bosch inbouw koffieapparaat gekocht. Besteld op vrijdag en zaterdagmiddag had ik weer lekkere koffie.", "Score": 5},
    {"Text": "Zeer goede ervaring met FixPart.nl. De medewerkers hebben mij geholpen om precies het juiste onderdeel te vinden.", "Score": 5},
    {"Text": "De ontvangen schakelaar voor mijn oven is identiek aan de oude. Vervangen was eenvoudig. Mijn oven werkt weer prima!", "Score": 5},
    {"Text": "Zeer groot assortiment. Toch simpel om de juiste onderdelen te vinden op de website. Snelle en correcte levering.", "Score": 5},
    {"Text": "Heb een onderdeel van mijn koelkast besteld. Helaas de verkeerde. Retour label ontvangen maar na 2 maanden nog geen terugbetaling.", "Score": 2},
    {"Text": "Hoe simpel kan het zijn. Merk, type, hoofdgroep, duidelijke foto's, de keuze was snel gemaakt. De 2de dag al was de bestelling binnen.", "Score": 5},
    {"Text": "Koop niks bij Fixpart! Onderdeel besteld dead on arrival. Geen enkele service of garantie!", "Score": 1},
    {"Text": "Parts OK. Levering duurt 5 dagen, niet volgende dag. Geen enkel probleem maar communiceer dat duidelijker!", "Score": 3},
    {"Text": "Voor €30 heb ik mijn wasdroger weten te repareren. Dat scheelt een nieuwe wasdroger kopen. Erg tevreden!", "Score": 5},
    {"Text": "Heldere website om onderdelen te bestellen. Vond snel wat ik zocht.", "Score": 4},
    {"Text": "Bij kopen word je goed geholpen maar bij terugbetaling en retourneren zijn ze heel traag en reageren amper.", "Score": 2},
    {"Text": "Wordt snel geleverd, makkelijke site, maar verzendkosten zelf betalen ook bij een hoog bedrag is niet fijn.", "Score": 3},
    {"Text": "Heb eind oktober een deurvak besteld voor mijn koelkast. Na vijf maanden steeds hetzelfde standaard antwoord. Gecancelled.", "Score": 1},
    {"Text": "Snel geleverd, goed verpakt, kwaliteitsproduct. Mijn oude vaatwasser werkt weer als een nieuwe. Scherpe prijs.", "Score": 5},
    {"Text": "Motor van afzuigkap was defect, nieuwe gekocht bij FixPart. Als de producent het onderdeel niet heeft, hebben zij het wel.", "Score": 5},
    {"Text": "Gisteren besteld, vandaag in huis. Bij keuze van product wordt ook goedkoper alternatief benoemd, kunt zelf de keuze maken.", "Score": 5},
    {"Text": "De communicatie met FixPart verloopt zeer stroef. Bij vragen krijg je meestal een geautomatiseerd bericht.", "Score": 2},
    {"Text": "Ik heb afdichting voor een vaatwasmachine besteld. Vervolgens heb ik een lege doos ontvangen. Zeer teleurstellend.", "Score": 1},
    {"Text": "Een originele lader voor mijn Philips stofzuiger aangeschaft maar ik ontving een namaak lader die niet werkt.", "Score": 1},
    {"Text": "Op website staat precies voor welke machine het onderdeel is. Vorige keer ook een pomp besteld, paste ook perfect.", "Score": 5},
    {"Text": "Bezorging was snel ondanks het slechte weer, product was precies goed alleen jammer dat er geen schroefjes bijzaten.", "Score": 4},
    {"Text": "Hehe eindelijk een firma die zijn klanten ook op weg helpt. Als het een moeilijke reparatie betreft gewoon de video bekijken.", "Score": 5},
    {"Text": "Onderdeel dat ik niet ergens anders vond hier gekocht. Dag erna in huis. Positieve ervaring ondanks negatieve reviews.", "Score": 4},
    {"Text": "Snel gevonden via website en snel geleverd. Helaas geen handleiding voor de montage van de borstel.", "Score": 4},
    {"Text": "De pakketje was een dag te laat, maar klantenservice reageerde binnen 24 uur wat de stand van zaken was. Netjes.", "Score": 4},
    {"Text": "Al enkele malen iets besteld en steeds het juiste onderdeel omdat je specifiek kunt zoeken op het apparaat.", "Score": 5},
    {"Text": "Ik had een vervangende vlotter nodig voor mijn Whirlpool vaatwasser en kon die vinden bij FixPart. Goede kwaliteit voor een goede prijs.", "Score": 5},
]

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

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

.main .block-container { padding-top: 2rem; max-width: 1200px; }

.hero {
    background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 50%, #0f1117 100%);
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 2rem;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at 60% 40%, rgba(0,160,80,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-logo {
    flex-shrink: 0;
}
.hero-text h1 {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    color: #f4f4f5;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.hero-text .subtitle {
    font-size: 1rem;
    color: #71717a;
    margin: 0;
    font-weight: 300;
}
.hero-text .badge {
    display: inline-block;
    background: rgba(0,160,80,0.15);
    color: #34d399;
    border: 1px solid rgba(0,160,80,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.fixpart-logo-svg {
    width: 120px;
    height: auto;
}

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
.acc  { color: #34d399; }

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

.trustpilot-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(0,182,122,0.1);
    border: 1px solid rgba(0,182,122,0.3);
    border-radius: 8px;
    padding: 0.4rem 0.9rem;
    font-size: 0.8rem;
    color: #00b67a;
    font-weight: 600;
    margin-bottom: 1rem;
}

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
    "if","while","these","those","been","its","mijn","een","het","van","dat",
    "maar","ook","bij","zijn","voor","met","werd","heeft","was","had","ik",
    "ze","hij","we","ze","dit","die","der","den","ter","aan","op","er","niet"
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

LABEL_COLOR = {'Positive': '#34d399', 'Neutral': '#fbbf24', 'Negative': '#f87171'}
LABEL_CSS   = {'Positive': 'pos', 'Neutral': 'neu', 'Negative': 'neg'}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # FixPart logo in sidebar
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50" width="160">
        <rect width="200" height="50" fill="none"/>
        <text x="4" y="36" font-family="Arial Black, Arial" font-weight="900"
              font-size="28" fill="#00a050">Fix</text>
        <text x="58" y="36" font-family="Arial Black, Arial" font-weight="900"
              font-size="28" fill="#ffffff">Part</text>
        <circle cx="185" cy="25" r="10" fill="#00a050"/>
        <text x="180" y="30" font-family="Arial" font-size="14" fill="white">🔧</text>
      </svg>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("## Data Source")
    data_source = st.radio(
        "Choose data",
        ["FixPart Trustpilot Reviews", "Upload my own CSV"],
        index=0
    )

    uploaded = None
    text_col = "Text"
    score_col = "Score"

    if data_source == "Upload my own CSV":
        uploaded = st.file_uploader(
            "CSV with reviews", type=["csv"],
            help="Your file needs at least one text column."
        )
        text_col = None
        score_col = None
        if uploaded:
            preview = pd.read_csv(uploaded, nrows=5)
            uploaded.seek(0)
            cols = list(preview.columns)
            text_col = st.selectbox("Review text column", cols,
                                    index=cols.index("Text") if "Text" in cols else 0)
            score_col_sel = st.selectbox(
                "Star-rating column (optional)",
                ["— none —"] + cols,
                index=(["— none —"] + cols).index("Score") if "Score" in cols else 0
            )
            score_col = None if score_col_sel == "— none —" else score_col_sel

    st.markdown("## Filters")
    sentiment_filter = st.multiselect(
        "Show sentiments",
        ["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"]
    )

    st.markdown("---")
    st.markdown(
        "<span style='font-size:0.7rem;color:#4a4d5e;'>Powered by VADER · Streamlit<br>Reviews from Trustpilot</span>",
        unsafe_allow_html=True
    )

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <div class='hero-logo'>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 60" class="fixpart-logo-svg" width="140">
      <text x="4" y="44" font-family="Arial Black, Arial" font-weight="900"
            font-size="38" fill="#00a050">Fix</text>
      <text x="72" y="44" font-family="Arial Black, Arial" font-weight="900"
            font-size="38" fill="#ffffff">Part</text>
    </svg>
  </div>
  <div class='hero-text'>
    <div class='badge'>Trustpilot · Sentiment Analysis</div>
    <h1>Review Analyser</h1>
    <p class='subtitle'>Analyseer klantreviews van FixPart.nl — powered by VADER NLP sentiment analysis.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Live analyser (always visible) ───────────────────────────────────────────
st.markdown("<div class='section-title'>Live Analyser</div>", unsafe_allow_html=True)

custom_text = st.text_area(
    "Paste any review to analyse it instantly:",
    placeholder="e.g. Snelle levering, het juiste onderdeel, uitstekende service!",
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
            <span>😊 Positive: <b style='color:#f4f4f5'>{analyzer.polarity_scores(custom_text)["pos"]:.2f}</b></span>
            <span>😐 Neutral: <b style='color:#f4f4f5'>{analyzer.polarity_scores(custom_text)["neu"]:.2f}</b></span>
            <span>😞 Negative: <b style='color:#f4f4f5'>{analyzer.polarity_scores(custom_text)["neg"]:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
show_analysis = False
df = None

if data_source == "FixPart Trustpilot Reviews":
    st.markdown("""
    <div class='trustpilot-badge'>
        ★ Trustpilot · fixpart.nl &nbsp;|&nbsp; 30 reviews geladen
    </div>
    """, unsafe_allow_html=True)
    df_raw = pd.DataFrame(FIXPART_REVIEWS)
    with st.spinner("Running VADER sentiment analysis…"):
        df = run_vader(df_raw, "Text")
    text_col = "Text"
    score_col = "Score"
    show_analysis = True

elif data_source == "Upload my own CSV" and uploaded and text_col:
    with st.spinner("Running VADER on your dataset…"):
        df_raw = pd.read_csv(uploaded)
        df = run_vader(df_raw, text_col)
    show_analysis = True

# ── Dataset section ───────────────────────────────────────────────────────────
if show_analysis and df is not None:
    df_view = df[df['sentiment_label'].isin(sentiment_filter)].copy()

    st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)

    total   = len(df)
    n_pos   = (df['sentiment_label'] == 'Positive').sum()
    n_neu   = (df['sentiment_label'] == 'Neutral').sum()
    n_neg   = (df['sentiment_label'] == 'Negative').sum()
    mean_sc = df['compound_score'].mean()

    acc_html = ""
    if score_col and score_col in df.columns:
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
    c1.markdown(f"<div class='metric-card'><div class='lbl'>Total Reviews</div><div class='val' style='color:#f4f4f5'>{total:,}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='lbl'>Positive</div><div class='val pos'>{n_pos:,}</div><div class='lbl'>{n_pos/total:.1%}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='lbl'>Neutral</div><div class='val neu'>{n_neu:,}</div><div class='lbl'>{n_neu/total:.1%}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div class='lbl'>Negative</div><div class='val neg'>{n_neg:,}</div><div class='lbl'>{n_neg/total:.1%}</div></div>", unsafe_allow_html=True)
    if acc_html:
        c5.markdown(acc_html, unsafe_allow_html=True)
    else:
        c5.markdown(f"<div class='metric-card'><div class='lbl'>Avg Score</div><div class='val' style='color:#34d399'>{mean_sc:+.3f}</div></div>", unsafe_allow_html=True)

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
            nbinsx=40,
            marker_color='#00a050',
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
    if score_col and score_col in df.columns and 'score_label' in df.columns:
        st.markdown("<div class='section-title'>Accuracy vs Star Ratings</div>", unsafe_allow_html=True)

        try:
            from sklearn.metrics import confusion_matrix
            labels_cm = ['Positive','Neutral','Negative']
            valid2 = df[df['score_label'].notna()]
            cm = confusion_matrix(valid2['score_label'], valid2['sentiment_label'], labels=labels_cm)

            hm = go.Figure(go.Heatmap(
                z=cm, x=labels_cm, y=labels_cm,
                colorscale=[[0,'#16181f'],[0.5,'#00502a'],[1,'#00a050']],
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
        except ImportError:
            st.info("Install scikit-learn to see the confusion matrix.")

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
    if score_col and score_col in df.columns:
        export_cols += [score_col]
    if 'score_label' in df.columns:
        export_cols += ['score_label']

    csv_buf = io.StringIO()
    df[export_cols].to_csv(csv_buf, index=False)
    st.download_button(
        "⬇ Download scored reviews (CSV)",
        data=csv_buf.getvalue(),
        file_name="fixpart_sentiment_results.csv",
        mime="text/csv",
    )

else:
    if data_source == "Upload my own CSV":
        st.markdown("<div class='section-title'>Getting Started</div>", unsafe_allow_html=True)
        st.info(
            "Upload a CSV in the sidebar to analyse your dataset.  \n"
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
        """)
