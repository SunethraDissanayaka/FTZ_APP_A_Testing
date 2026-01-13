import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
#from streamlit.components.v1 import html as st_html
import streamlit as st

# ---------------------------------------------------------
# BACK TO MAIN PAGE BUTTON
# ---------------------------------------------------------
if st.button("⬅ Back to Main Page"):
    st.switch_page("app.py")

# ---------------------------------------------------------
# PAGE CONFIG (Details Page)
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="FTZ Savings — Details")

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
# MONEY FORMATTER
# ---------------------------------------------------------
def money_fmt_val(x):
    try:
        x = float(x)
    except:
        return x
    if x < 0:
        return f"(${abs(x):,.0f})"
    return f"${x:,.0f}"

def money_fmt(x):
    try:
        x = float(x)
    except (ValueError, TypeError):
        return x  # leave strings untouched

    if x < 0:
        return f"(${abs(x):,.0f})"
    return f"${x:,.0f}"



# ---------------------------------------------------------
# INPUTS (Same 16 Inputs)
# ---------------------------------------------------------
left, right = st.columns([1.25, 1.55])

with left:
#     #st.markdown("### Customer Data Assumptions")
#     st.markdown("<h4 style='color:#0f172a;'>Customer Data Assumptions</h4>", unsafe_allow_html=True)

#     c1, c2, c3, c4 = st.columns(4)

#     with c1:
#         shipments_per_week = st.number_input("Shipments / Week", min_value=1, value=2)
#         export_sales_pct = st.number_input("Export Sales (%)", 0.0, 100.0, 1.0)

#     with c2:
#         avg_import_value = st.number_input("Avg Import Value ($)", 1000, value=50000, step=1000)
#         off_spec_pct = st.number_input("Off-Spec (%)", 0.0, 100.0, 0.25)

#     with c3:
#         mpf_pct = st.number_input("MPF %", 0.0, 100.0, 0.35)
#         hmf_pct = st.number_input("HMF %", 0.0, 100.0, 0.13)

#     with c4:
#         broker_cost = st.number_input("Broker Cost ($/entry)", value=125.0)
#         avg_duty_pct = st.number_input("Avg Duty %", 0.0, 100.0, 30.0)

    st.markdown("### Customer Data Assumptions")

    r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
    r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns(5)

    with r1c1:
        shipments_per_week = st.number_input("Shipments / Week", min_value=1, value=2)

    with r1c2:
        avg_import_value = st.number_input("Avg Import Value", min_value=1000, value=50000, step=1000)

    with r1c3:
        export_sales_pct = st.number_input("Export Sales (%)", 0.0, 100.0, 1.0)

    with r1c4:
        off_spec_pct = st.number_input("Off-Spec (%)", 0.0, 100.0, 0.25)

    with r1c5:
        avg_duty_pct = st.number_input("Avg Duty %", 0.0, 100.0, 30.0)

    with r2c1:
        mpf_pct = st.number_input("MPF %", value=0.35, disabled=True)

    with r2c2:
        hmf_pct = st.number_input("HMF %", value=0.13, disabled=True)

    with r2c3:
        broker_cost = st.number_input("Broker Cost ($/entry)", value=125.0)

    with r2c4:
        current_interest_rate = st.number_input(
            "Current Interest Rate (%)", value=6.5
        )

    with r2c5:
        avg_stock_holding_days = st.number_input(
            "Avg # Stock Holding Days", value=45
        )

    #st.markdown("### Costs With FTZ (Annual)")
    st.markdown("<h4 style='color:#0f172a;'>Costs With FTZ</h4>", unsafe_allow_html=True)

    w1, w2, w3, w4 = st.columns(4)
    ftz_consult = w1.number_input("FTZ Consulting", value=50000)
    ftz_mgmt = w2.number_input("FTZ Management", value=150000)
    ftz_software = w3.number_input("FTZ Software Fee", value=40000)
    ftz_bond = w4.number_input("FTZ Operator Bond", value=1000)

    #st.markdown("### Costs Without FTZ (Annual)")
    st.markdown("<h4 style='color:#0f172a;'>Costs Without FTZ</h4>", unsafe_allow_html=True)

    n1, n2, n3, n4 = st.columns(4)
    noftz_consult = n1.number_input("Consulting (No FTZ)", value=0)
    noftz_mgmt = n2.number_input("Management (No FTZ)", value=0)
    noftz_software = n3.number_input("Software (No FTZ)", value=0)
    noftz_bond = n4.number_input("Operator Bond (No FTZ)", value=0)

