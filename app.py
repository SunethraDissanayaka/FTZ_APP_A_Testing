###############################################
# FTZ Savings – Agentic AI Calculator (MAIN)
###############################################

import streamlit as st
import pandas as pd
import difflib
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================================
# GOOGLE SHEETS LOGGING (REPLACES LOCAL EXCEL)
# =====================================================
import gspread
from google.oauth2.service_account import Credentials

# import streamlit as st

# st.write(st.secrets["gcp_service_account"].keys())


SHEET_NAME = "FTZ_App_Usage_Log"

LOG_COLUMNS = [
    "timestamp",
    "session_id",
    "net_savings",
    "cost_with_ftz",
    "cost_without_ftz",
    "cta_clicked",
    "cta_name",
    "cta_company",
    "cta_email",
    "cta_phone",
    "cta_message",
    "chat_question",
]

@st.cache_resource
def get_sheet():
    # scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    # creds = Credentials.from_service_account_info(
    #     st.secrets["gcp_service_account"],
    #     scopes=scopes

    SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1

    # Ensure headers exist
    if sheet.row_count == 0 or sheet.get_all_values() == []:
        sheet.append_row(LOG_COLUMNS)

    return sheet

def log_to_google_sheets(row: dict):
    sheet = get_sheet()

    row_data = {
        col: row.get(col, "")
        for col in LOG_COLUMNS
    }

    row_data["timestamp"] = datetime.now(
        ZoneInfo("America/New_York")
    ).strftime("%Y-%m-%d %H:%M:%S EST")

    sheet.append_row(list(row_data.values()))

# =====================================================
# SESSION ID
# =====================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="FTZ Savings – Agentic AI Calculator",
    layout="wide",
    page_icon="💼"
)

# -----------------------------
# MONEY FORMATTER
# -----------------------------
def money(x):
    try:
        x = float(x)
    except:
        return x
    return f"(${abs(x):,.0f})" if x < 0 else f"${x:,.0f}"

