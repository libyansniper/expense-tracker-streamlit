import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")
st.title("📊 Personal Expense Dashboard")
st.subheader("Track your daily expenses and monitor your budget in real-time")

# 2. Initialize Session State for Data Storage
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount (€)", "Notes"])

# 3. Sidebar Input Form
st.sidebar.header("📥 Add New Expense")
with st.sidebar.form("expense_form", clear_on_submit=True):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Housing & Insurance", "Transport", "Entertainment", "Others"])
    amount = st.number_input("Amount (€)", min_value=0.0, step=1.0)
    notes = st.text_input("Notes / Description")
    submit = st.form_submit_button("Save Expense")

    if submit and amount > 0:
        # Add new record to the DataFrame
        new_row = pd.DataFrame([[date, category, amount, notes]], columns=["Date", "Category", "Amount (€)", "Notes"])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
        st.success("Expense saved successfully! ✅")

# 4. Dashboard Visualizations and Data Table
df = st.session_state.expenses

if not df.empty:
    # Split the screen into two columns
    col1, col2 = st.columns()

    with col1:
        st.markdown("### 📋 Registered Expenses")
        st.dataframe(df, use_container_width=True)
        
        # Calculate Total Expenses
        total = df["Amount (€)"].sum()
        st.metric(label="💰 Total Spending", value=f"{total:.2f} €")

    with col2:
        st.markdown("### 📈 Expense Breakdown by Category")
        # Interactive Pie Chart using Plotly
        fig = px.pie(df, values="Amount (€)", names="Category", hole=0.3, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 No expenses recorded yet. Use the sidebar menu to add your first expense!")