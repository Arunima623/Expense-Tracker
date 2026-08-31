"""
Streamlit Web Dashboard for Expense Tracker & Budget Manager.
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date
import os
import io

from core.expense_manager import ExpenseManager
from core.models import Expense


# Page Configuration
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize ExpenseManager
@st.cache_resource
def get_manager():
    return ExpenseManager(db_path="expenses.db")

manager = get_manager()

# Custom CSS styling for clean card UI
st.markdown("""
<style>
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1E293B;
        margin-top: 4px;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================================
# SIDEBAR: QUICK ACTIONS & CONFIG
# =========================================================================
with st.sidebar:
    st.title("💰 Expense Tracker")
    st.caption("Personal Finance & Budget Control")
    st.divider()

    # 1. Add Expense Form
    with st.expander("➕ **Add New Expense**", expanded=True):
        with st.form("add_expense_form", clear_on_submit=True):
            f_title = st.text_input("Title / Description", placeholder="e.g. Grocery Store")
            f_amount = st.number_input("Amount ($)", min_value=0.01, step=1.0, format="%.2f")
            
            categories = manager.get_categories()
            f_cat = st.selectbox("Category", options=categories if categories else ["Other"])
            f_date = st.date_input("Date", value=date.today())
            f_pm = st.selectbox("Payment Method", options=manager.get_payment_methods())
            f_notes = st.text_input("Notes (optional)", placeholder="e.g. Weekly shopping")

            submitted = st.form_submit_button("Record Expense", use_container_width=True)
            if submitted:
                if not f_title.strip():
                    st.error("Please enter a title.")
                else:
                    manager.add_expense(
                        title=f_title.strip(),
                        amount=f_amount,
                        category=f_cat,
                        expense_date=f_date.strftime("%Y-%m-%d"),
                        payment_method=f_pm,
                        notes=f_notes.strip()
                    )
                    st.success("✓ Expense added!")
                    st.rerun()

    # 2. Set Category Budget Form
    with st.expander("🎯 **Set Monthly Budget**"):
        with st.form("set_budget_form", clear_on_submit=True):
            b_cat = st.selectbox("Category", options=categories if categories else ["Other"], key="b_cat")
            b_month = st.text_input("Month (YYYY-MM)", value=date.today().strftime("%Y-%m"))
            b_limit = st.number_input("Budget Limit ($)", min_value=1.0, step=10.0, format="%.2f")

            b_submit = st.form_submit_button("Save Budget", use_container_width=True)
            if b_submit:
                try:
                    manager.set_budget(b_cat, b_month, b_limit)
                    st.success(f"✓ Budget for {b_cat} set to ${b_limit:,.2f}!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # 3. Category Manager
    with st.expander("🏷️ **Manage Categories**"):
        new_cat_name = st.text_input("New Category Name")
        if st.button("Add Category", use_container_width=True):
            if new_cat_name.strip():
                if manager.add_category(new_cat_name.strip()):
                    st.success(f"Added '{new_cat_name}'")
                    st.rerun()
                else:
                    st.warning("Category already exists.")

    # 4. Sample Demo Data Seeder
    st.divider()
    if st.button("🎲 Seed Demo Data", use_container_width=True, help="Load realistic demo transactions"):
        from sample_data import seed_sample_data
        seed_sample_data("expenses.db")
        st.success("Sample data loaded!")
        st.rerun()


# =========================================================================
# MAIN DASHBOARD CONTENT
# =========================================================================

# Month Selector
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.title("Financial Overview & Dashboard")
with col_header2:
    trends = manager.get_monthly_trends()
    available_months = [t["month"] for t in trends] if trends else []
    curr_month_str = date.today().strftime("%Y-%m")
    if curr_month_str not in available_months:
        available_months.append(curr_month_str)
    available_months.sort(reverse=True)

    selected_month = st.selectbox("Select Month", options=available_months, index=0)

# Fetch Monthly Report & Budget Alerts
report = manager.generate_monthly_report(selected_month)
alerts = manager.check_budget_alerts(selected_month)

# Display Budget Alerts
if alerts:
    for a in alerts:
        if a["status"] == "EXCEEDED":
            st.error(f"🚨 **Budget Alert**: {a['message']}")
        else:
            st.warning(f"⚠️ **Budget Warning**: {a['message']}")

# KPI Cards Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #2563EB;">
        <div class="metric-title">Total Spent ({selected_month})</div>
        <div class="metric-value">${report.total_spent:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    budget_label = f"${report.total_budget:,.2f}" if report.total_budget > 0 else "No Budget Set"
    budget_color = "#10B981" if report.total_budget == 0 or report.total_spent <= report.total_budget else "#EF4444"
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {budget_color};">
        <div class="metric-title">Total Budget</div>
        <div class="metric-value">{budget_label}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #F59E0B;">
        <div class="metric-title">Daily Average</div>
        <div class="metric-value">${report.daily_average:,.2f}/day</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #8B5CF6;">
        <div class="metric-title">Transactions</div>
        <div class="metric-value">{report.transaction_count} items</div>
    </div>
    """, unsafe_allow_html=True)


# Tabs for Analytics vs Transactions vs Budgeting
tab_analytics, tab_transactions, tab_budget_view = st.tabs([
    "📊 **Analytics & Charts**",
    "💳 **Transactions History**",
    "🎯 **Budget Tracking**"
])

# -------------------------------------------------------------
# TAB 1: ANALYTICS & VISUALIZATIONS
# -------------------------------------------------------------
with tab_analytics:
    chart_col1, chart_col2 = st.columns(2)

    # 1. Category Breakdown Donut / Bar Chart
    with chart_col1:
        st.subheader("Category Distribution")
        cat_summaries = report.category_summaries
        if cat_summaries:
            df_cat = pd.DataFrame([
                {"Category": s.category, "Amount": s.total_amount, "Percentage": s.percentage}
                for s in cat_summaries
            ])
            
            # Altair Donut Chart
            donut = alt.Chart(df_cat).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Amount", type="quantitative"),
                color=alt.Color(field="Category", type="nominal", legend=alt.Legend(orient="bottom")),
                tooltip=["Category", alt.Tooltip("Amount:Q", format="$.2f"), alt.Tooltip("Percentage:Q", format=".1f")]
            ).properties(height=320)
            
            st.altair_chart(donut, use_container_width=True)
        else:
            st.info("No expense data recorded for this month.")

    # 2. Daily Spending Trend
    with chart_col2:
        st.subheader("Daily Spending Trend")
        daily_data = manager.get_daily_spending(selected_month)
        if daily_data:
            df_daily = pd.DataFrame(daily_data)
            df_daily["date"] = pd.to_datetime(df_daily["date"])
            
            line_chart = alt.Chart(df_daily).mark_area(
                line={"color": "#2563EB"},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#2563EB', offset=0),
                           alt.GradientStop(color='rgba(37, 99, 235, 0.05)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X("date:T", title="Date", axis=alt.Axis(format="%b %d")),
                y=alt.Y("total:Q", title="Total ($)"),
                tooltip=[alt.Tooltip("date:T", format="%Y-%m-%d"), alt.Tooltip("total:Q", format="$.2f"), "count:Q"]
            ).properties(height=320)
            
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.info("No daily transactions for this month.")

    # 3. Monthly Trends Over Time
    st.subheader("Monthly Spending Overview")
    if trends:
        df_trends = pd.DataFrame(trends)
        trend_bar = alt.Chart(df_trends).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#3B82F6").encode(
            x=alt.X("month:N", title="Month"),
            y=alt.Y("total:Q", title="Total Spent ($)"),
            tooltip=["month", alt.Tooltip("total:Q", format="$.2f"), "count:Q"]
        ).properties(height=240)
        st.altair_chart(trend_bar, use_container_width=True)


# -------------------------------------------------------------
# TAB 2: TRANSACTIONS HISTORY & FILTERS
# -------------------------------------------------------------
with tab_transactions:
    # Filter Toolbar
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 2, 2])
    with f_col1:
        tx_search = st.text_input("🔍 Search", placeholder="Title or notes...", label_visibility="collapsed")
    with f_col2:
        all_cats = ["All Categories"] + manager.get_categories()
        tx_cat = st.selectbox("Category Filter", options=all_cats, label_visibility="collapsed")
    with f_col3:
        all_pms = ["All Payment Methods"] + manager.get_payment_methods()
        tx_pm = st.selectbox("Payment Method Filter", options=all_pms, label_visibility="collapsed")
    with f_col4:
        all_time = st.checkbox("Show All Months", value=False)

    # Fetch Filtered Transactions
    start_filter = None if all_time else f"{selected_month}-01"
    end_filter = None if all_time else f"{selected_month}-31"

    filtered_expenses = manager.filter_expenses(
        start_date=start_filter,
        end_date=end_filter,
        category=None if tx_cat == "All Categories" else tx_cat,
        payment_method=None if tx_pm == "All Payment Methods" else tx_pm,
        search_query=tx_search if tx_search else None
    )

    if filtered_expenses:
        df_display = pd.DataFrame([e.to_dict() for e in filtered_expenses])
        df_display = df_display.drop(columns=["created_at"], errors="ignore")
        df_display["amount"] = df_display["amount"].apply(lambda x: f"${x:,.2f}")
        df_display.columns = ["ID", "Title", "Amount", "Category", "Date", "Payment Method", "Notes"]

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Quick Delete by ID
        del_col1, del_col2 = st.columns([1, 4])
        with del_col1:
            del_id = st.number_input("Delete ID", min_value=1, step=1, label_visibility="collapsed")
        with del_col2:
            if st.button("🗑️ Delete Transaction", type="secondary"):
                if manager.delete_expense(int(del_id)):
                    st.success(f"Deleted transaction #{del_id}")
                    st.rerun()
                else:
                    st.error(f"Transaction #{del_id} not found.")

        # CSV Export & Download
        csv_buffer = io.StringIO()
        manager.export_to_csv(csv_buffer.name if hasattr(csv_buffer, 'name') else "temp.csv", filtered_expenses)
        with open("temp.csv", "r", encoding="utf-8") as f:
            csv_data = f.read()

        st.download_button(
            label="📥 Download Transactions (CSV)",
            data=csv_data,
            file_name=f"expenses_{selected_month}.csv",
            mime="text/csv"
        )
    else:
        st.info("No transactions found matching the criteria.")

    # CSV Import Section
    st.divider()
    st.subheader("📤 Import Transactions from CSV")
    uploaded_file = st.file_uploader("Upload CSV file (Must have Title, Amount, Category, Date columns)", type=["csv"])
    if uploaded_file is not None:
        temp_import_path = "temp_import.csv"
        with open(temp_import_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        success_cnt, err_cnt, err_msgs = manager.import_from_csv(temp_import_path)
        if os.path.exists(temp_import_path):
            os.remove(temp_import_path)
        
        st.success(f"✓ Imported {success_cnt} transactions successfully!")
        if err_cnt > 0:
            st.warning(f"⚠️ {err_cnt} rows failed:")
            for err in err_msgs[:5]:
                st.write(f"- {err}")
        st.rerun()


# -------------------------------------------------------------
# TAB 3: BUDGET TRACKING
# -------------------------------------------------------------
with tab_budget_view:
    st.subheader(f"Category Budget Status for {selected_month}")
    
    budgets_map = manager.get_budgets_for_month(selected_month)
    summaries = manager.get_category_breakdown(selected_month)

    if not summaries and not budgets_map:
        st.info("No expenses or budgets configured for this month.")
    else:
        budget_rows = []
        for s in summaries:
            b_limit = budgets_map.get(s.category, 0.0)
            remaining = b_limit - s.total_amount if b_limit > 0 else 0.0
            used_pct = (s.total_amount / b_limit * 100.0) if b_limit > 0 else 0.0

            status = "Normal"
            if b_limit > 0:
                if used_pct >= 100.0:
                    status = "🚨 Exceeded"
                elif used_pct >= 80.0:
                    status = "⚠️ Warning (80%+)"
                else:
                    status = "✅ On Track"
            else:
                status = "No Limit Set"

            budget_rows.append({
                "Category": s.category,
                "Spent ($)": f"${s.total_amount:,.2f}",
                "Budget ($)": f"${b_limit:,.2f}" if b_limit > 0 else "-",
                "Remaining ($)": f"${remaining:,.2f}" if b_limit > 0 else "-",
                "Used (%)": f"{used_pct:.1f}%" if b_limit > 0 else "-",
                "Status": status
            })

        st.dataframe(pd.DataFrame(budget_rows), use_container_width=True, hide_index=True)

        # Progress bars for budgeted categories
        st.write("#### Budget Progress Indicators")
        for s in summaries:
            b_limit = budgets_map.get(s.category, 0.0)
            if b_limit > 0:
                pct = min(1.0, s.total_amount / b_limit)
                st.write(f"**{s.category}**: ${s.total_amount:,.2f} of ${b_limit:,.2f} ({s.total_amount/b_limit*100:.1f}%)")
                st.progress(pct)
