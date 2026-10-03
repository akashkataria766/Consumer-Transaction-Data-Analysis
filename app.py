"""Streamlit entry point for consumer transaction analysis."""

from io import BytesIO
from datetime import date
from pathlib import Path
import random
import time

import pandas as pd
import plotly.express as px
import streamlit as st

import config
from analysis import build_summaries, detect_outliers
from data_cleaning import clean_transactions
from export_to_excel import prepare_analysis_tables


REQUIRED_COLUMNS = {
    "txn_id",
    "customer_id",
    "category",
    "amount",
    "status",
    "order_date",
}
NAVY = config.DASHBOARD_NAVY
CURRENCY_SYMBOLS = {
    "USD": "$",
    "INR": "₹",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "A$",
    "SGD": "S$",
    "AED": "AED",
    "SAR": "SAR",
    "CNY": "¥",
}
CURRENCY_OPTIONS = list(CURRENCY_SYMBOLS)
FACTS = [
    'The term "Data Scientist" was coined in 2008 by DJ Patil and Jeff Hammerbacher.',
    'Netflix saves $1 billion per year using data analytics to reduce customer churn.',
    "90% of the world's data was generated in the last two years alone.",
    'The global data analytics market is expected to reach $650 billion by 2029.',
    'Amazon uses over 60 machine learning models to predict what you will buy next.',
    'A single Boeing 737 generates 240 terabytes of data per flight.',
    'SQL was invented at IBM in 1974 and is still the most used data language today.',
    'Google processes over 8.5 billion search queries every single day.',
    'Excel was first released in 1985 and still powers 750 million users worldwide.',
    'The average data analyst saves their company 20 hours per week through automation.',
    "Data cleaning takes up 60–80% of a data analyst's total working time.",
    'Walmart collects 2.5 petabytes of customer transaction data every hour.',
    'The first computer bug was an actual moth found in a Harvard computer in 1947.',
    'Python became the most popular programming language in the world in 2022.',
    'Pandas library was created by Wes McKinney in 2008 while working at a hedge fund.',
    'The word "algorithm" comes from the name of Persian mathematician Al-Khwarizmi.',
    'LinkedIn uses data analytics to rank your profile in recruiter search results.',
    'Spotify analyzes 30 billion data points daily to power its recommendation engine.',
    'The first spreadsheet software, VisiCalc, launched in 1979 and changed business forever.',
    'Over 328 million terabytes of new data are created every single day globally.',
    'A data analyst at an entry level can process insights that once required a full team.',
    'Oracle was founded in 1977 and named after a CIA project its founders worked on.',
    'The 99th percentile threshold is a standard statistical method for outlier detection.',
    'Z-score measures how many standard deviations a value is from the mean.',
    'Pivot Tables were introduced in Excel in 1994 and revolutionized business reporting.',
    'The term "Big Data" was first used in a research paper by NASA scientists in 1997.',
    'Deloitte employs over 15,000 analytics professionals across its global practices.',
    'Amazon Web Services stores data for over 1 million businesses worldwide.',
    'India produces the second-largest number of data professionals in the world.',
    'A single tweet generates approximately 0.5 kilobytes of structured data.',
    'The human brain processes visual information 60,000 times faster than text.',
    'Good data visualization can reduce decision-making time by up to 70%.',
    'Matplotlib was first released in 2003 and is still the foundation of Python charting.',
    'NumPy arrays are up to 50 times faster than Python lists for numerical operations.',
    'The first ATM was installed in London in 1967 and generated the first banking transaction data.',
    'McKinsey estimates that data-driven organizations are 23 times more likely to acquire customers.',
    'EXL Service manages analytics operations for over 50 Fortune 500 companies.',
    'Data validation is the first line of defence against incorrect business decisions.',
    'Referential integrity ensures every foreign key in a database points to a valid record.',
    'The median is preferred over mean for imputing missing values in skewed distributions.',
    'Duplicate records in a database can inflate revenue figures by up to 15%.',
    'A well-designed dashboard can communicate the same insight 5 times faster than a report.',
    'The word "statistics" comes from the Latin word for "state" — it was invented to govern nations.',
    'Florence Nightingale invented the pie chart in 1858 to visualize hospital death rates.',
    'Over 70% of business intelligence projects fail due to poor data quality at the source.',
    'SQL joins were inspired by mathematical set theory operations developed in the 1960s.',
    'VLOOKUP is the most searched Excel formula on the internet every single year.',
    'The first data warehouse was built by Walmart in the 1980s to track store inventory.',
    "Python's Pandas library name comes from 'Panel Data' — a term used in econometrics.",
    'Every second, 1.7 megabytes of new data is created for every person on Earth.',
]


