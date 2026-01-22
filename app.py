###############################################
# FTZ Savings – Agentic AI Calculator (MAIN)
###############################################

import streamlit as st
import pandas as pd
import difflib
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
#from utils import calculate_summary
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
    "wc_saving",
    "cta_clicked",
    "cta_name",
    "cta_company",
    "cta_email",
    "cta_phone",
    "cta_preferred_date",
    "cta_preferred_time",
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
            
.kpi-card_new {
    background:#052c87;
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
# st.markdown(
#     "<h3 style='text-align:center;'>FTZ Savings – Agentic AI Calculator - A Testing</h3>",
#     unsafe_allow_html=True
# )

st.markdown(
    """
    <h3 style="text-align:center;">
        Foreign Trade Zone (FTZ) Saving Agentic AI Simulator
        
    </h3>
    """,
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

defaults = {
    "shipments_per_week": 2,
    "avg_import_value": 500000,
    "mpf_pct": 0.35,
    "hmf_pct": 0.13,
    "duty_pct": 30.0,
    "export_pct": 1.0,
    "offspec_pct": 0.25,
    "broker_cost": 125.0,
    "current_interest_rate": 7,
    "avg_stock_holding_days": 120,
    "ftz_consult": 19000,
    "ftz_mgmt": 100000,
    "ftz_software": 10000,
    "ftz_bond": 1000,
    "noftz_consult": 0,
    "noftz_mgmt": 0,
    "noftz_software": 0,
    "noftz_bond": 0,
}

FTZ_CONSTS = {
    "ftz_consult": 19000,
    "ftz_mgmt": 100000,
    "ftz_software": 10000,
    "ftz_bond": 1000,
}

for key, value in defaults.items():
    st.session_state.setdefault(key, value)

for k, v in FTZ_CONSTS.items():
    st.session_state[k] = v  # keep in session for cross-page syncing

# remove all No-FTZ operating costs from state & calculations
for k in ["noftz_consult", "noftz_mgmt", "noftz_software", "noftz_bond"]:
    st.session_state[k] = 0.0

# =====================================================
# INPUTS (UNCHANGED)
# =====================================================
st.subheader("Customer Data Inputs",help=("Please Enter Your Inputs"
        
    ),)

cols = st.columns(5)
st.session_state["shipments_per_week"] = cols[0].number_input("Shipments / Week", 1, value=st.session_state["shipments_per_week"])
st.session_state["avg_import_value"] = cols[1].number_input("Avg Import Value ($)", 1000, step=1000, value=st.session_state["avg_import_value"])
#st.number_input("MPF %", value=st.session_state["mpf_pct"], disabled=True)
cols[2].number_input("MPF %", value=st.session_state["mpf_pct"], disabled=True, key="mpf_pct", help=("Merchandize Processing Fee"  
    ))

st.session_state["broker_cost"] = cols[3].number_input("Broker Cost ($/entry)", value=st.session_state["broker_cost"])
#st.session_state["current_interest_rate"] = cols[4].number_input("Current Interest Rate (%)", value=st.session_state["current_interest_rate"])
st.session_state["current_interest_rate"] = cols[4].number_input("Cost of Capital %", value=st.session_state["current_interest_rate"])


cols2 = st.columns(5)
st.session_state["export_pct"] = cols2[0].number_input("Export %", 0.0, 100.0, step=1.0, value=st.session_state["export_pct"])
st.session_state["offspec_pct"] = cols2[1].number_input("Off-Spec %", 0.0, 100.0, step=0.01, help=("Off-Specification Merchandize" ), value=st.session_state["offspec_pct"])
cols2[2].number_input("HMF %", value=st.session_state["hmf_pct"], disabled=True,key="hmf_pct", help=("Harbor Maintenance Fee" ))
st.session_state["duty_pct"] = cols2[3].number_input("Avg Duty %", 0.0, 100.0, step=0.1, value=st.session_state["duty_pct"])
st.session_state["avg_stock_holding_days"] = cols2[4].number_input("Avg Stock Holding Days", help=(
        "(360/Inv Turns) or Days of Supply 0r (Months of Supply * 30)"
    ), value=st.session_state["avg_stock_holding_days"])
# 
# --- Disclaimer (small, italic, grey) ---
st.markdown(
    """
    <div style="margin-top:8px; color:#6b7280; font-size:12px;">
      <span style="color:#9ca3af;">*</span>
      <em>
        MAS USA Holdings' provides a wide array of FTZ Services for you to take advantage of and those savings are presented as "Net Savings using FTZ" and  potential "Woking Capital Savings" separately
      </em>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")
# st.markdown("**Costs With FTZ (Annual)**")
# c1, c2, c3, c4 = st.columns(4)
# st.session_state["ftz_consult"] = c1.number_input("FTZ Consulting ($)", value=st.session_state["ftz_consult"])
# st.session_state["ftz_mgmt"] = c2.number_input("FTZ Management ($)", value=st.session_state["ftz_mgmt"])
# st.session_state["ftz_software"] = c3.number_input("FTZ Software Fee ($)", value=st.session_state["ftz_software"])
# st.session_state["ftz_bond"] = c4.number_input("FTZ Operator Bond ($)", value=st.session_state["ftz_bond"])

# st.markdown("**Costs With FTZ (Annual)**")
# c1, c2, c3, c4 = st.columns(4)
# with c1:
#     st.metric("FTZ Consulting ($)", f"{int(st.session_state['ftz_consult']):,}")
# with c2:
#     st.metric("FTZ Management ($)", f"{int(st.session_state['ftz_mgmt']):,}")
# with c3:
#     st.metric("FTZ Software Fee ($)", f"{int(st.session_state['ftz_software']):,}")
# with c4:
#     st.metric("FTZ Operator Bond ($)", f"{int(st.session_state['ftz_bond']):,}")

# st.markdown("**Costs Without FTZ (Annual)**")
# n1, n2, n3, n4 = st.columns(4)
# st.session_state["noftz_consult"] = n1.number_input("Consulting (No FTZ)", value=st.session_state["noftz_consult"])
# st.session_state["noftz_mgmt"] = n2.number_input("Management (No FTZ)", value=st.session_state["noftz_mgmt"])
# st.session_state["noftz_software"] = n3.number_input("Software (No FTZ)", value=st.session_state["noftz_software"])
# st.session_state["noftz_bond"] = n4.number_input("Operator Bond (No FTZ)", value=st.session_state["noftz_bond"])

# =====================================================
# BIND LOCALS FOR CALCULATIONS (this is what was missing)
# =====================================================
shipments_per_week   = st.session_state["shipments_per_week"]
avg_import_value     = st.session_state["avg_import_value"]
mpf_pct              = st.session_state["mpf_pct"]
hmf_pct              = st.session_state["hmf_pct"]
duty_pct             = st.session_state["duty_pct"]
export_pct           = st.session_state["export_pct"]
offspec_pct          = st.session_state["offspec_pct"]
broker_cost          = st.session_state["broker_cost"]
current_interest_rate = st.session_state["current_interest_rate"]
avg_stock_holding_days = st.session_state["avg_stock_holding_days"]

ftz_consult   = st.session_state["ftz_consult"]
ftz_mgmt      = st.session_state["ftz_mgmt"]
ftz_software  = st.session_state["ftz_software"]
ftz_bond      = st.session_state["ftz_bond"]

noftz_consult  = st.session_state["noftz_consult"]
noftz_mgmt     = st.session_state["noftz_mgmt"]
noftz_software = st.session_state["noftz_software"]
noftz_bond     = st.session_state["noftz_bond"]

# =====================================================
# CORE CALCULATIONS (UNCHANGED)
# =====================================================
# --- Percentage conversions ---
export_sales = export_pct / 100
off_spec = offspec_pct / 100
mpf_rate = mpf_pct / 100
hmf_rate = hmf_pct / 100
avg_duty = duty_pct / 100

ftz_consult  = st.session_state["ftz_consult"]
ftz_mgmt     = st.session_state["ftz_mgmt"]
ftz_software = st.session_state["ftz_software"]
ftz_bond     = st.session_state["ftz_bond"]

# removed from model
noftz_consult  = 0.0
noftz_mgmt     = 0.0
noftz_software = 0.0
noftz_bond     = 0.0

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
# total_wc_saving = (
#     deferred_duty_amount
#     * interest_rate
#     * (avg_stock_holding_days / 365)
# )

total_wc_saving = ((total_duty+ mpf_with_ftz)* interest_rate* (avg_stock_holding_days / 365))
# ---------------------------------------------------------
# ADJUST COST WITH FTZ (DEDUCT WC SAVINGS)
# ---------------------------------------------------------
total_cost_with_ftz = (
    total_net_duty_with_ftz + mpf_with_ftz + broker_hmf_with_ftz + cost_with_ftz
)
#total_cost_with_ftz_adj = total_cost_with_ftz - total_wc_saving

# --- Final savings ---
net_savings_to_brand = total_cost_without_ftz - total_cost_with_ftz


# =====================================================
# BUTTONS
# =====================================================
b1, b2, b3 = st.columns(3)
calculate = b1.button("📊 Calculate Savings", use_container_width=True)

def _go_details():
    st.session_state["nav_target"] = "details"   # remember intent across reruns

b3.button("📄 Show Details", key="show_details_btn", use_container_width=True, on_click=_go_details)

#details = b3.button("📄 Show Details", use_container_width=True)

# =====================================================
# KPI + LOGGING
# =====================================================
if calculate:

    log_to_google_sheets({
        "session_id": st.session_state.session_id,
        "net_savings": net_savings_to_brand,
        "cost_with_ftz": total_cost_with_ftz,
        "cost_without_ftz": total_cost_without_ftz,
        "wc_saving": total_wc_saving,
        "cta_clicked": "No",
    })

    k1, k2, k3, k4, k5 = st.columns(5)

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
        k1, k2, k3, k4,k5 = st.columns(5)

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

        with k5:
            savings_color = "#22c55e" if total_wc_saving >= 0 else "#ef4444"

            st.markdown(f"""
            <div class='kpi-card_new'>
                <div class='kpi-label'>📉 Working Capital Saving</div>
                <div class='kpi-value' style='color:{savings_color};'>
                    {money_fmt_val(total_wc_saving)}
                </div>
            </div>
            """, unsafe_allow_html=True)


# =====================================================
# SMART CTA (LOGGED)
# =====================================================
if "cta_open" not in st.session_state:
    st.session_state.cta_open = False

if b2.button("📅 Book Free Consultation Here", use_container_width=True):
    st.session_state.cta_open = True

if st.session_state.cta_open:
    st.markdown("---")
    st.markdown(
        "<h4 style='color:#0f172a;'>📅 Schedule a Meeting with MAS USA FTZ Consultation Team</h4>",
        unsafe_allow_html=True
    )
    
    with st.form("smart_cta_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *")
            company = st.text_input("Company *")
            preferred_date = st.date_input("Preferred Date")
        with c2:
            email = st.text_input("Business Email *")
            phone = st.text_input("Phone Number *")
            preferred_time = st.time_input("Preferred Time")

        # st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        # dtc1, dtc2 = st.columns(2)
        # with dtc1:
        #     preferred_date = st.date_input("Preferred Date")
        #     preferred_time = st.time_input("Preferred Time")
            # if hasattr(st, "datetime_input"):
            #     preferred_dt = st.datetime_input("Preferred Date & Time")
            #     preferred_date, preferred_time = (preferred_dt.date(), preferred_dt.time()) if preferred_dt else (None, None)
            # else:
            #     preferred_date = st.date_input("Preferred Date")
            #     preferred_time = st.time_input("Preferred Time")
            #     preferred_dt = datetime.combine(preferred_date, preferred_time)

        message = st.text_area("Question", placeholder="Anything specific you'd like us to review before the call?")

        submit = st.form_submit_button("Schedule a Meeting")
    if submit:
        log_to_google_sheets({
            "session_id": st.session_state.session_id,
            "net_savings": net_savings_to_brand,
            "cost_with_ftz": total_cost_with_ftz,
            "cost_without_ftz": total_cost_without_ftz,
            "wc_saving": total_wc_saving,
            "cta_clicked": "Yes",
            "cta_name": name,
            "cta_company": company,
            "cta_email": email,
            "cta_phone": phone,
            "cta_preferred_date": preferred_date.isoformat() if preferred_date else "",
            "cta_preferred_time": preferred_time.strftime("%H:%M") if preferred_time else "",
            "cta_message": message,
        })
        st.success("✅ Thank you! Your request has been received.\n\n"
                "MAS FTZ Consultation team will contact you shortly.")
        
    # # --- SECOND SEGMENT: Book a Consultation (with person icon) ---
    # st.markdown(
    #     "<h4 style='color:#0f172a; margin-top:14px;'>👤 Book a Consultation</h4>",
    #     unsafe_allow_html=True
    # )

    # # Set your booking link here
    # BOOKING_URL = "https://outlook.office.com/bookwithme/user/c143102e201742738e4a73274b7ead96@masholdings.com/meetingtype/8nt2nJ0om0uxZ9yc187X_w2?anonymous&ismsaljsauthenabled&ep=mCardFromTile"

    # # Prefer st.link_button if available (Streamlit ≥ 1.29).
    # # If your version doesn't support it, uncomment the fallback below.
    # try:
    #     st.link_button("Book Consultation", BOOKING_URL, use_container_width=False)
    # except Exception:
    #     # Fallback: styled Markdown link to look like a button
    #     st.markdown(
    #         f"""
    #         <a href="{BOOKING_URL}" target="_blank"
    #         style="
    #             display:inline-block;
    #             background:#0f172a; color:#fff; text-decoration:none;
    #             padding:8px 14px; border-radius:8px; font-weight:600;">
    #         Book Consultation
    #         </a>
    #         """,
    #         unsafe_allow_html=True
    #     )
        
# -----------------------------
# DETAILS PAGE NAV
# -----------------------------
# if details:
#     st.switch_page("pages/1_Show_Details.py")
if st.session_state.get("nav_target") == "details":
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
    "to turn estimates into execution.",

    "what is an ftz foreign trade zone":
        "A Foreign-Trade Zone (FTZ) is a secured area under U.S. Customs supervision where imported goods "
        "can be stored, processed, or re-exported with deferral, reduction, or elimination of customs duties.",

    "who qualifies for an ftz apparel brand":
        "Importers who regularly bring merchandise into the U.S. and manage inventory benefit most—especially "
        "apparel brands with multi-channel flows (DTC, wholesale, marketplaces) and material export or off-spec volumes.",

    "how long does ftz activation take timeline":
        "Most brands can activate and go live in roughly 60–90 days with focused execution—covering application, "
        "procedures, systems integration, and operator approval.",

    "what documents required for ftz operations":
        "Typical items include inventory control procedures, zone admission documentation, weekly entry processes, "
        "audit trails, and standard operating procedures aligned to apparel workflows.",

    "how does weekly entry work benefits":
        "Weekly entry consolidates multiple shipments into one customs entry per week—significantly reducing MPF exposure "
        "and admin friction while maintaining compliance.",

    "difference ftz vs bonded warehouse":
        "A bonded warehouse defers duty until withdrawal but lacks FTZ’s weekly entry and manufacturing/processing flexibility. "
        "FTZs also support re-exports without duty and better align to omnichannel inventory strategies.",

    "can we export from ftz without paying duty":
        "Yes. Goods exported directly from the FTZ typically avoid U.S. duty; duty applies only when goods enter "
        "U.S. commerce. Off-spec/returns relief may also apply per regulations.",

    "how big are savings mpf hmf duty examples":
        "Savings come from three levers: export/off-spec duty relief, MPF reduction via weekly entry, and optimized broker/HMF handling. "
        "Exact impact depends on your shipments/week, average import value, duty rate, and export/off-spec mix."

}

# ✅ Add starter FTZ FAQs without changing existing ones
faq_qa.update({
    "what is an ftz foreign trade zone":
        "A Foreign-Trade Zone (FTZ) is a secured area under U.S. Customs supervision where imported goods "
        "can be stored, processed, or re-exported with deferral, reduction, or elimination of customs duties.",

    "who qualifies for an ftz apparel brand":
        "Importers who regularly bring merchandise into the U.S. and manage inventory benefit most—especially "
        "apparel brands with multi-channel flows (DTC, wholesale, marketplaces) and material export or off-spec volumes.",

    "how long does ftz activation take timeline":
        "Most brands can activate and go live in roughly 60–90 days with focused execution—covering application, "
        "procedures, systems integration, and operator approval.",

    "what documents required for ftz operations":
        "Typical items include inventory control procedures, zone admission documentation, weekly entry processes, "
        "audit trails, and standard operating procedures aligned to apparel workflows.",

    "how does weekly entry work benefits":
        "Weekly entry consolidates multiple shipments into one customs entry per week—significantly reducing MPF exposure "
        "and admin friction while maintaining compliance.",

    "difference ftz vs bonded warehouse":
        "A bonded warehouse defers duty until withdrawal but lacks FTZ’s weekly entry and manufacturing/processing flexibility. "
        "FTZs also support re-exports without duty and better align to omnichannel inventory strategies.",

    "can we export from ftz without paying duty":
        "Yes. Goods exported directly from the FTZ typically avoid U.S. duty; duty applies only when goods enter "
        "U.S. commerce. Off-spec/returns relief may also apply per regulations.",

    "how big are savings mpf hmf duty examples":
        "Savings come from three levers: export/off-spec duty relief, MPF reduction via weekly entry, and optimized broker/HMF handling. "
        "Exact impact depends on your shipments/week, average import value, duty rate, and export/off-spec mix."
})

faq_keys = list(faq_qa.keys())

import difflib

def match_question(q):
    m = difflib.get_close_matches(q.lower(), faq_keys, 1, 0.55)
    return faq_qa[m[0]] if m else None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

q = st.text_input("Ask a question about FTZ:")

# --- Starter questions (chips) shown under the input field ---
st.markdown("<div style='color:#475569; font-size:13px; margin:6px 0 4px 0;'>Try one of these:</div>", unsafe_allow_html=True)


starter_map = [
    ("What is Foreign Trade Zone?", "what is an ftz foreign trade zone"),
    ("Who qualifies for an FTZ (apparel)?", "who qualifies for an ftz apparel brand"),
    ("How does weekly entry reduce MPF?", "how does weekly entry work benefits"),
    ("Do savings hit cash flow immediately?", "direct cash flow savings immediate not deferral"),
    ("How are these numbers calculated?", "how are numbers calculated"),

    #("FTZ vs bonded warehouse — what's different?", "difference ftz vs bonded warehouse"),
    ("Can we export from an FTZ without duty?", "can we export from ftz without paying duty"),
    ("How big can the savings be?", "how big are savings mpf hmf duty examples"),
]

# Render as small buttons (chips) in a few columns
cols = st.columns(7)
for i, (label, keyname) in enumerate(starter_map):
    with cols[i % 7]:
        if st.button(label, key=f"starter_{i}"):
            ans = faq_qa.get(keyname) or match_question(label)
            if not ans:
                # keep your existing logging behavior when nothing matches
                log_to_google_sheets({
                    "session_id": st.session_state.session_id,
                    "net_savings": net_savings_to_brand,
                    "cost_with_ftz": total_cost_with_ftz,
                    "cost_without_ftz": total_cost_without_ftz,
                    "chat_question": label,
                })
                ans = "Thank you for your question, Your question will be directed to the Customer Success Lead at MAS US Holdings at oscarc@masholdings.com."
            st.session_state.chat_history.append(("You", label))
            st.session_state.chat_history.append(("AI", ans))


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
# st.markdown("""
# **Disclaimer:**  
# This calculator provides directional estimates only and does not constitute financial,
# legal, or compliance advice. If you need further details, book a free consultation
# """)
st.markdown(
    """
    <div style="margin-top:8px; color:#6b7280; font-size:14px;">
      <span style="color:#9ca3af;">*</span>
      <em>
        **Disclaimer:** 
        This calculator provides directional estimates only and does not constitute financial, legal, or compliance advice. If you need further details, book a free consultation
      </em>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")