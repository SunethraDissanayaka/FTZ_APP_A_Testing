# pages/1_Show_Details.py
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
#from utils import calculate_summary  # optional

# ---------------------------------------------------------
# PAGE CONFIG (put first)
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="FTZ Savings — Details")

# if "details" not in st.session_state:
#     st.warning("Please configure assumptions on the main page first.")
#     st.stop()
# ---------------------------------------------------------
# NAV: Back to Main Page (keeps your session-state nav)
# ---------------------------------------------------------
def _go_main():
    st.session_state["nav_target"] = "main"

st.button("⬅ Back to Main Page", on_click=_go_main)
if st.session_state.get("nav_target") == "main":
    st.switch_page("app.py")

# ---------------------------------------------------------
# HIDE SIDEBAR COMPLETELY
# ---------------------------------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}
[data-testid="collapsedControl"] {display:none;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SEED DEFAULTS (same as app.py; safe no-op if already set)
# ---------------------------------------------------------
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

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# >>> LIVE INSIGHTS (sticky toggle for insights visibility)
if "show_insights" not in st.session_state:
    st.session_state.show_insights = False

# >>> LIVE UPDATE: force rerun on any input change (helps some setups)
# Trigger a rerun when any input changes
def mark_dirty():
    st.session_state["_dirty"] = True

for k, v in FTZ_CONSTS.items():
    st.session_state[k] = v

# Remove No-FTZ operating costs from the model entirely
for k in ["noftz_consult", "noftz_mgmt", "noftz_software", "noftz_bond"]:
    st.session_state[k] = 0.0

# ---------------------------------------------------------
# MONEY FORMATTERS
# ---------------------------------------------------------
def money_fmt_val(x):
    try:
        x = float(x)
    except:
        return x
    return f"(${abs(x):,.0f})" if x < 0 else f"${x:,.0f}"

def money_fmt(x):
    try:
        x = float(x)
    except (ValueError, TypeError):
        return x
    return f"(${abs(x):,.0f})" if x < 0 else f"${x:,.0f}"

# ---------------------------------------------------------
# INPUTS (EDITABLE + SYNCED; no manual assignment to session_state)
# ---------------------------------------------------------
left, right = st.columns([1.25, 1.55])

with left:
    st.markdown("<h4 style='color:#0f172a;'>Customer Data Assumptions</h4>", unsafe_allow_html=True)

    # r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
    # r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns(5)

    # r1c1.number_input("Shipments / Week", min_value=1, key="shipments_per_week", on_change=mark_dirty)
    # r1c2.number_input("Avg Import Value ($)", min_value=1000, step=1000, key="avg_import_value", on_change=mark_dirty)
    # r1c3.number_input("Export %", min_value=0, max_value=100, step=1, key="export_pct", on_change=mark_dirty)
    # r1c4.number_input("Off-Spec %", min_value=0.0, max_value=100.0, step=0.01, key="offspec_pct", on_change=mark_dirty)
    # r1c5.number_input("Avg Duty %", min_value=0.0, max_value=100.0, step=0.1, key="duty_pct", on_change=mark_dirty)


    # r2c1.number_input("MPF %", key="mpf_pct", disabled=True)
    # r2c2.number_input("HMF %", key="hmf_pct", disabled=True)
    # r2c3.number_input("Broker Cost ($/entry)", key="broker_cost", on_change=mark_dirty)
    # r2c4.number_input("Cost of Capital %", key="current_interest_rate", on_change=mark_dirty)
    # r2c5.number_input("Avg Stock Holding Days", key="avg_stock_holding_days", help=(
    #     "(360/Inv Turns) or Days of Supply 0r (Months of Supply * 30)"
    # ), on_change=mark_dirty,step=1)
    # Row 1 (3)
    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.number_input("Shipments / Week", min_value=1, key="shipments_per_week", on_change=mark_dirty)
    r1c2.number_input("Avg Import Value ($)", min_value=1000, step=1000, key="avg_import_value", on_change=mark_dirty)
    r1c3.number_input("Export %", min_value=0, max_value=100, step=1, key="export_pct", on_change=mark_dirty)

    # Row 2 (4)
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.number_input("Off-Spec %", min_value=0.0, max_value=100.0, step=0.01, key="offspec_pct", on_change=mark_dirty)
    r2c2.number_input("Avg Duty %", min_value=0.0, max_value=100.0, step=0.1, key="duty_pct", on_change=mark_dirty)
    r2c3.number_input("MPF %", key="mpf_pct", disabled=True)
    r2c4.number_input("HMF %", key="hmf_pct", disabled=True)

    # Row 3 (3)
    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.number_input("Broker Cost ($/entry)", key="broker_cost", on_change=mark_dirty)
    r3c2.number_input("Cost of Capital %", key="current_interest_rate", on_change=mark_dirty)
    r3c3.number_input(
        "Avg Stock Holding Days",
        key="avg_stock_holding_days",
        help="(360/Inv Turns) or Days of Supply or (Months of Supply * 30)",
        on_change=mark_dirty,
        step=1,
    )

    # st.markdown("<h4 style='color:#0f172a;'>Costs With FTZ</h4>", unsafe_allow_html=True)
    # c1, c2, c3, c4 = st.columns(4)
    # c1.number_input("FTZ Consulting ($)", key="ftz_consult", step=1,on_change=mark_dirty)
    # c2.number_input("FTZ Management ($)", key="ftz_mgmt",step=1, on_change=mark_dirty)
    # c3.number_input("FTZ Software Fee ($)", key="ftz_software", step=1,on_change=mark_dirty)
    # c4.number_input("FTZ Operator Bond ($)", key="ftz_bond",step=1, on_change=mark_dirty)


    # st.markdown("<h4 style='color:#0f172a;'>Costs Without FTZ</h4>", unsafe_allow_html=True)
    # n1, n2, n3, n4 = st.columns(4)
    # n1.number_input("Consulting (No FTZ)", key="noftz_consult",step=1, on_change=mark_dirty)
    # n2.number_input("Management (No FTZ)", key="noftz_mgmt", step=1, on_change=mark_dirty)
    # n3.number_input("Software (No FTZ)", key="noftz_software", step=1,on_change=mark_dirty)
    # n4.number_input("Operator Bond (No FTZ)", key="noftz_bond",step=1, on_change=mark_dirty)


    # Rerun if _dirty is set
    if st.session_state.pop("_dirty", False):
        st.rerun()
        # ---------------------------------------------------------
# BIND LOCALS FOR CALCULATIONS (read from session_state)
# ---------------------------------------------------------
shipments_per_week     = st.session_state["shipments_per_week"]
avg_import_value       = st.session_state["avg_import_value"]
mpf_pct                = st.session_state["mpf_pct"]
hmf_pct                = st.session_state["hmf_pct"]
duty_pct               = st.session_state["duty_pct"]
export_pct             = st.session_state["export_pct"]
offspec_pct            = st.session_state["offspec_pct"]
broker_cost            = st.session_state["broker_cost"]
current_interest_rate  = st.session_state["current_interest_rate"]
avg_stock_holding_days = st.session_state["avg_stock_holding_days"]

ftz_consult  = st.session_state["ftz_consult"]
ftz_mgmt     = st.session_state["ftz_mgmt"]
ftz_software = st.session_state["ftz_software"]
ftz_bond     = st.session_state["ftz_bond"]

noftz_consult  = st.session_state["noftz_consult"]
noftz_mgmt     = st.session_state["noftz_mgmt"]
noftz_software = st.session_state["noftz_software"]
noftz_bond     = st.session_state["noftz_bond"]

# ---------------------------------------------------------
# CALCULATIONS (same as main app)
# ---------------------------------------------------------
ftz_consult  = st.session_state["ftz_consult"]
ftz_mgmt     = st.session_state["ftz_mgmt"]
ftz_software = st.session_state["ftz_software"]
ftz_bond     = st.session_state["ftz_bond"]

# No-FTZ op costs removed
noftz_consult  = 0.0
noftz_mgmt     = 0.0
noftz_software = 0.0
noftz_bond     = 0.0

export_sales = export_pct / 100
off_spec     = offspec_pct / 100
mpf_rate     = mpf_pct / 100
hmf_rate     = hmf_pct / 100
avg_duty     = duty_pct / 100

total_import_value   = shipments_per_week * avg_import_value * 52
total_duty           = total_import_value * avg_duty
duty_saved_export    = total_import_value * export_sales * avg_duty
duty_saved_offspec   = total_import_value * off_spec * avg_duty

entries_year   = shipments_per_week * 52
per_entry_mpf  = min(avg_import_value * mpf_rate, 634.62)
mpf_no_ftz     = per_entry_mpf * entries_year
mpf_with_ftz   = min(shipments_per_week * avg_import_value * mpf_rate, 634.62) * 52

broker_no_ftz  = entries_year * broker_cost + shipments_per_week * avg_import_value * hmf_rate
broker_ftz     = 52 * broker_cost + shipments_per_week * avg_import_value * hmf_rate

noftz_ops = 0
ftz_ops   = ftz_consult + ftz_mgmt + ftz_software + ftz_bond

# Working capital
interest_rate            = current_interest_rate / 100
total_net_duty_no_ftz    = total_duty
total_net_duty_with_ftz  = total_duty - duty_saved_export - duty_saved_offspec
deferred_duty_amount     = total_net_duty_with_ftz
#total_wc_saving          = deferred_duty_amount * interest_rate * (avg_stock_holding_days / 365)
total_wc_saving = ((total_duty+ mpf_with_ftz)* interest_rate* (avg_stock_holding_days / 365))

total_no_ftz = total_duty + mpf_no_ftz + broker_no_ftz + noftz_ops
total_ftz    = (total_duty - duty_saved_export - duty_saved_offspec) + mpf_with_ftz + broker_ftz + ftz_ops
net_savings  = total_no_ftz - total_ftz

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>Key Metrics</h4>", unsafe_allow_html=True)
k1, k2, k3, k4,k5 = st.columns(5)
k1.metric("Total Duty Baseline", money_fmt(total_duty))
k2.metric("Cost Without FTZ",  money_fmt(total_no_ftz))
k3.metric("Cost With FTZ",     money_fmt(total_ftz))
k4.metric("Net Savings",       money_fmt(net_savings))
k5.metric("Working Capital Savings",       money_fmt(total_wc_saving))

# =========================================================
# FTZ COST COMPARISON — FULL TABLE
# =========================================================
with right:
    st.markdown("<h4 style='color:#0f172a;'>FTZ Cost Comparison</h4>", unsafe_allow_html=True)

    def money_fmt_tbl(x):
        try:
            x = float(x)
        except:
            return ""
        return f"(${abs(x):,.0f})" if x < 0 else f"${x:,.0f}"

    def color_negative(v):
        try:
            return "color: red;" if float(v) < 0 else ""
        except:
            return ""

    entries_per_year = shipments_per_week * 52
    total_import_value = shipments_per_week * avg_import_value * 52

    total_duty = total_import_value * avg_duty
    duty_saved_export = total_import_value * export_sales * avg_duty
    duty_saved_offspec = total_import_value * off_spec * avg_duty

    net_duty_no_ftz  = total_duty
    net_duty_with_ftz = total_duty - duty_saved_export - duty_saved_offspec

    per_entry_mpf = min(avg_import_value * mpf_rate, 634.62)
    mpf_no_ftz = per_entry_mpf * entries_per_year
    mpf_with_ftz = min(shipments_per_week * avg_import_value * mpf_rate, 634.62) * 52

    broker_hmf_no_ftz  = entries_per_year * broker_cost + shipments_per_week * avg_import_value * hmf_rate
    broker_hmf_with_ftz = 52 * broker_cost + shipments_per_week * avg_import_value * hmf_rate

    operating_no_ftz = noftz_consult + noftz_mgmt + noftz_software + noftz_bond
    operating_ftz    = ftz_consult + ftz_mgmt + ftz_software + ftz_bond

    totals_no_ftz   = net_duty_no_ftz + mpf_no_ftz + broker_hmf_no_ftz
    totals_with_ftz = net_duty_with_ftz + mpf_with_ftz + broker_hmf_with_ftz

    total_cost_no_ftz = totals_no_ftz + operating_no_ftz
    total_cost_ftz    = totals_with_ftz + operating_ftz

    net_savings_tbl = total_cost_no_ftz - total_cost_ftz

    df = pd.DataFrame({
        "Category": [
            "Total Duty",
            "Duty Saved of Exported Goods",
            "Duty Saved on Non-Spec Goods",
            "Total Net Duty",
            "Total MPF",
            "Total Broker Costs + HMF",
            "Totals",
            #"FTZ Consulting",
            #"FTZ Management",
            #"FTZ Software Fee",
            #"FTZ Operator Bond",
            "Total Operating Costs",
            "Total Working Capital Saving",
            "Net Savings to Brand",
        ],
        "Without FTZ ($)": [
            total_duty, 0, 0, total_net_duty_no_ftz,
            mpf_no_ftz, broker_hmf_no_ftz, totals_no_ftz,
            #noftz_consult, noftz_mgmt, noftz_software, noftz_bond,
            operating_no_ftz,
            0,
            total_cost_no_ftz,
        ],
        "With FTZ ($)": [
            total_duty, -duty_saved_export, -duty_saved_offspec,
            total_net_duty_with_ftz, mpf_with_ftz, broker_hmf_with_ftz,
            totals_with_ftz,
            #ftz_consult, ftz_mgmt, ftz_software, ftz_bond,
            operating_ftz,
            #total_wc_saving,
            0,
            total_cost_ftz,
        ],
        "FTZ Savings ($)": [
            0,
            duty_saved_export,
            duty_saved_offspec,
            total_net_duty_no_ftz - total_net_duty_with_ftz,
            mpf_no_ftz - mpf_with_ftz,
            broker_hmf_no_ftz - broker_hmf_with_ftz,
            totals_no_ftz - totals_with_ftz,
            #noftz_consult - ftz_consult,
            #noftz_mgmt - ftz_mgmt,
            #noftz_software - ftz_software,
            #noftz_bond - ftz_bond,
            operating_no_ftz - operating_ftz,
            total_wc_saving,
            net_savings_tbl,
        ],
    })

    styled_table = (
        df.style
        .format(money_fmt_tbl, subset=["Without FTZ ($)", "With FTZ ($)", "FTZ Savings ($)"])
        .applymap(color_negative, subset=["Without FTZ ($)", "With FTZ ($)", "FTZ Savings ($)"])
        .set_properties(**{"font-size": "12px", "padding": "4px"})
        .hide(axis="index")
    )
    st.dataframe(styled_table, use_container_width=True, height=400)

# =========================================================
# AI INSIGHTS ASSISTANT
# =========================================================
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>AI Insights Assistant</h4>", unsafe_allow_html=True)

see_insights = st.button("🔍 See Insights")
if see_insights:
    roi_pct = (net_savings / ftz_ops * 100) if ftz_ops else 0
    monthly_savings = net_savings / 12 if net_savings else 0
    payback_months = (ftz_ops / monthly_savings) if monthly_savings > 0 else 0
    savings_pct = (net_savings / total_no_ftz * 100) if total_no_ftz else 0

    insights_html = (
        "<div style='background:#f8fafc;padding:24px;border-radius:12px;border:1px solid #e5e7eb;margin-top:18px;'>"
        "<h2 style='color:#0f172a;margin-bottom:8px;'>FTZ Savings Summary Report</h2>"
        "<h3 style='color:#1e293b;margin-top:14px;'>FTZ Savings Summary</h3>"
        f"<p style='color:#1f2937;font-size:14px;line-height:1.6;'>"
        f"<strong>Entries per year:</strong> {entries_year}<br>"
        f"<strong>Annual import value:</strong> {money_fmt_val(total_import_value)}<br>"
        f"<strong>Total Duty Baseline:</strong> {money_fmt_val(total_duty)}<br>"
        f"<strong>Total Duty Saved:</strong> {money_fmt_val(duty_saved_export + duty_saved_offspec)}<br><br>"
        f"<strong>MPF no-FTZ:</strong> {money_fmt_val(mpf_no_ftz)}, "
        f"<strong>MPF with FTZ:</strong> {money_fmt_val(mpf_with_ftz)}<br>"
        f"<strong>Broker + HMF no-FTZ:</strong> {money_fmt_val(broker_no_ftz)}, "
        f"<strong>with FTZ:</strong> {money_fmt_val(broker_ftz)}<br><br>"
        f"<strong>Fully-loaded cost WITHOUT FTZ:</strong> {money_fmt_val(total_no_ftz)}<br>"
        f"<strong>Fully-loaded cost WITH FTZ:</strong> {money_fmt_val(total_ftz)}<br>"
        f"<strong>Net Savings to Brand:</strong> "
        f"<span style='color:{'#16a34a' if net_savings >= 0 else '#dc2626'};'>{money_fmt_val(net_savings)}</span>"
        "</p>"
        "<h3 style='color:#1e293b;margin-top:18px;'>Key Drivers and Recommendations</h3>"
        "<ul style='color:#1f2937;font-size:14px;line-height:1.6;'>"
        f"<li>Duty saved (exports + non-spec): {money_fmt_val(duty_saved_export + duty_saved_offspec)}"
        "<ul>"
        f"<li>Export duty saved: {money_fmt_val(duty_saved_export)}</li>"
        f"<li>Non-spec duty saved: {money_fmt_val(duty_saved_offspec)}</li>"
        "</ul></li>"
        f"<li>MPF savings: {money_fmt_val(mpf_no_ftz - mpf_with_ftz)}</li>"
        f"<li>Broker + HMF savings: {money_fmt_val(broker_no_ftz - broker_ftz)}</li>"
        f"<li>Operating cost difference (No FTZ - FTZ): {money_fmt_val(noftz_ops - ftz_ops)}</li>"
        "</ul>"
        "<h3 style='color:#1e293b;margin-top:18px;'>Totals</h3>"
        "<ul style='color:#1f2937;font-size:14px;'>"
        f"<li>Fully-loaded cost WITHOUT FTZ: {money_fmt_val(total_no_ftz)}</li>"
        f"<li>Fully-loaded cost WITH FTZ: {money_fmt_val(total_ftz)}</li>"
        f"<li>Savings percentage: {savings_pct:.2f}%</li>"
        "</ul>"
        "<h3 style='color:#1e293b;margin-top:18px;'>Business Interpretation & Recommendations</h3>"
        "<ul style='color:#1f2937;font-size:14px;line-height:1.6;'>"
        "<li>MPF consolidation and higher export percentages materially increase FTZ value.</li>"
        "<li>If FTZ operating costs outweigh savings, consider consolidation or renegotiating program fees.</li>"
        "<li>Recommended next steps: HTS/SKU validation, scenario sensitivity testing, and a consultative feasibility review.</li>"
        "</ul>"
        "<h3 style='color:#1e293b;margin-top:18px;'>ROI & Payback</h3>"
        "<ul style='color:#1f2937;font-size:14px;'>"
        f"<li>ROI: {roi_pct:.2f}%</li>"
        f"<li>Payback Period: {payback_months:.1f} months</li>"
        "</ul>"
        "</div>"
    )
    st.markdown(insights_html, unsafe_allow_html=True)
    st.session_state["ai_insights_report"] = insights_html

# ---------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>Report Download</h4>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    excel = BytesIO()
    pd.DataFrame(df).to_excel(excel, index=False)
    st.download_button("📊 Download Excel", excel.getvalue(), "FTZ_Details.xlsx")

with c2:
    if "ai_insights_report" not in st.session_state:
        st.warning("Please click 'See Insights' before downloading the PDF.")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FTZ Savings Summary Report", ln=True, align="C")
        pdf.ln(6)
        pdf.set_font("Arial", size=11)
        clean_text = (
            f"FTZ Savings Summary\n\n"
            f"Entries per year: {entries_year}\n"
            f"Annual import value: {money_fmt_val(total_import_value)}\n"
            f"Total Duty Baseline: {money_fmt_val(total_duty)}\n"
            f"Total Duty Saved: {money_fmt_val(duty_saved_export + duty_saved_offspec)}\n\n"
            f"MPF no-FTZ: {money_fmt_val(mpf_no_ftz)}, MPF with FTZ: {money_fmt_val(mpf_with_ftz)}\n"
            f"Broker + HMF no-FTZ: {money_fmt_val(broker_no_ftz)}, with FTZ: {money_fmt_val(broker_ftz)}\n\n"
            f"Fully-loaded cost WITHOUT FTZ: {money_fmt_val(total_no_ftz)}\n"
            f"Fully-loaded cost WITH FTZ: {money_fmt_val(total_ftz)}\n"
            f"Net Savings to Brand: {money_fmt_val(net_savings)}\n\n"
            f"ROI: {((net_savings / ftz_ops) * 100):.2f}%\n"
            f"Payback Period: {(ftz_ops / (net_savings / 12)):.1f} months\n\n"

            f"Key Drivers:\n"
            f"- Duty saved (exports + non-spec): {money_fmt_val(duty_saved_export + duty_saved_offspec)}\n"
            f"  - Export duty saved: {money_fmt_val(duty_saved_export)}\n"
            f"  - Non-spec duty saved: {money_fmt_val(duty_saved_offspec)}\n"
            f"- MPF savings: {money_fmt_val(mpf_no_ftz - mpf_with_ftz)}\n"
            f"- Broker + HMF savings: {money_fmt_val(broker_no_ftz - broker_ftz)}\n"
            f"- Operating cost difference (No FTZ - FTZ): {money_fmt_val(noftz_ops - ftz_ops)}\n\n"

            f"Totals:\n"
            f"- Fully-loaded cost WITHOUT FTZ: {money_fmt_val(total_no_ftz)}\n"
            f"- Fully-loaded cost WITH FTZ: {money_fmt_val(total_ftz)}\n"
            f"- Savings percentage vs baseline: {(net_savings / total_no_ftz * 100):.2f}%\n\n"

            f"Business Interpretation & Recommendations:\n"
            f"- MPF consolidation and higher export percentages materially increase FTZ value.\n"
            f"- If FTZ operating costs outweigh savings, consider consolidation or renegotiating program fees.\n"
            f"- Recommended next steps: HTS/SKU validation, scenario sensitivity testing, "
            f"and a consultative feasibility review."
        )
        pdf.multi_cell(0, 7, clean_text)
        st.download_button(
            label="📄 Download PDF",
            data=pdf.output(dest="S").encode("latin-1", "replace"),
            file_name="FTZ_Insights_Report.pdf",
            mime="application/pdf",
        )

# ---------------------------------------------------------
# METHODOLOGY (unchanged text)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>Calculations & Methodology</h4>", unsafe_allow_html=True)

with st.expander("📦 Shipment Volume & Import Value"):
    st.markdown("""
**Entries per Year**  
`Entries per Year = Shipments per Week × 52`

**Annual Import Value**  
`Annual Import Value = Shipments per Week × Average Import Value × 52`
""")

with st.expander("💰 Duty Calculations"):
    st.markdown("""
**Total Duty Baseline (No FTZ)**  
`Total Duty = Annual Import Value × Average Duty %`

**Duty Saved on Exports**  
`Export Duty Saved = Annual Import Value × Export % × Average Duty %`

**Duty Saved on Non-Spec Goods**  
`Non-Spec Duty Saved = Annual Import Value × Off-Spec % × Average Duty %`

**Net Duty With FTZ**  
`Net Duty (FTZ) = Total Duty − Export Duty Saved − Non-Spec Duty Saved`
""")

with st.expander("🧾 MPF (Merchandise Processing Fee)"):
    st.markdown("""
**Per-Entry MPF**  
`Per Entry MPF = min(Average Import Value × MPF %, $634.62)`

**MPF Without FTZ**  
`MPF (No FTZ) = Per Entry MPF × Entries per Year`

**MPF With FTZ (Weekly Entry)**  
`MPF (FTZ) = min(Shipments per Week × Avg Import Value × MPF %, $634.62) × 52`
""")

with st.expander("🚢 Broker & Harbor Maintenance Fees (HMF)"):
    st.markdown("""
**Broker + HMF Without FTZ**  
`Broker/HMF (No FTZ) = (Entries per Year × Broker Cost) + (Shipments per Week × Avg Import Value × HMF %)`  

**Broker + HMF With FTZ**  
`Broker/HMF (FTZ) = (52 × Broker Cost) + (Shipments per Week × Avg Import Value × HMF %)`
""")

with st.expander("🏭 Operating Costs"):
    st.markdown("""
**Operating Costs Without FTZ**  
`No-FTZ Operating Costs = Consulting + Management + Software + Bond`  

**Operating Costs With FTZ**  
`FTZ Operating Costs = FTZ Consulting + FTZ Management + FTZ Software + FTZ Bond`
""")

with st.expander("🏦 Working Capital (WC) Savings"):
    st.markdown("""
**Deferred Duty Amount**  
`Deferred Duty = Net Duty With FTZ`  

**Total Working Capital Savings**  
`WC Savings = Deferred Duty × Interest Rate × (Avg Stock Holding Days ÷ 365)`
""")

with st.expander("📊 Total Cost Comparison"):
    st.markdown("""
**Total Cost Without FTZ**  
`Total Cost (No FTZ) = Duty + MPF + Broker/HMF + No-FTZ Operating Costs`  

**Total Cost With FTZ**  
`Total Cost (FTZ) = Net Duty + MPF (FTZ) + Broker/HMF (FTZ) + FTZ Operating Costs − WC Savings`
""")

with st.expander("🏷 Net Savings Calculation"):
    st.markdown("""
**Net Savings to Brand**  
`Net Savings = Total Cost (No FTZ) − Total Cost (FTZ)`
""")

with st.expander("📈 ROI & Payback Period"):
    st.markdown("""
**ROI (%)**  
`ROI = (Net Savings ÷ FTZ Operating Costs) × 100`  

**Monthly Savings**  
`Monthly Savings = Net Savings ÷ 12`  

**Payback (Months)**  
`Payback = FTZ Operating Costs ÷ Monthly Savings`
""")

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