# ---------------------------------------------------------
# CALCULATIONS (same as full app)
# ---------------------------------------------------------
export_sales = export_sales_pct / 100
off_spec = off_spec_pct / 100
mpf_rate = mpf_pct / 100
hmf_rate = hmf_pct / 100
avg_duty = avg_duty_pct / 100

total_import_value = shipments_per_week * avg_import_value * 52
total_duty = total_import_value * avg_duty
duty_saved_export = total_import_value * export_sales * avg_duty
duty_saved_offspec = total_import_value * off_spec * avg_duty

entries_year = shipments_per_week * 52
per_entry_mpf = min(avg_import_value * mpf_rate, 634.62)

mpf_no_ftz = per_entry_mpf * entries_year
mpf_with_ftz = min(shipments_per_week * avg_import_value * mpf_rate, 634.62) * 52

broker_no_ftz = entries_year * broker_cost + shipments_per_week * avg_import_value * hmf_rate
broker_ftz = 52 * broker_cost + shipments_per_week * avg_import_value * hmf_rate

noftz_ops = noftz_consult + noftz_mgmt + noftz_software + noftz_bond
ftz_ops = ftz_consult + ftz_mgmt + ftz_software + ftz_bond

# ---------------------------------------------------------
# WORKING CAPITAL SAVINGS (DETAILS PAGE)
# ---------------------------------------------------------

interest_rate = current_interest_rate / 100
total_net_duty_no_ftz = total_duty
total_net_duty_with_ftz = (
    total_duty
    - duty_saved_export
    - duty_saved_offspec
)

deferred_duty_amount = total_net_duty_with_ftz

total_wc_saving = (
    deferred_duty_amount
    * interest_rate
    * (avg_stock_holding_days / 365)
)


total_no_ftz = total_duty + mpf_no_ftz + broker_no_ftz + noftz_ops
total_ftz = (total_duty - duty_saved_export - duty_saved_offspec) + mpf_with_ftz + broker_ftz + ftz_ops-total_wc_saving

net_savings = total_no_ftz - total_ftz

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
#st.markdown("### Key Metrics")
st.markdown("<h4 style='color:#0f172a;'>Key Metrics</h4>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Duty Baseline", money_fmt(total_duty))
k2.metric("Cost Without FTZ", money_fmt(total_no_ftz))
k3.metric("Cost With FTZ", money_fmt(total_ftz))
k4.metric("Net Savings", money_fmt(net_savings))



# =========================================================
# FTZ COST COMPARISON — FULL TABLE (DETAILS PAGE)
# =========================================================
with right:
    #st.markdown("### FTZ Cost Comparison")
    st.markdown("<h4 style='color:#0f172a;'>FTZ Cost Comparison</h4>", unsafe_allow_html=True)

#st.markdown("## FTZ Cost Comparison")

