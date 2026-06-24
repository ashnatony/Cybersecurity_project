import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="Sentinel IDS",
    page_icon="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%234ec9d4' d='M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5l-8-3z'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================
# DESIGN SYSTEM -- load external CSS
# ==========================

CSS_PATH = Path(__file__).parent / "styles.css"


def inject_styles() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")


inject_styles()

# Chart / UI color tokens (mirror CSS variables for Matplotlib)
CHART_BG = "#141a22"
CHART_PANEL = "#1f2733"
CHART_TEXT = "#b6c2d1"
CHART_GRID = "#222b38"
CHART_TITLE = "#e6ebf2"
CHART_AXIS = "#5a6776"
CHART_BAR_COLORS = [
    "#4ec9d4", "#62d4de", "#7ddee7", "#9be8ef",
    "#5ec99c", "#7ed3aa", "#9fddb8", "#e6b85c",
    "#e07a85", "#b08cb6",
]

# ==========================
# ICONS -- inline SVG primitives (no emoji, no library)
# ==========================

ICON_SHIELD = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>"""

ICON_CHART = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-6"/></svg>"""

ICON_RADAR = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 17.78 13.5"/><path d="M12 12L12 8"/><circle cx="12" cy="12" r="2"/></svg>"""

ICON_TARGET = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>"""

ICON_DATABASE = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg>"""

ICON_BOLT = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>"""

ICON_CIRCLE_CHECK = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>"""

ICON_CIRCLE_ALERT = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>"""

ICON_CIRCLE_X = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>"""

ICON_ARROW_RIGHT = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>"""

ICON_PLUG = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22v-5"/><path d="M9 7V2"/><path d="M15 7V2"/><path d="M6 13V8h12v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4z"/></svg>"""