# -----------------------------
# GLOBAL STYLE (UNCHANGED)
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f8fafc,#eef2f7);
}
h1,h2,h3 { color:#0f172a; }
.soft-card {
    background:white;
    border-radius:10px;
    padding:14px;
    box-shadow:0 3px 10px rgba(0,0,0,0.08);
}
.kpi-card {
    background:#0f172a;
    color:white;
    border-radius:10px;
    padding:14px;
    text-align:center;
}
.kpi-value {
    font-size:20px;
    font-weight:700;
}
.glass {
    background:rgba(15,23,42,0.75);
    backdrop-filter:blur(12px);
    padding:24px;
    border-radius:14px;
    color:white;
}
/* COMPLETELY HIDE STREAMLIT SIDEBAR */
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="stSidebar"] { display:none; }
.chat-user {color:#0f172a;font-weight:600;}
.chat-ai {color:#2563eb;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER (UNCHANGED)
# -----------------------------
st.markdown(
    "<h3 style='text-align:center;'>FTZ Savings – Agentic AI Calculator - A Testing</h3>",
    unsafe_allow_html=True
)

left, center, right = st.columns([2, 1, 2])
with center:
    st.image("assets/mas_logo.jpg", width=150)

st.markdown("""
<div style="text-align:center; max-width:700px; margin:auto;">
<p style="color:#334155; font-size:15px; line-height:1.5;">
We MAS US Holdings have created a best-in-class, transparent, and conversion-focused digital experience,
ready to drive full spectrum of value unlocks through the FTZ apparel offering.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# INPUTS (UNCHANGED)
# =====================================================
st.subheader("Customer Data Assumptions")

r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
shipments_per_week = r1c1.number_input("Shipments / Week", min_value=1, value=2)
avg_import_value = r1c2.number_input("Avg Import Value ($)", 1000, value=500000, step=1000)
mpf_pct = r1c3.number_input("MPF %", value=0.35, disabled=True)
broker_cost = r1c4.number_input("Broker Cost ($/entry)", value=125.0)
current_interest_rate = r1c5.number_input("Current Interest Rate (%)", value=6.5)

r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns(5)
export_pct = r2c1.number_input("Export %", 0.0, 100.0, 1.0)
offspec_pct = r2c2.number_input("Off-Spec %", 0.0, 100.0, 0.25)
hmf_pct = r2c3.number_input("HMF %", value=0.13, disabled=True)
duty_pct = r2c4.number_input("Avg Duty %", 0.0, 100.0, 30.0)
avg_stock_holding_days = r2c5.number_input("Avg # Stock Holding Days", value=45)

st.markdown("**Costs With FTZ (Annual)**")
c1, c2, c3, c4 = st.columns(4)
ftz_consult = c1.number_input("FTZ Consulting ($)", value=50000)
ftz_mgmt = c2.number_input("FTZ Management ($)", value=150000)
ftz_software = c3.number_input("FTZ Software Fee ($)", value=40000)
ftz_bond = c4.number_input("FTZ Operator Bond ($)", value=1000)

st.markdown("**Costs Without FTZ (Annual)**")
n1, n2, n3, n4 = st.columns(4)
noftz_consult = n1.number_input("Consulting (No FTZ)", value=0)
noftz_mgmt = n2.number_input("Management (No FTZ)", value=0)
noftz_software = n3.number_input("Software (No FTZ)", value=0)
noftz_bond = n4.number_input("Operator Bond (No FTZ)", value=0)

# =====================================================
# CORE CALCULATIONS (UNCHANGED)
# =====================================================
# --- Percentage conversions ---
export_sales = export_pct / 100
off_spec = offspec_pct / 100
mpf_rate = mpf_pct / 100
hmf_rate = hmf_pct / 100
avg_duty = duty_pct / 100

# --- Annual import value ---
total_import_value = shipments_per_week * avg_import_value * 52

# --- Duty calculations ---
total_duty = total_import_value * avg_duty
duty_saved_export = total_import_value * export_sales * avg_duty
duty_saved_offspec = total_import_value * off_spec * avg_duty

total_net_duty_no_ftz = total_duty
total_net_duty_with_ftz = total_duty - duty_saved_export - duty_saved_offspec

# --- Entry & MPF calculations ---
entries_per_year = shipments_per_week * 52

per_entry_mpf = min(avg_import_value * mpf_rate, 634.62)
mpf_no_ftz = per_entry_mpf * entries_per_year

weekly_mpf_base = shipments_per_week * avg_import_value * mpf_rate
mpf_with_ftz = min(weekly_mpf_base, 634.62) * 52

# --- Broker & HMF ---
broker_hmf_no_ftz = (
    entries_per_year * broker_cost
    + shipments_per_week * avg_import_value * hmf_rate
)

broker_hmf_with_ftz = (
    52 * broker_cost
    + shipments_per_week * avg_import_value * hmf_rate
)

# --- Operating costs ---
cost_with_ftz = ftz_consult + ftz_mgmt + ftz_software + ftz_bond
cost_without_ftz = noftz_consult + noftz_mgmt + noftz_software + noftz_bond

# --- Total landed cost ---
total_cost_without_ftz = (
    total_net_duty_no_ftz + mpf_no_ftz + broker_hmf_no_ftz + cost_without_ftz
)



# Convert interest rate to decimal
interest_rate = current_interest_rate / 100

# Duty capital tied up under FTZ
deferred_duty_amount = total_net_duty_with_ftz

# Total Working Capital Savings (H25 equivalent)
total_wc_saving = (
    deferred_duty_amount
    * interest_rate
    * (avg_stock_holding_days / 365)
)
# ---------------------------------------------------------
# ADJUST COST WITH FTZ (DEDUCT WC SAVINGS)
# ---------------------------------------------------------
total_cost_with_ftz = (
    total_net_duty_with_ftz + mpf_with_ftz + broker_hmf_with_ftz + cost_with_ftz-total_wc_saving
)
#total_cost_with_ftz_adj = total_cost_with_ftz - total_wc_saving

# --- Final savings ---
net_savings_to_brand = total_cost_without_ftz - total_cost_with_ftz


# =====================================================
# BUTTONS
# =====================================================
b1, b2, b3 = st.columns(3)
calculate = b1.button("📊 Calculate Savings", use_container_width=True)
details = b3.button("📄 Show Details", use_container_width=True)

# =====================================================
# KPI + LOGGING
# =====================================================
if calculate:

    log_to_google_sheets({
        "session_id": st.session_state.session_id,
        "net_savings": net_savings_to_brand,
        "cost_with_ftz": total_cost_with_ftz,
        "cost_without_ftz": total_cost_without_ftz,
        "cta_clicked": "No",
    })

    k1, k2, k3, k4 = st.columns(4)

    # k1.metric("Total Duty Baseline", money(total_duty))
    # k2.metric("Cost With FTZ", money(total_cost_with_ftz))
    # k3.metric("Cost Without FTZ", money(total_cost_without_ftz))
    # k4.metric("Net Savings", money(net_savings_to_brand))
    def money_fmt_val(x):
        try:
            x = float(x)
        except:
            return x

        if x < 0:
            return f"(${abs(x):,.0f})"
        return f"${x:,.0f}"
    if calculate:
        k1, k2, k3, k4 = st.columns(4)

        # -------- KPI 1 — Total Duty Baseline --------
        with k1:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>💰 Total Duty Baseline</div>
                <div class='kpi-value'>
                    {money_fmt_val(total_duty)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # -------- KPI 2 — Cost With FTZ --------
        with k2:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📦 Cost With FTZ</div>
                <div class='kpi-value'>
                    {money_fmt_val(total_cost_with_ftz)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # -------- KPI 3 — Cost Without FTZ --------
        with k3:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>🏷 Cost Without FTZ</div>
                <div class='kpi-value'>
                    {money_fmt_val(total_cost_without_ftz)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # -------- KPI 4 — Net Savings --------
        with k4:
            savings_color = "#22c55e" if net_savings_to_brand >= 0 else "#ef4444"

            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📉 Net Savings</div>
                <div class='kpi-value' style='color:{savings_color};'>
                    {money_fmt_val(net_savings_to_brand)}
                </div>
            </div>
            """, unsafe_allow_html=True)


# =====================================================
# SMART CTA (LOGGED)
# =====================================================
if "cta_open" not in st.session_state:
    st.session_state.cta_open = False

if b2.button("📞 Smart CTA", use_container_width=True):
    st.session_state.cta_open = True

if st.session_state.cta_open:
    st.markdown("---")
    st.markdown(
        "<h4 style='color:#0f172a;'>📞 Smart CTA — Request a Consultation</h4>",
        unsafe_allow_html=True
    )
    # with st.form("cta_form"):
    #     name = st.text_input("Full Name *")
    #     company = st.text_input("Company *")
    #     email = st.text_input("Email *")
    #     phone = st.text_input("Phone")
    #     message = st.text_area("Message")
    #     submit = st.form_submit_button("Request a Call")
    with st.form("smart_cta_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *")
            company = st.text_input("Company *")
        with c2:
            email = st.text_input("Business Email *")
            phone = st.text_input("Phone Number *")
        message = st.text_area("Question", placeholder="Anything specific you'd like us to review before the call?")

        submit = st.form_submit_button("Request a Call")
    if submit:
        log_to_google_sheets({
            "session_id": st.session_state.session_id,
            "net_savings": net_savings_to_brand,
            "cost_with_ftz": total_cost_with_ftz,
            "cost_without_ftz": total_cost_without_ftz,
            "cta_clicked": "Yes",
            "cta_name": name,
            "cta_company": company,
            "cta_email": email,
            "cta_phone": phone,
            "cta_message": message,
        })
        st.success("✅ Thank you! Your request has been received.\n\n"
                "Our FTZ advisory team will contact you shortly..")
        
# -----------------------------
# DETAILS PAGE NAV
# -----------------------------
if details:
    st.switch_page("pages/1_Show_Details.py")

# =====================================================
# CHATBOT (UNMATCHED LOGGING)
# =====================================================
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>FTZ Chatbot Assistant</h4>", unsafe_allow_html=True)

faq_qa = {
    "ftz-enabled single-sku omnichannel advantages apparel 3pl": 
    "Think of one, unified inventory heartbeat serving DTC, marketplaces, and retail. "
    "In our FTZ, that single-SKU pool removes duplicate stock, cuts stockouts, and enables "
    "two-day promises—while the zone’s duty advantages keep more margin in your pocket. "
    "It’s the apparel-native system founders wish they had from day one.",

    "direct cash flow savings immediate not deferral": 
    "You’ll feel savings right away: duties vanish on exports and off-spec goods, MPF fees drop "
    "when we consolidate entries weekly, and you only part with duty when product enters U.S. commerce. "
    "It’s immediate cash you can redirect to growth, not just an accounting fiction.",

    "brands benefit most ftz omnichannel": 
    "Brands that import, move fast, and sell across channels—DTC expanding to wholesale, "
    "marketplace-heavy, international entrants, seasonal or high-SKU lines—see the biggest lift.",

    "how are numbers calculated": 
    "The calculator uses your operational inputs—shipments per week, average import value, "
    "export %, off-spec %, broker fees, and average duty rate. FTZ rules are applied to show "
    "duty saved on exports, off-spec relief, and MPF savings from weekly consolidation.",

    "numbers unusual outside typical ranges": 
    "No problem—outliers are fine. The calculator is directional. For unusual flows, "
    "a consultation unlocks a tuned, custom analysis.",

    "why savings negative": 
    "Negative savings signal volume, cost structure, or assumption issues. "
    "Higher consolidation, better HTS averages, and stronger export/off-spec flows "
    "often flip results positive.",

    "data bring consultation precise analysis": 
    "Bring HTS mix, channel split, return rates, freight modes, and your cost stack. "
    "These inputs unlock precision and actionable ROI insights.",

    "how estimate savings exported off spec inputs": 
    "Using shipments per week, average import value, export %, off-spec %, broker fees, "
    "and duty rate, the calculator converts flows into duty savings and entry reductions.",

    "what are mpf hmf weekly entry consolidation": 
    "MPF is capped per entry; HMF applies to ocean freight. Weekly consolidation "
    "reduces how often fees are paid—so savings compound quickly.",

    "hmf air land freight": 
    "HMF applies only to ocean freight. If your flow is air or land, it is excluded "
    "so results reflect reality.",

    "varying duty rates hts season accuracy": 
    "We start with an average duty rate to show direction. SKU-level precision "
    "comes during a consult.",

    "entries per shipment vs weekly consolidated entries": 
    "Non-FTZ assumes one entry per shipment; FTZ assumes one weekly entry. "
    "Enter shipments per week and the calculator models both automatically.",

    "difference vs global 3pls d2c brokers": 
    "We combine FTZ economics, apparel-native workflows, and omnichannel execution—"
    "speed, compliance, and margin in one system.",

    "support retail edi asn marketplace prep": 
    "Yes. One FTZ inventory pool feeds retail, marketplaces, and DTC—"
    "eliminating duplicate stock.",

    "how fast pilot go live 60 90 days": 
    "Our 60–90 day pilot connects systems, activates FTZ inventory, "
    "and runs live orders quickly.",

    "what not included calculator results": 
    "We focus on immediate savings. Working capital, inventory days, "
    "and deeper ROI come in custom models.",

    "quantify working capital inventory days": 
    "Yes—deferral, inventory pooling, and margin impacts are quantified "
    "during consultation.",

    "compliance guardrails audit ready apparel": 
    "Tight inventory controls, auditable entries, and apparel-specific SOPs "
    "keep operations compliant and scalable.",

    "export off spec ranges validation": 
    "Exports typically 0–30%; off-spec usually under 5%. "
    "Outliers are fine but directional.",

    "export share results pdf excel consult": 
    "Export PDF/Excel directly and use the consult CTA "
    "to turn estimates into execution."
}
faq_keys = list(faq_qa.keys())

import difflib

def match_question(q):
    m = difflib.get_close_matches(q.lower(), faq_keys, 1, 0.55)
    return faq_qa[m[0]] if m else None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

q = st.text_input("Ask a question about FTZ:")

if st.button("Ask AI"):
    ans = match_question(q)
    if not ans:
        log_to_google_sheets({
            "session_id": st.session_state.session_id,
            "net_savings": net_savings_to_brand,
            "cost_with_ftz": total_cost_with_ftz,
            "cost_without_ftz": total_cost_without_ftz,
            "chat_question": q,
        })
        ans = "Thank you for your question, Your question will be directed to the Customer Success Lead at MAS US Holdings at oscarc@masholdings.com."
            

    st.session_state.chat_history.append(("You", q))
    st.session_state.chat_history.append(("AI", ans))

for s, m in st.session_state.chat_history:
    #st.markdown(f"**{s}:** {m}")
    if s == "You":
        st.markdown(
            f"<div class='chat-user'><strong>You:</strong> {m}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='chat-ai'><strong>AI:</strong> {m}</div>",
            unsafe_allow_html=True
        )


st.markdown("---")
st.markdown("""
**Disclaimer:**  
This calculator provides directional estimates only and does not constitute financial,
legal, or compliance advice.
""")
