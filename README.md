# Review Sentiment Dashboard

This repository contains a Streamlit dashboard for analysing customer reviews with VADER sentiment analysis. The app can analyse the built-in FixPart Trustpilot review sample, or users can upload their own CSV file with review text.

## Live dashboard

https://exl2k5rex9gtsaqsqsq8jf.streamlit.app/

## Project overview

The dashboard automatically classifies reviews as:

- Positive
- Neutral
- Negative

It also shows visual insights such as KPI cards, sentiment distribution, compound score distribution, top words per sentiment category, sample reviews, and a confusion matrix when star ratings are available.

## Repository structure

```text
T-08/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python packages needed to run the app
└── README.md           # Project explanation and setup instructions
```

## Requirements

The app uses the following main Python libraries:

```text
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
vaderSentiment>=3.3.2
scikit-learn>=1.3.0
```

These packages are listed in `requirements.txt` and will be installed automatically by Streamlit Community Cloud during deployment.

## How to run the app locally

### 1. Clone the repository

```bash
git clone https://github.com/SydStohr/T-08.git
cd T-08
```

### 2. Install the required packages

```bash
pip install -r requirements.txt
```

### 3. Start the Streamlit app

```bash
streamlit run app.py
```

After running this command, Streamlit will open the app in your browser.

## How to deploy with Streamlit Community Cloud

1. Place `app.py`, `requirements.txt`, and `README.md` in the GitHub repository.
2. Go to Streamlit Community Cloud.
3. Click **Create app** or **Deploy an app**.
4. Connect the GitHub repository.
5. Select:
   - Repository: `SydStohr/T-08`
   - Branch: `main`
   - Main file path: `app.py`
6. Click **Deploy**.

Streamlit Community Cloud reads the `requirements.txt` file automatically, installs the dependencies, and runs the application from `app.py`.

## CSV upload format

The app can also analyse a custom CSV file. The file must include at least one column containing review text. A star-rating column is optional.

Example:

| Text | Score |
|---|---|
| This product is amazing! | 5 |
| Terrible quality, very disappointed. | 1 |
| It is okay, nothing special. | 3 |

When uploading a CSV file, the user can select the review text column in the sidebar. If a score column is included, the app can compare the VADER sentiment prediction with the star rating.

## Main app features

- Built-in FixPart Trustpilot review dataset
- Custom CSV upload
- Live review analyser
- VADER sentiment classification
- Sentiment filter in the sidebar
- KPI cards for positive, neutral, and negative reviews
- Sentiment split chart
- Compound score distribution
- Top words by sentiment
- Confusion matrix against star ratings
- Export button for scored reviews

## Notes

VADER is a rule-based sentiment model. It is fast, transparent, and useful for a first version of a review analysis dashboard. However, it may be less accurate for sarcasm, mixed sentiment, non-English reviews, and very short or unclear review texts.