# ---------- Helper formatters ----------
    def money_fmt(x):
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

    # ---------- Core Calculations ----------
    export_sales = export_sales_pct / 100
    off_spec = off_spec_pct / 100
    mpf_rate = mpf_pct / 100
    hmf_rate = hmf_pct / 100
    avg_duty = avg_duty_pct / 100

    entries_per_year = shipments_per_week * 52
    total_import_value = shipments_per_week * avg_import_value * 52

    # Duty
    total_duty = total_import_value * avg_duty
    duty_saved_export = total_import_value * export_sales * avg_duty
    duty_saved_offspec = total_import_value * off_spec * avg_duty

    net_duty_no_ftz = total_duty
    net_duty_with_ftz = total_duty - duty_saved_export - duty_saved_offspec

    # MPF
    per_entry_mpf = min(avg_import_value * mpf_rate, 634.62)
    mpf_no_ftz = per_entry_mpf * entries_per_year
    mpf_with_ftz = min(shipments_per_week * avg_import_value * mpf_rate, 634.62) * 52

    # Broker + HMF
    broker_hmf_no_ftz = entries_per_year * broker_cost + shipments_per_week * avg_import_value * hmf_rate
    broker_hmf_with_ftz = 52 * broker_cost + shipments_per_week * avg_import_value * hmf_rate

    # Operating Costs
    operating_no_ftz = noftz_consult + noftz_mgmt + noftz_software + noftz_bond
    operating_ftz = ftz_consult + ftz_mgmt + ftz_software + ftz_bond

    # Totals
    totals_no_ftz = net_duty_no_ftz + mpf_no_ftz + broker_hmf_no_ftz
    totals_with_ftz = net_duty_with_ftz + mpf_with_ftz + broker_hmf_with_ftz

    total_cost_no_ftz = totals_no_ftz + operating_no_ftz
    total_cost_ftz = totals_with_ftz + operating_ftz-total_wc_saving

    net_savings = total_cost_no_ftz - total_cost_ftz

    # ---------- Build Table ----------
    # df = pd.DataFrame({
    #     "Category": [
    #         "Total Duty",
    #         "Duty Saved of Exported Goods",
    #         "Duty Saved on Non-Spec Goods",
    #         "Total Net Duty",
    #         "Total MPF",
    #         "Total Broker Costs + HMF",
    #         "Totals",
    #         "FTZ Consulting",
    #         "FTZ Management",
    #         "FTZ Software Fee",
    #         "FTZ Operator Bond",
    #         "Total Operating Costs",
    #         "Net Savings to Brand",
    #     ],
    #     "Without FTZ ($)": [
    #         total_duty, 0, 0, net_duty_no_ftz,
    #         mpf_no_ftz, broker_hmf_no_ftz, totals_no_ftz,
    #         noftz_consult, noftz_mgmt, noftz_software, noftz_bond,
    #         operating_no_ftz, total_cost_no_ftz
    #     ],
    #     "With FTZ ($)": [
    #         total_duty, -duty_saved_export, -duty_saved_offspec,
    #         net_duty_with_ftz, mpf_with_ftz, broker_hmf_with_ftz,
    #         totals_with_ftz,
    #         ftz_consult, ftz_mgmt, ftz_software, ftz_bond,
    #         operating_ftz, total_cost_ftz
    #     ],
    #     "FTZ Savings ($)": [
    #         0, duty_saved_export, duty_saved_offspec,
    #         net_duty_no_ftz - net_duty_with_ftz,
    #         mpf_no_ftz - mpf_with_ftz,
    #         broker_hmf_no_ftz - broker_hmf_with_ftz,
    #         totals_no_ftz - totals_with_ftz,
    #         noftz_consult - ftz_consult,
    #         noftz_mgmt - ftz_mgmt,
    #         noftz_software - ftz_software,
    #         noftz_bond - ftz_bond,
    #         operating_no_ftz - operating_ftz,
    #         net_savings
    #     ]
    # })

    # INSERT after "Total Operating Costs"
    df = pd.DataFrame({
        "Category": [
            "Total Duty",
            "Duty Saved of Exported Goods",
            "Duty Saved on Non-Spec Goods",
            "Total Net Duty",
            "Total MPF",
            "Total Broker Costs + HMF",
            "Totals",
            "FTZ Consulting",
            "FTZ Management",
            "FTZ Software Fee",
            "FTZ Operator Bond",
            "Total Operating Costs",
            "Total WC Saving",
            "Net Savings to Brand",
        ],
        "Without FTZ ($)": [
            total_duty, 0, 0, total_net_duty_no_ftz,
            mpf_no_ftz, broker_hmf_no_ftz, totals_no_ftz,
            noftz_consult, noftz_mgmt, noftz_software, noftz_bond,
            operating_no_ftz,
            0,
            total_cost_no_ftz,
        ],
        "With FTZ ($)": [
            total_duty, -duty_saved_export, -duty_saved_offspec,
            total_net_duty_with_ftz, mpf_with_ftz, broker_hmf_with_ftz,
            totals_with_ftz,
            ftz_consult, ftz_mgmt, ftz_software, ftz_bond,
            operating_ftz,
            -total_wc_saving,
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
            noftz_consult - ftz_consult,
            noftz_mgmt - ftz_mgmt,
            noftz_software - ftz_software,
            noftz_bond - ftz_bond,
            operating_no_ftz - operating_ftz,
            total_wc_saving,
            net_savings,
        ],
    })


    # ---------- Styled Render ----------
    styled_table = (
        df.style
        .format(money_fmt, subset=["Without FTZ ($)", "With FTZ ($)", "FTZ Savings ($)"])
        .applymap(color_negative, subset=["Without FTZ ($)", "With FTZ ($)", "FTZ Savings ($)"])
        .set_properties(**{"font-size": "12px", "padding": "4px"})
        .hide(axis="index")
    )

    st.dataframe(
        styled_table,
        use_container_width=True,
        height=500
    )