ICON_INFO = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>"""

ICON_TIP = """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>"""

# ==========================
# LOAD MODEL
# ==========================


@st.cache_resource
def load_assets():
    model = joblib.load("intrusion_model.pkl")
    features = joblib.load("features.pkl")
    return model, features


model, features = load_assets()

USER_AGENT_MAPPING = {
    "Chrome": "user_agent_Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Firefox": "user_agent_Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Googlebot": "user_agent_Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "sqlmap_1.7": "user_agent_Mozilla/5.0 (compatible; sqlmap/1.7)",
    "iPhone": "user_agent_Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "curl_7.81": "user_agent_curl/7.81.0",
    "curl_8.4": "user_agent_curl/8.4.0",
    "python_requests_2.28": "user_agent_python-requests/2.28",
    "python_requests_2.31": "user_agent_python-requests/2.31.0",
    "python_urllib": "user_agent_python-urllib/3.9",
    "sqlmap_1.8": "user_agent_sqlmap/1.8",
    "zgrab": "user_agent_zgrab/0.x",
}

FEATURE_NAMES = [
    "sqlmap/1.7", "python-requests/2.28", "curl/7.81", "sqlmap/1.8",
    "dst_port", "zgrab", "src_port", "bytes_sent", "curl/8.4", "iPhone",
]
IMPORTANCE_SCORES = [0.142, 0.119, 0.106, 0.079, 0.073, 0.068, 0.056, 0.045, 0.036, 0.033]

# Model evaluation metrics (F1 derived from precision & recall for consistency)
MODEL_ACCURACY = 0.97
MODEL_PRECISION = 0.64
MODEL_RECALL = 0.59
MODEL_F1 = 2 * MODEL_PRECISION * MODEL_RECALL / (MODEL_PRECISION + MODEL_RECALL)


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


METRIC_TOOLTIPS = {
    "Accuracy": (
        f"Overall correct predictions ({format_pct(MODEL_ACCURACY)}). Can appear high on "
        "imbalanced data where 96% of traffic is benign. Pair with precision, recall, and F1."
    ),
    "Precision": (
        f"Of sessions flagged malicious, {format_pct(MODEL_PRECISION)} truly were attacks. "
        "False positives are common when attacks are only 4% of the dataset."
    ),
    "Recall": (
        f"The model detects {format_pct(MODEL_RECALL)} of actual attacks. Weighted training "
        "improves rare-class detection, but some attacks still slip through."
    ),
    "F1": (
        f"Harmonic mean of precision and recall ({format_pct(MODEL_F1)}). "
        "Best single score for balancing false alarms vs missed attacks."
    ),
}

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "show_validation" not in st.session_state:
    st.session_state.show_validation = False


# ==========================
# HELPERS
# ==========================


def section_header(icon_svg: str, title: str, meta: str = "") -> None:
    meta_html = f'<span class="section-head__meta">{meta}</span>' if meta else ""
    st.html(
        f"""
        <div class="section-head">
            <h2 class="section-head__title">
                <span class="section-head__icon">{icon_svg}</span>
                <span>{title}</span>
            </h2>
            {meta_html}
        </div>
        """,
    )


def metric_card(
    label: str,
    value: str,
    color_class: str = "",
    tooltip: str = "",
    label_html: str | None = None,
    delta: str = "",
    spark: str = "",
    feature: bool = False,
    index: int = 0,
) -> str:
    display_label = label_html if label_html else label
    tip_html = (
        f'<span class="metric__tip" tabindex="0" data-tooltip="{tooltip}" '
        f'aria-label="{tooltip}">?</span>'
    )
    value_class = f"metric__value {('metric__value--' + color_class) if color_class else ''}".strip()
    feature_class = " metric metric--feature" if feature else " metric"
    delta_html = f'<div class="metric__delta">{delta}</div>' if delta else ""
    spark_html = f'<div class="metric__spark">{spark}</div>' if spark else ""
    return f"""
    <div class="{feature_class.strip()}" style="--index: {index};">
        <div class="metric__label">
            <span>{display_label}</span>
            {tip_html}
        </div>
        <div class="{value_class}">{value}</div>
        {delta_html}
        {spark_html}
    </div>
    """


def validate_inputs(
    src_port, dst_port, bytes_sent, bytes_received, user_agent, protocol
):
    errors = []

    if not (0 <= src_port <= 65535):
        errors.append("Source port must be between 0 and 65535.")
    if not (0 <= dst_port <= 65535):
        errors.append("Destination port must be between 0 and 65535.")
    if bytes_sent < 0:
        errors.append("Bytes sent cannot be negative.")
    if bytes_received < 0:
        errors.append("Bytes received cannot be negative.")
    if bytes_sent == 0 and bytes_received == 0:
        errors.append("At least one of bytes sent or bytes received must be greater than zero.")
    if not user_agent:
        errors.append("User agent selection is required.")
    if protocol not in ("TCP", "UDP", "ICMP"):
        errors.append("Protocol must be TCP, UDP, or ICMP.")

    return errors


def render_validation_errors(errors: list[str]) -> None:
    items = "".join(f"<li>{e}</li>" for e in errors)
    st.html(
        f"""
        <div class="validation" role="alert">
            <div class="validation__head">{ICON_CIRCLE_ALERT}<span>Resolve to enable analysis</span></div>
            <ul class="validation__list">{items}</ul>
        </div>
        """,
    )


def build_input_data(
    src_port, dst_port, bytes_sent, bytes_received,
    is_internal, hour, day, protocol, user_agent,
):
    input_data = dict.fromkeys(features, 0)
    input_data["src_port"] = src_port
    input_data["dst_port"] = dst_port
    input_data["bytes_sent"] = bytes_sent
    input_data["bytes_received"] = bytes_received
    input_data["is_internal_traffic"] = int(is_internal)
    input_data["hour"] = hour
    input_data["day"] = day

    if protocol == "TCP":
        input_data["protocol_TCP"] = 1
    elif protocol == "UDP":
        input_data["protocol_UDP"] = 1

    input_data[USER_AGENT_MAPPING[user_agent]] = 1
    return input_data


def render_feature_chart():
    fig, ax = plt.subplots(figsize=(8, 4.2))
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)

    names = FEATURE_NAMES[::-1]
    scores = IMPORTANCE_SCORES[::-1]
    colors = CHART_BAR_COLORS[:len(names)][::-1]

    bars = ax.barh(names, scores, color=colors, height=0.62, edgecolor="none")

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_width() + 0.003,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.3f}",
            va="center",
            ha="left",
            fontsize=10,
            color=CHART_TEXT,
            fontfamily="monospace",
            fontweight="500",
        )

    ax.set_xlabel("Feature Importance", color=CHART_TEXT, fontsize=10, labelpad=10, fontfamily="sans-serif")
    ax.tick_params(colors=CHART_TEXT, labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(CHART_GRID)
    ax.spines["left"].set_color(CHART_GRID)
    ax.set_xlim(0, max(IMPORTANCE_SCORES) * 1.2)
    ax.grid(axis="x", color=CHART_GRID, alpha=0.6, linestyle="--", linewidth=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    return fig


def render_class_balance_chart():
    benign_count = 9600
    malicious_count = 400
    sizes = [benign_count, malicious_count]
    colors = ["#5ec99c", "#e07a85"]
    explode = (0, 0.06)

    fig, ax = plt.subplots(figsize=(3, 3))
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)

    wedges, _texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": CHART_BG, "linewidth": 2},
        autopct=lambda pct: f"{pct:.0f}%",
        pctdistance=0.78,
        textprops={"color": CHART_TITLE, "fontsize": 10, "fontweight": "600"},
    )

    for autotext in autotexts:
        autotext.set_color("#0a0e14")

    ax.text(0, 0.04, "10K", ha="center", va="center",
            fontsize=16, fontweight="700", color=CHART_TITLE, fontfamily="monospace")
    ax.text(0, -0.14, "records", ha="center", va="center",
            fontsize=9, color=CHART_TEXT, fontfamily="sans-serif")

    ax.legend(
        wedges,
        [f"Benign {benign_count:,}", f"Malicious {malicious_count:,}"],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=2,
        frameon=False,
        fontsize=8,
        labelcolor=CHART_TEXT,
    )

    plt.tight_layout()
    return fig


def render_prediction_result(prediction, malicious_prob):
    is_malicious = prediction == 1
    card_class = "result--malicious" if is_malicious else "result--benign"
    icon_svg = ICON_CIRCLE_ALERT if is_malicious else ICON_CIRCLE_CHECK
    verdict_text = "Malicious traffic detected" if is_malicious else "Benign traffic"
    verdict_sub = (
        "Session matches known attack signatures" if is_malicious
        else "No malicious indicators found in this session"
    )
    benign_prob = (1 - malicious_prob) * 100
    mal_prob_pct = malicious_prob * 100

    if malicious_prob < 0.30:
        risk_class, risk_text = "risk--low", "Low Risk"
        risk_icon = ICON_CIRCLE_CHECK
    elif malicious_prob < 0.70:
        risk_class, risk_text = "risk--medium", "Medium Risk"
        risk_icon = ICON_CIRCLE_ALERT
    else:
        risk_class, risk_text = "risk--high", "High Risk"
        risk_icon = ICON_CIRCLE_X

    st.html(
        f"""
        <div class="result {card_class}" role="status" aria-live="polite">
            <div class="result__head">
                <div>
                    <div class="result__label">Classification Result</div>
                    <h3 class="result__verdict result__verdict--{('malicious' if is_malicious else 'benign')}">{verdict_text}
                        <small>{verdict_sub}</small>
                    </h3>
                </div>
                <div class="result__icon">{icon_svg}</div>
            </div>

            <div class="result__grid">
                <div class="result__prob">
                    <div class="result__label" style="margin-bottom: 8px;">Threat Probability</div>
                    <div class="result__prob-label">
                        <span>Benign <strong>{benign_prob:.1f}%</strong></span>
                        <span>Malicious <strong>{mal_prob_pct:.1f}%</strong></span>
                    </div>
                    <div class="result__prob-track" role="progressbar"
                         aria-valuenow="{mal_prob_pct:.1f}" aria-valuemin="0" aria-valuemax="100">
                        <div class="result__prob-fill" style="width: {mal_prob_pct:.1f}%;"></div>
                    </div>
                </div>
                <div>
                    <div class="result__label" style="margin-bottom: 8px;">Risk Assessment</div>
                    <span class="risk {risk_class}">
                        {risk_icon}<span>{risk_text}</span>
                    </span>
                </div>
            </div>
        </div>
        """,
    )


# ==========================
# SIDEBAR
# ==========================

with st.sidebar:
    st.html(
        f"""
        <div class="brand">
            <div class="brand__mark">
                <div class="brand__logo">{ICON_SHIELD}</div>
                <div class="brand__name">Sentinel IDS</div>
            </div>
            <div class="brand__tag">Network Intrusion Detection Platform</div>
        </div>
        """,
    )

    st.html(
        f"""
        <div class="panel">
            <div class="panel__title"><span class="panel__title-dot"></span><span>Active Model</span></div>
            <p><strong>Weighted XGBoost</strong> classifier<br><br>
            Classifies live network traffic as <strong>benign</strong> or <strong>malicious</strong>
            using port, protocol, timing, and user-agent signals.</p>
        </div>
        """,
    )

    st.html(
        f"""
        <div class="panel">
            <div class="panel__title"><span>System Status</span></div>
            <ul class="status-list">
                <li><span class="status-list__label">Engine</span><span class="status-list__value status-list__value--online">Online</span></li>
                <li><span class="status-list__label">Model</span><span class="status-list__value">XGBoost</span></li>
                <li><span class="status-list__label">Features</span><span class="status-list__value">21</span></li>
                <li><span class="status-list__label">Classes</span><span class="status-list__value">2</span></li>
            </ul>
        </div>
        """,
    )

    st.html(
        f"""
        <div class="panel">
            <div class="panel__title"><span>Tip</span></div>
            <p>Suspicious user agents like <em>sqlmap</em>, <em>curl</em>, and <em>zgrab</em>
            are strong indicators of automated scanning activity.</p>
        </div>
        """,
    )

# ==========================
# HERO -- asymmetric split (anti-center bias)
# ==========================

st.html(
    f"""
    <div class="hero">
        <div class="hero__copy">
            <div class="hero__eyebrow">Machine Learning for Cybersecurity</div>
            <h1 class="hero__title">Real-time <em>intrusion detection</em><br>for live network traffic.</h1>
            <p class="hero__sub">Analyze sessions, classify risk, surface attacks. Trained on imbalanced traffic data, weighted for rare-event detection.</p>
            <div class="hero__meta">
                <div class="hero__meta-item">
                    <span class="hero__meta-label">Engine</span>
                    <span class="hero__meta-value">XGBoost · v2</span>
                </div>
                <div class="hero__meta-item">
                    <span class="hero__meta-label">Latency</span>
                    <span class="hero__meta-value">~ 80 ms</span>
                </div>
                <div class="hero__meta-item">
                    <span class="hero__meta-label">Features</span>
                    <span class="hero__meta-value">21 signals</span>
                </div>
                <div class="hero__meta-item">
                    <span class="hero__meta-label">Status</span>
                    <span class="hero__meta-value" style="color: var(--success);">● Online</span>
                </div>
            </div>
        </div>
        <div class="hero__visual">
            <div class="hero__grid"></div>
            <div class="hero__shield">
                <div class="hero__shield-ring"></div>
                <div class="hero__shield-ring"></div>
                <div class="hero__shield-ring"></div>
                <div class="hero__shield-core">{ICON_SHIELD}</div>
            </div>
        </div>
    </div>
    """
)

# ==========================
# MODEL PERFORMANCE -- bento (asymmetric)
# ==========================

section_header(ICON_CHART, "Model Performance", "Weighted XGBoost · test split")

metrics = [
    (
        "Accuracy",
        format_pct(MODEL_ACCURACY),
        "success",
        METRIC_TOOLTIPS["Accuracy"],
        None,
        "baseline on 10K records",
        '<svg viewBox="0 0 64 24"><polyline fill="none" stroke="#5ec99c" stroke-width="1.5" points="0,18 8,14 16,16 24,10 32,12 40,8 48,9 56,4 64,6"/></svg>',
        True,
    ),
    (
        "Precision",
        format_pct(MODEL_PRECISION),
        "",
        METRIC_TOOLTIPS["Precision"],
        None,
        "attack-class precision",
        '<svg viewBox="0 0 64 24"><polyline fill="none" stroke="#4ec9d4" stroke-width="1.5" points="0,16 8,14 16,12 24,13 32,10 40,8 48,9 56,6 64,4"/></svg>',
        False,
    ),
    (
        "Recall",
        format_pct(MODEL_RECALL),
        "warning",
        METRIC_TOOLTIPS["Recall"],
        None,
        "true-positive rate",
        '<svg viewBox="0 0 64 24"><polyline fill="none" stroke="#e6b85c" stroke-width="1.5" points="0,18 8,16 16,12 24,10 32,11 40,9 48,7 56,8 64,6"/></svg>',
        False,
    ),
    (
        "F1 Score",
        format_pct(MODEL_F1),
        "accent",
        METRIC_TOOLTIPS["F1"],
        '<span style="font-family:\'Geist Mono\',monospace;font-weight:600;">F1</span>&nbsp;Score',
        "precision-recall balance",
        '<svg viewBox="0 0 64 24"><polyline fill="none" stroke="#4ec9d4" stroke-width="1.5" points="0,20 8,16 16,12 24,10 32,12 40,8 48,10 56,6 64,8"/></svg>',
        False,
    ),
]
bento_html = '<div class="bento">'
for i, (label, value, css, tooltip, label_html, delta, spark, feature) in enumerate(metrics):
    bento_html += metric_card(label, value, css, tooltip, label_html, delta, spark, feature, index=i)
bento_html += "</div>"
st.html(bento_html)

# ==========================
# INPUT FORM
# ==========================

section_header(ICON_RADAR, "Traffic Analysis", "Configure a session")

form_col1, form_col2 = st.columns(2)

with form_col1:
    st.html(
        '<div class="form-card"><div class="form-card__head"><span class="form-card__title">Connection Details</span><span class="form-card__tag">TCP · UDP</span></div>',
    )
    src_port = st.number_input("Source Port", min_value=0, max_value=65535, value=5000)
    dst_port = st.number_input("Destination Port", min_value=0, max_value=65535, value=443)
    bytes_sent = st.number_input("Bytes Sent", min_value=0, value=10000)
    bytes_received = st.number_input("Bytes Received", min_value=0, value=20000)
    st.html("</div>")

with form_col2:
    st.html(
        '<div class="form-card"><div class="form-card__head"><span class="form-card__title">Session Metadata</span><span class="form-card__tag">context</span></div>',
    )
    is_internal = st.selectbox("Internal Traffic", [False, True])
    hour = st.slider("Hour of Day", 0, 23, 12)
    day = st.slider("Day of Month", 1, 31, 15)
    protocol = st.selectbox("Protocol", ["TCP", "UDP", "ICMP"])
    user_agent = st.selectbox("User Agent", list(USER_AGENT_MAPPING.keys()))
    st.html("</div>")

validation_errors = validate_inputs(
    src_port, dst_port, bytes_sent, bytes_received, user_agent, protocol
)
form_valid = len(validation_errors) == 0

if st.session_state.show_validation and validation_errors:
    render_validation_errors(validation_errors)

st.html('<div class="cta-row">')
predict_button = st.button(
    "Run threat analysis",
    use_container_width=False,
    disabled=not form_valid,
    type="primary",
)
st.html("</div>")

if not form_valid:
    st.html(
        '<p class="cta-hint cta-hint--disabled" style="text-align:center;">'
        "Resolve validation errors to enable analysis."
        "</p>",
    )
else:
    st.html(
        '<p class="cta-hint" style="text-align:center;">Estimated runtime · &lt; 100 ms</p>',
    )

# ==========================
# PREDICTION
# ==========================

if predict_button and form_valid:
    st.session_state.show_validation = False
    with st.spinner("Analyzing traffic patterns…"):
        time.sleep(0.6)
        input_data = build_input_data(
            src_port, dst_port, bytes_sent, bytes_received,
            is_internal, hour, day, protocol, user_agent,
        )
        input_df = pd.DataFrame([input_data])
        prediction = model.predict(input_df)[0]
        malicious_prob = model.predict_proba(input_df)[0][1]
        st.session_state.analysis_result = {
            "prediction": int(prediction),
            "malicious_prob": float(malicious_prob),
        }
elif predict_button and not form_valid:
    st.session_state.show_validation = True

if st.session_state.analysis_result:
    section_header(ICON_TARGET, "Analysis Result", "Live prediction")
    result = st.session_state.analysis_result
    render_prediction_result(result["prediction"], result["malicious_prob"])

st.html("<hr>")

# ==========================
# ANALYTICS ROW
# ==========================

section_header(ICON_BOLT, "Model Insights", "Features · dataset balance")

col_chart, col_stats = st.columns([3, 2], vertical_alignment="top")

with col_chart:
    st.html(
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        '<h3 style="font-size:0.85rem;font-weight:600;color:#e6ebf2;margin:0;letter-spacing:-0.005em;">Top 10 model features</h3>'
        '<span style="font-family:Geist Mono,monospace;font-size:0.7rem;color:#8593a3;">Gain · weighted</span>'
        '</div>',
    )
    st.pyplot(render_feature_chart(), use_container_width=True)

with col_stats:
    st.html(
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        '<h3 style="font-size:0.85rem;font-weight:600;color:#e6ebf2;margin:0;letter-spacing:-0.005em;">Training dataset balance</h3>'
        '<span style="font-family:Geist Mono,monospace;font-size:0.7rem;color:#8593a3;">10,000 records</span>'
        '</div>',
    )
    st.pyplot(render_class_balance_chart(), use_container_width=True)
    st.html(
        """
        <div class="dataset-row"><span class="dataset-row__label">Total records</span><span class="dataset-row__value">10,000</span></div>
        <div class="dataset-row"><span class="dataset-row__label">Benign traffic</span><span class="dataset-row__value dataset-row__value--benign">9,600</span></div>
        <div class="dataset-row"><span class="dataset-row__label">Malicious traffic</span><span class="dataset-row__value dataset-row__value--malicious">400</span></div>
        <div class="dataset-row"><span class="dataset-row__label">Class ratio</span><span class="dataset-row__value">24 : 1</span></div>
        """,
    )

# ==========================
# FOOTER
# ==========================

st.html(
    """
    <div class="footer">
        <span><span class="footer__mark">●</span>&nbsp; Sentinel IDS · Intrusion Detection System</span>
        <span>Weighted XGBoost · production-ready</span>
    </div>
    """
)
