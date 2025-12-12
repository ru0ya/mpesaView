import streamlit as st
import pandas as pd
from config.settings import PAGE_CONFIG, APP_NAME, APP_VERSION, GEMINI_API_KEY
from utils.parser import MpesaParser
from utils.analyzer import ExpenseAnalyzer
from utils.visualizations import Charts
from utils.ai_insights import FinancialAdvisor

# Page Setup
st.set_page_config(**PAGE_CONFIG)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title(f"📊 {APP_NAME} v{APP_VERSION}")
    
    # -- Sidebar --
    with st.sidebar:
        st.header("Upload M-Pesa Statement")
        uploaded_file = st.file_uploader("Choose PDF or CSV file", type=['pdf', 'csv'])
        
        st.divider()
        st.info("💡 Privacy Note: Your data is processed locally in memory. Only summarized stats are sent to AI if you use the Insights feature.")
        
        api_key_input = st.text_input("Gemini API Key", value=GEMINI_API_KEY, type="password", help="Needed for AI Insights")
        
        # Model Selection
        if api_key_input:
            with st.spinner("Loading models..."):
                available_models = FinancialAdvisor.list_available_models(api_key_input)
            
            if available_models:
                # Default to gemini-2.0-flash if available, else first one
                default_ix = 0
                if 'gemini-2.0-flash' in available_models:
                    default_ix = available_models.index('gemini-2.0-flash')
                elif 'gemini-1.5-flash' in available_models:
                    default_ix = available_models.index('gemini-1.5-flash')
                    
                model_name = st.selectbox("Select Model", available_models, index=default_ix)
            else:
                st.error("Invalid API Key or no available models found.")
                model_name = "gemini-2.0-flash" # Fallback
        else:
            model_name = "gemini-2.0-flash"

    # -- Processing --
    if uploaded_file is not None:
        try:
            # Check if file has changed
            if st.session_state.get('last_uploaded') != uploaded_file.name:
                with st.spinner("Parsing statement..."):
                    file_type = uploaded_file.name.split('.')[-1]
                    df = MpesaParser.parse_file(uploaded_file, file_type)
                    st.session_state.data = df
                    st.session_state.last_uploaded = uploaded_file.name
                    st.toast("Statement loaded successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error parsing file: {e}")
            return

    # -- Main Dashboard --
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Date Filter
        min_date = df['Completion Time'].min().date()
        max_date = df['Completion Time'].max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date)
        with col2:
            end_date = st.date_input("End Date", max_date)
            
        # Filter Data
        mask = (df['Completion Time'].dt.date >= start_date) & (df['Completion Time'].dt.date <= end_date)
        filtered_df = df.loc[mask]
        
        if filtered_df.empty:
            st.warning("No transactions found in selected date range.")
            return

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Spending Analysis", "Transactions", "AI Insights"])
        
        with tab1:
            st.subheader("Financial Overview")
            
            # KPIs
            kpis = ExpenseAnalyzer.calculate_kpis(filtered_df)
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Income", f"KES {kpis['total_income']:,.2f}", delta_color="normal")
            k2.metric("Total Expenses", f"KES {kpis['total_expenses']:,.2f}", delta_color="inverse")
            k3.metric("Net Savings", f"KES {kpis['net_savings']:,.2f}", delta=f"{kpis['net_savings']:,.2f}")
            k4.metric("Transactions", kpis['transaction_count'])
            
            st.divider()
            
            # Charts
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(Charts.get_income_expense_pie(kpis), use_container_width=True)
            with c2:
                monthly_trends = ExpenseAnalyzer.get_monthly_trends(filtered_df)
                st.plotly_chart(Charts.get_monthly_trend_line(monthly_trends), use_container_width=True)
                
        with tab2:
            st.subheader("Spending Analysis")
            
            # Category Breakdown
            cat_df = ExpenseAnalyzer.get_category_breakdown(filtered_df, transaction_type='Expense')
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.plotly_chart(Charts.get_category_bar(cat_df), use_container_width=True)
            with c2:
                st.markdown("### Top Expense Categories")
                st.dataframe(cat_df, hide_index=True)
                
            st.divider()
            st.subheader("Transaction Activity Heatmap")
            st.plotly_chart(Charts.get_daily_activity_heatmap(filtered_df), use_container_width=True)
            
        with tab3:
            st.subheader("Transaction History")
            
            search_term = st.text_input("Search Transactions", placeholder="Enter name, receipt no, etc.")
            
            display_df = filtered_df.copy()
            if search_term:
                display_df = display_df[
                    display_df['Details'].astype(str).str.contains(search_term, case=False) |
                    display_df['Receipt No.'].astype(str).str.contains(search_term, case=False)
                ]
                
            st.dataframe(
                display_df.sort_values('Completion Time', ascending=False),
                column_config={
                    "Completion Time": st.column_config.DatetimeColumn(format="D MMM YYYY, h:mm a"),
                    "Amount": st.column_config.NumberColumn(format="KES %.2f")
                },
                use_container_width=True
            )
            
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "filtered_transactions.csv", "text/csv")
            
        with tab4:
            st.subheader("🤖 AI Financial Advisor")
            st.markdown("Get personalized insights powered by Google Gemini.")
            
            if st.button("Generate Insights", type="primary"):
                with st.spinner("Analyzing your financial patterns..."):
                    advisor = FinancialAdvisor(api_key=api_key_input, model_name=model_name)
                    
                    # Prepare data summary
                    kpis_clean = {k: float(v) for k, v in kpis.items()}
                    top_cats = ExpenseAnalyzer.get_category_breakdown(filtered_df)
                    
                    insight = advisor.generate_insights(kpis_clean, top_cats)
                    st.markdown(insight)

    else:
        st.info("👆 Please upload your M-Pesa statement (PDF or CSV) to begin analysis.")
        
        # Demo Data Option could go here
        
if __name__ == "__main__":
    main()