st.set_page_config(
    page_title="Consumer Transaction Analysis",
    layout="wide",
)

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
        .stApp {{ background: linear-gradient(135deg, #f4f7fb 0%, #ffffff 48%, #edf3f9 100%); color: #172235; }}
        [data-testid="stAppViewContainer"] {{ background: transparent; }}
        h1, h2, h3 {{ color: {NAVY}; font-family: 'Playfair Display', Georgia, serif; }}
        p, label, button, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ font-family: 'DM Sans', Arial, sans-serif; }}
        [data-testid="stSidebar"] {{ background: {NAVY}; }}
        [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
        [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.18); }}
        [data-testid="stFileUploader"] {{ background-color: #f8f9ff; border: 2px dashed {NAVY}; border-radius: 12px; padding: 20px; }}
        [data-testid="stFileUploader"] * {{ color: {NAVY} !important; }}
        [data-testid="stFileUploaderDropzone"] {{ background: #f8f9ff !important; border: 0 !important; }}
        [data-testid="stFileUploaderDropzone"] * {{ color: {NAVY} !important; background-color: transparent !important; }}
        [data-testid="stFileUploaderDropzone"] button {{ color: #fff !important; background: {NAVY} !important; border: 0 !important; }}
        .sidebar-nav-item {{ display: block; margin: .5rem 0; padding: 10px 16px; border-left: 5px solid {NAVY}; border-radius: 8px; color: {NAVY} !important; background: #fff; font: 600 .9rem 'DM Sans', Arial, sans-serif; text-decoration: none; cursor: pointer; transition: background .2s ease, transform .2s ease; }}
        .sidebar-nav-item:hover {{ color: {NAVY} !important; background: #e8f0fe; transform: translateX(3px); }}
        .sidebar-stats {{ margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,.18); }}
        .sidebar-stat {{ display: flex; justify-content: space-between; gap: 10px; padding: .55rem 0; color: #dbe8f8; font: .75rem 'DM Sans', Arial, sans-serif; }}
        .sidebar-stat strong {{ color: #fff; font-size: .82rem; text-align: right; }}
        [data-testid="stMetric"] {{ min-height: 132px; padding: 1.25rem; border: 1px solid rgba(68,114,196,.18); border-left: 5px solid {NAVY}; border-radius: 12px; background: linear-gradient(135deg, #ffffff, #eaf1fb); box-shadow: 0 12px 28px rgba(31,56,100,.12); transition: transform .2s ease, box-shadow .2s ease; }}
        [data-testid="stMetric"]:hover {{ transform: translateY(-4px); box-shadow: 0 18px 34px rgba(31,56,100,.2); }}
        [data-testid="stMetricLabel"] {{ color: #697589; }}
        [data-testid="stMetricValue"] {{ color: {NAVY}; }}
        [data-testid="stDataFrame"] {{ border: 1px solid #dbe3ec; border-radius: 10px; box-shadow: 0 8px 22px rgba(31,56,100,.07); }}
        div[data-testid="stExpander"] {{ border: 1px solid #dbe3ec; border-radius: 10px; background: #fff; }}
        div[data-testid="stHeading"] {{ margin-top: 1.3rem; padding: .65rem 1rem; border-left: 5px solid {NAVY}; background: rgba(31,56,100,.06); animation: section-in .55s ease both; }}
        div[data-testid="stProgress"] > div {{ background: #dbe3ec; }}
        div[data-testid="stProgress"] > div > div {{ background: linear-gradient(90deg, {NAVY}, #4472c4); }}
        .health-card {{ margin: 1rem 0 1.2rem; padding: 1rem 1.25rem; border-left: 5px solid var(--health-color); border-radius: 10px; background: #fff; box-shadow: 0 8px 20px rgba(31,56,100,.08); }}
        .health-card strong {{ color: var(--health-color); font: 700 1.15rem 'DM Sans', Arial, sans-serif; }}
        .health-card span {{ display: block; margin-top: .25rem; color: #697589; font: .8rem 'DM Sans', Arial, sans-serif; }}
        div[data-testid="stDownloadButton"] button {{ border: 0; border-radius: 7px; color: #fff; background: {NAVY}; font-weight: 700; box-shadow: 0 8px 16px rgba(31,56,100,.2); transition: transform .2s ease, background .2s ease; }}
        div[data-testid="stDownloadButton"] button:hover {{ color: #fff; background: #4472c4; transform: translateY(-2px); }}
        .top-banner {{ margin: 0 0 1.5rem; padding: 2rem 2.2rem; border-radius: 14px; color: white; background: linear-gradient(115deg, {NAVY}, #4472c4); box-shadow: 0 16px 30px rgba(31,56,100,.2); }}
        .top-banner h1 {{ margin: 0; color: white; font: 700 2.4rem/1.1 'Playfair Display', Georgia, serif; }}
        .top-banner p {{ margin: .55rem 0 0; color: #dce8f8; font: 1rem/1.5 'DM Sans', Arial, sans-serif; }}
        .file-badge {{ display: inline-block; margin: .5rem 0 1rem; padding: .42rem .8rem; border-radius: 999px; color: #0c5c3c; background: #d9f4e7; font: 600 .82rem 'DM Sans', Arial, sans-serif; }}
        .currency-badge {{ display: inline-block; margin: -.35rem 0 1rem; padding: .35rem .7rem; border-radius: 999px; color: #0c5c3c; background: #d9f4e7; font: 600 .78rem 'DM Sans', Arial, sans-serif; }}
        .currency-badge.manual {{ color: #1f3864; background: #e8f0fe; }}
        .currency-warning {{ margin: -.35rem 0 1rem; padding: .55rem .8rem; border-radius: 7px; color: #7a4b00; background: #fff3cd; font: .78rem 'DM Sans', Arial, sans-serif; }}
        .loading-overlay {{ position: fixed; inset: 0; z-index: 999999; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; text-align: center; color: #fff; background: {NAVY}; animation: overlay-in .25s ease both; }}
        .loading-spinner {{ width: 58px; height: 58px; margin-bottom: 2rem; border: 4px solid rgba(255,255,255,.22); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }}
        .loading-fact {{ max-width: 720px; padding: 0 1rem; color: #fff; font: 600 clamp(20px, 3vw, 2.35rem)/1.25 'Playfair Display', Georgia, serif; }}
        .loading-label {{ margin-top: 1.2rem; color: #b9cce5; font: .78rem 'DM Sans', Arial, sans-serif; letter-spacing: .12em; text-transform: uppercase; }}
        .footer-note {{ margin-top: 3rem; padding: 1rem 0; color: #697589; border-top: 1px solid #dbe3ec; font: .78rem 'DM Sans', Arial, sans-serif; text-align: center; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        @keyframes overlay-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes section-in {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @media (max-width: 700px) {{ .top-banner h1 {{ font-size: 1.8rem; }} [data-testid="stMetric"] {{ min-height: 112px; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)


def format_currency(value: float, symbol: str) -> str:
    """Format a numeric value with the selected currency symbol."""
    return f"{symbol}{value:,.2f}"


def excel_bytes(data: pd.DataFrame, symbol: str) -> bytes:
    """Create the three-sheet Excel report in memory for download."""
    summary, category, monthly = prepare_analysis_tables(data)
    monetary_metrics = {"Total revenue", "Average order", "Maximum order", "Minimum order"}
    summary["value"] = summary.apply(
        lambda row: format_currency(row["value"], symbol)
        if row["metric"] in monetary_metrics
        else row["value"],
        axis=1,
    )
    category["total_revenue"] = category["total_revenue"].map(lambda value: format_currency(value, symbol))
    category["average_order"] = category["average_order"].map(lambda value: format_currency(value, symbol))
    monthly["total_revenue"] = monthly["total_revenue"].map(lambda value: format_currency(value, symbol))
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        category.to_excel(writer, sheet_name="Category", index=False)
        monthly.to_excel(writer, sheet_name="Monthly", index=False)
    return output.getvalue()


def detect_currency(data: pd.DataFrame) -> tuple[str, str, list[str]]:
    """Detect the most common uploaded currency or request a manual selection."""
    currency_column = next(
        (column for column in ("currency", "currency_code") if column in data.columns),
        None,
    )
    if currency_column is None:
        selected_currency = st.selectbox("Select currency", CURRENCY_OPTIONS, key="manual_currency")
        return selected_currency, CURRENCY_SYMBOLS[selected_currency], []

    values = data[currency_column].dropna().astype(str).str.strip().str.upper()
    unique_values = sorted(value for value in values.unique() if value)
    detected_currency = values.mode().iloc[0] if not values.mode().empty else "USD"
    if detected_currency not in CURRENCY_SYMBOLS:
        detected_currency = "USD"
    return detected_currency, CURRENCY_SYMBOLS[detected_currency], unique_values


def make_anomaly_table(data: pd.DataFrame) -> tuple[float, pd.DataFrame]:
    """Return high-value orders with the result of both detection methods."""
    percentile_cutoff, percentile_outliers, z_threshold, z_score_outliers = detect_outliers(data)
    standard_deviation = data["amount"].std()
    if pd.isna(standard_deviation) or standard_deviation == 0:
        z_scores = pd.Series(0.0, index=data.index)
    else:
        z_scores = (data["amount"] - data["amount"].mean()) / standard_deviation

    anomalies = data.copy()
    anomalies["percentile_flag"] = anomalies["amount"] > percentile_cutoff
    anomalies["z_score"] = z_scores
    anomalies["z_score_flag"] = anomalies["z_score"].abs() > z_threshold
    anomalies = anomalies[anomalies["percentile_flag"] | anomalies["z_score_flag"]]
    columns = [
        "txn_id",
        "customer_id",
        "category",
        "amount",
        "status",
        "order_date",
        "z_score",
        "percentile_flag",
        "z_score_flag",
    ]
    return percentile_cutoff, anomalies[columns].sort_values("amount", ascending=False)


def show_loading_overlay() -> tuple[object, float]:
    """Render the visual loading state and select an unused session fact."""
    seen_facts = st.session_state.setdefault("seen_facts", set())
    available_facts = [fact for fact in FACTS if fact not in seen_facts]
    fact = random.choice(available_facts or FACTS)
    seen_facts.add(fact)
    placeholder = st.empty()
    placeholder.markdown(
        f'<div class="loading-overlay"><div class="loading-spinner"></div><div class="loading-fact">{fact}</div><div class="loading-label">Did you know? — Loading your analysis...</div></div>',
        unsafe_allow_html=True,
    )
    return placeholder, time.perf_counter()


def finish_loading(placeholder: object, started_at: float) -> None:
    """Keep the fact visible briefly, then remove the overlay."""
    time.sleep(max(0, 1.5 - (time.perf_counter() - started_at)))
    placeholder.empty()


with st.sidebar:
    st.markdown("## CT · Analytics")
    st.caption("Consumer transaction intelligence")
    st.divider()
    st.markdown('<a class="sidebar-nav-item" href="#kpi-section">▦ &nbsp; Dashboard</a>', unsafe_allow_html=True)
    showcase_path = Path(__file__).with_name("sample_transactions.csv")
    if showcase_path.exists():
        st.markdown(
            '<a class="sidebar-nav-item" href="sample_transactions.csv">▤ &nbsp; Showcase file · INR</a>',
            unsafe_allow_html=True,
        )
    st.divider()
    sidebar_stats = st.empty()
    st.caption("Built with Streamlit, Pandas, Plotly and openpyxl")

st.markdown('<div class="top-banner"><h1>Consumer Transaction Analysis</h1><p>Turn a raw transaction file into a clear, decision-ready readout in seconds.</p></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV with txn_id, customer_id, category, amount, status, and order_date to begin.")
    st.stop()

st.markdown(f'<span class="file-badge">✓ {uploaded_file.name} ready for analysis</span>', unsafe_allow_html=True)

try:
    raw_data = pd.read_csv(uploaded_file)
except (pd.errors.ParserError, UnicodeDecodeError, OSError) as error:
    st.error(f"Could not read the uploaded CSV: {error}")
    st.stop()

missing_columns = sorted(REQUIRED_COLUMNS - set(raw_data.columns))
if missing_columns:
    st.error("Missing required columns: " + ", ".join(missing_columns))
    st.stop()

currency_code, currency_symbol, currencies_found = detect_currency(raw_data)
if currencies_found:
    if len(currencies_found) > 1:
        st.markdown(
            f'<div class="currency-warning">⚠️ Multiple currencies found. Showing most common: {currency_code}<br><small>{", ".join(currencies_found)}</small></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<span class="currency-badge">🪙 Currency detected: {currency_code} ({currency_symbol})</span>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<span class="currency-badge manual">🪙 Currency: {currency_code} ({currency_symbol}) (selected)</span>',
        unsafe_allow_html=True,
    )

loading_placeholder, loading_started = show_loading_overlay()

with st.expander("Raw data sample"):
    st.dataframe(raw_data.head(10), use_container_width=True)

try:
    cleaned_data = clean_transactions(raw_data.copy())
except (KeyError, TypeError, ValueError) as error:
    finish_loading(loading_placeholder, loading_started)
    st.error(f"Could not clean the uploaded CSV: {error}")
    st.stop()

if cleaned_data.empty:
    finish_loading(loading_placeholder, loading_started)
    st.error("No valid transactions remain after cleaning. Check amounts, dates, and statuses.")
    st.stop()

with st.expander("Cleaned data sample"):
    st.dataframe(cleaned_data.head(10), use_container_width=True)

category_summary, monthly_summary, status_summary, customer_summary = build_summaries(cleaned_data.assign(
    month=cleaned_data["order_date"].dt.to_period("M").astype(str)
))
health_score = len(cleaned_data) / len(raw_data) * 100
health_color = "#16805c" if health_score >= 90 else "#a26b00" if health_score >= 70 else "#b53c32"
date_range = f"{cleaned_data['order_date'].min():%b %Y} – {cleaned_data['order_date'].max():%b %Y}"
sidebar_stats.markdown(
    f'<div class="sidebar-stats"><div class="sidebar-stat"><span>Total records</span><strong>{len(cleaned_data):,}</strong></div><div class="sidebar-stat"><span>Date range</span><strong>{date_range}</strong></div><div class="sidebar-stat"><span>Categories found</span><strong>{cleaned_data["category"].nunique():,}</strong></div></div>',
    unsafe_allow_html=True,
)

completed_count = int((cleaned_data["status"] == "COMPLETED").sum())
completion_rate = completed_count / len(cleaned_data) * 100
finish_loading(loading_placeholder, loading_started)

st.markdown('<div id="kpi-section"></div>', unsafe_allow_html=True)
st.subheader("Key Performance Indicators")
st.markdown(
    f'<div class="health-card" style="--health-color: {health_color};"><strong>Data Health Score: {health_score:.0f}%</strong><span>{len(cleaned_data):,}/{len(raw_data):,} records valid after cleaning</span></div>',
    unsafe_allow_html=True,
)
kpi_columns = st.columns(4)
kpi_columns[0].metric("Total Transactions", f"{len(cleaned_data):,}")
kpi_columns[1].metric("Total Revenue", format_currency(cleaned_data["amount"].sum(), currency_symbol))
kpi_columns[2].metric("Avg Order Value", format_currency(cleaned_data["amount"].mean(), currency_symbol))
kpi_columns[3].metric("Completion Rate", f"{completion_rate:.1f}%")
st.divider()

st.subheader("Revenue by Category")
category_chart, category_table = st.columns(2)
with category_chart:
    figure = px.bar(
        category_summary.reset_index(),
        x="category",
        y="total_revenue",
        color_discrete_sequence=[NAVY],
        labels={"category": "Category", "total_revenue": "Revenue"},
    )
    figure.update_layout(showlegend=False, margin=dict(t=20, b=20), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
    figure.update_yaxes(tickprefix=currency_symbol)
    st.plotly_chart(figure, use_container_width=True)
with category_table:
    st.dataframe(category_summary.style.format({"total_revenue": lambda value: format_currency(value, currency_symbol), "average_order": lambda value: format_currency(value, currency_symbol)}), use_container_width=True)
st.divider()

st.subheader("Monthly Trend")
monthly_chart_data = monthly_summary.reset_index()
monthly_chart_data["month"] = pd.to_datetime(monthly_chart_data["month"])
monthly_chart = px.line(
    monthly_chart_data,
    x="month",
    y=["total_revenue", "total_orders"],
    markers=True,
    color_discrete_sequence=[NAVY, "#70AD47"],
    labels={"value": "Value", "variable": "Measure", "month": "Month"},
)
monthly_chart.update_layout(hovermode="x unified", margin=dict(t=20, b=20), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
st.plotly_chart(monthly_chart, use_container_width=True)
st.divider()

st.subheader("Order Status Breakdown")
status_chart, status_table = st.columns(2)
with status_chart:
    status_figure = px.pie(
        status_summary.reset_index(),
        names="status",
        values="orders",
        color_discrete_sequence=config.DASHBOARD_PALETTE,
    )
    status_figure.update_layout(margin=dict(t=20, b=20), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
    st.plotly_chart(status_figure, use_container_width=True)
with status_table:
    st.dataframe(status_summary.style.format({"percentage": "{:.1f}%"}), use_container_width=True)
st.divider()

st.subheader("Top 5 Customers")
st.dataframe(
    customer_summary.style.format({"total_spend": lambda value: format_currency(value, currency_symbol)}),
    use_container_width=True,
)
st.divider()

st.subheader("Anomaly Detection")
percentile_cutoff, anomaly_table = make_anomaly_table(cleaned_data)
st.caption(f"Flagged orders exceed the 99th percentile threshold of {format_currency(percentile_cutoff, currency_symbol)} or have an absolute Z-score above {config.Z_SCORE_THRESHOLD:.1f}.")
if anomaly_table.empty:
    st.success("No high-value orders were flagged.")
else:
    st.dataframe(
        anomaly_table.style.format({"amount": lambda value: format_currency(value, currency_symbol), "z_score": "{:.2f}"}),
        use_container_width=True,
    )
st.divider()

st.markdown('<div id="upload-section"></div>', unsafe_allow_html=True)
st.subheader("Downloads")
download_data = cleaned_data.copy()
download_data["amount"] = download_data["amount"].map(lambda value: format_currency(value, currency_symbol))
if "currency" not in download_data.columns and "currency_code" not in download_data.columns:
    download_data["currency"] = currency_code
cleaned_csv = download_data.to_csv(index=False, date_format="%Y-%m-%d").encode("utf-8")
download_columns = st.columns(2)
download_columns[0].download_button(
    "↓  Download cleaned CSV",
    data=cleaned_csv,
    file_name="transactions_clean.csv",
    mime="text/csv",
)
download_columns[1].download_button(
    "↓  Download Excel report",
    data=excel_bytes(cleaned_data, currency_symbol),
    file_name="transaction_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown(f'<div class="footer-note">Consumer Transaction Data Analysis · Streamlit · Pandas · Plotly · openpyxl · {date.today().strftime("%B %d, %Y")}</div>', unsafe_allow_html=True)