# =========================================================
# AI INSIGHTS ASSISTANT (FIXED VARIABLE MAPPING)
# =========================================================
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>AI Insights Assistant</h4>", unsafe_allow_html=True)

see_insights = st.button("🔍 See Insights")

if see_insights:

    # -------------------------
    # Derived metrics
    # -------------------------
    roi_pct = (net_savings / ftz_ops * 100) if ftz_ops else 0
    monthly_savings = net_savings / 12 if net_savings else 0
    payback_months = (ftz_ops / monthly_savings) if monthly_savings > 0 else 0
    savings_pct = (net_savings / total_no_ftz * 100) if total_no_ftz else 0

    # -------------------------
    # EXACT REPORT CONTENT (with live variables)
    # -------------------------
    insights_html = (
        "<div style='"
        "background:#f8fafc;"
        "padding:24px;"
        "border-radius:12px;"
        "border:1px solid #e5e7eb;"
        "margin-top:18px;"
        "'>"

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
        f"<span style='color:{'#16a34a' if net_savings >= 0 else '#dc2626'};'>"
        f"{money_fmt_val(net_savings)}</span>"
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
        f"<li>Operating cost difference (No FTZ - FTZ): "
        f"{money_fmt_val(noftz_ops - ftz_ops)}</li>"
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

    # Store for PDF export
    st.session_state["ai_insights_report"] = insights_html




# ---------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>Report Download</h4>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    excel = BytesIO()
    df.to_excel(excel, index=False)
    st.download_button("📊 Download Excel", excel.getvalue(), "FTZ_Details.xlsx")


with c2:

    if "ai_insights_report" not in st.session_state:
        st.warning("Please click 'See Insights' before downloading the PDF.")
    else:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FTZ Savings Summary Report", ln=True, align="C")
        pdf.ln(6)

        # Body text
        pdf.set_font("Arial", size=11)

        # Convert HTML-style content to clean text
        clean_text = (
            f"FTZ Savings Summary\n\n"
            f"Entries per year: {entries_year}\n"
            f"Annual import value: {money_fmt_val(total_import_value)}\n"
            f"Total Duty Baseline: {money_fmt_val(total_duty)}\n"
            f"Total Duty Saved: {money_fmt_val(duty_saved_export + duty_saved_offspec)}\n\n"

            f"MPF no-FTZ: {money_fmt_val(mpf_no_ftz)}, "
            f"MPF with FTZ: {money_fmt_val(mpf_with_ftz)}\n"
            f"Broker + HMF no-FTZ: {money_fmt_val(broker_no_ftz)}, "
            f"with FTZ: {money_fmt_val(broker_ftz)}\n\n"

            f"Fully-loaded cost WITHOUT FTZ: {money_fmt_val(total_no_ftz)}\n"
            f"Fully-loaded cost WITH FTZ: {money_fmt_val(total_ftz)}\n"
            f"Net Savings to Brand: {money_fmt_val(net_savings)}\n\n"

            f"ROI: {((net_savings / ftz_ops) * 100):.2f}%\n"
            f"Payback Period: "
            f"{(ftz_ops / (net_savings / 12)):.1f} months\n\n"

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

# =========================================================
# CALCULATIONS & METHODOLOGY
# =========================================================
st.markdown("---")
st.markdown("<h4 style='color:#0f172a;'>Calculations & Methodology</h4>", unsafe_allow_html=True)

st.markdown(
    "<p style='color:#0f172a; font-size:14px;'>"
    "The following formulas explain how each value in the FTZ Savings model is calculated. "
    "All calculations are based on your inputs and U.S. FTZ regulatory mechanics."
    "</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 1. Volume & Import Value
# ---------------------------------------------------------
with st.expander("📦 Shipment Volume & Import Value"):
    st.markdown("""
**Entries per Year**  
`Entries per Year = Shipments per Week × 52`

**Annual Import Value**  
`Annual Import Value = Shipments per Week × Average Import Value × 52`
""")

# ---------------------------------------------------------
# 2. Duty Calculations
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 3. MPF (Merchandise Processing Fee)
# ---------------------------------------------------------
with st.expander("🧾 MPF (Merchandise Processing Fee)"):
    st.markdown("""
**Per-Entry MPF (CBP Capped)**  
`Per Entry MPF = min(Average Import Value × MPF %, $634.62)`

**MPF Without FTZ**  
`MPF (No FTZ) = Per Entry MPF × Entries per Year`

**MPF With FTZ (Weekly Entry)**  
`MPF (FTZ) = min(Shipments per Week × Avg Import Value × MPF %, $634.62) × 52`
""")

# ---------------------------------------------------------
# 4. Broker & HMF Costs
# ---------------------------------------------------------
with st.expander("🚢 Broker & Harbor Maintenance Fees (HMF)"):
    st.markdown("""
**Broker + HMF Without FTZ**  
`Broker/HMF (No FTZ) = (Entries per Year × Broker Cost) + (Shipments per Week × Avg Import Value × HMF %)`

**Broker + HMF With FTZ**  
`Broker/HMF (FTZ) = (52 × Broker Cost) + (Shipments per Week × Avg Import Value × HMF %)`
""")

# ---------------------------------------------------------
# 5. Operating Costs
# ---------------------------------------------------------
with st.expander("🏭 Operating Costs"):
    st.markdown("""
**Operating Costs Without FTZ**  
`No-FTZ Operating Costs = Consulting + Management + Software + Bond`

**Operating Costs With FTZ**  
`FTZ Operating Costs = FTZ Consulting + FTZ Management + FTZ Software + FTZ Bond`
""")

# ---------------------------------------------------------
# 6. Working Capital (WC) Savings  ⭐ NEW
# ---------------------------------------------------------
with st.expander("🏦 Working Capital (WC) Savings"):
    st.markdown("""
**Deferred Duty Amount**  
`Deferred Duty = Net Duty With FTZ`

**Total Working Capital Savings**  
`WC Savings = Deferred Duty × Interest Rate × (Avg Stock Holding Days ÷ 365)`

This represents the financing benefit of deferring duty payments while inventory
remains in FTZ status.
""")

# ---------------------------------------------------------
# 6. Total Cost Comparison
# ---------------------------------------------------------
with st.expander("📊 Total Cost Comparison"):
    st.markdown("""
**Total Cost Without FTZ**  
`Total Cost (No FTZ) = Duty + MPF + Broker/HMF + No-FTZ Operating Costs`

**Total Cost With FTZ**  
`Total Cost (FTZ) = Net Duty + MPF (FTZ) + Broker/HMF (FTZ) + FTZ Operating Costs-WC Savings`
""")

# ---------------------------------------------------------
# 7. Net Savings
# ---------------------------------------------------------
with st.expander("🏷 Net Savings Calculation"):
    st.markdown("""
**Net Savings to Brand**  
`Net Savings = Total Cost (No FTZ) − Total Cost (FTZ)`
""")

# ---------------------------------------------------------
# 8. ROI & Payback
# ---------------------------------------------------------
with st.expander("📈 ROI & Payback Period"):
    st.markdown("""
**Return on Investment (ROI)**  
`ROI (%) = (Net Savings ÷ FTZ Operating Costs) × 100`

**Monthly Savings**  
`Monthly Savings = Net Savings ÷ 12`

**Payback Period**  
`Payback (Months) = FTZ Operating Costs ÷ Monthly Savings`
""")
