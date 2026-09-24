import sqlite3
import hashlib
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# 2. Database Setup & Helper Functions
def get_connection():
    conn = sqlite3.connect("expenses.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Table for users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # Table for expenses
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            category TEXT,
            amount REAL,
            notes TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def add_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, make_hashes(password)))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, make_hashes(password)))
    data = c.fetchall()
    conn.close()
    return data

def add_expense(username, date, category, amount, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO expenses(username, date, category, amount, notes) VALUES (?,?,?,?,?)',
              (username, str(date), category, amount, notes))
    conn.commit()
    conn.close()

def get_user_expenses(username):
    conn = get_connection()
    df = pd.read_sql_query('SELECT date AS Date, category AS Category, amount AS "Amount (€)", notes AS Notes FROM expenses WHERE username = ?', conn, params=(username,))
    conn.close()
    return df

# Initialize DB on start
init_db()

# 3. Session State for Authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# 4. Authentication UI
st.title("📊 Personal Expense Dashboard")

if not st.session_state.logged_in:
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Account Menu", menu)

    if choice == "Login":
        st.subheader("🔑 Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            result = login_user(username, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Incorrect Username/Password")

    elif choice == "Sign Up":
        st.subheader("📝 Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            if new_user and new_password:
                try:
                    add_user(new_user, new_password)
                    st.success("Account created successfully! Go to Login menu to log in.")
                except sqlite3.IntegrityError:
                    st.warning("Username already exists. Please choose a different username.")
            else:
                st.error("Please fill in all fields.")

else:
    # User is logged in
    st.sidebar.markdown(f"👤 **Logged in as:** `{st.session_state.username}`")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.subheader(f"Track your daily expenses and monitor your budget in real-time")

    # Sidebar Input Form
    st.sidebar.header("➕ Add New Expense")
    with st.sidebar.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Housing & Insurance", "Transport", "Entertainment", "Others"])
        amount = st.number_input("Amount (€)", min_value=0.0, step=1.0)
        notes = st.text_input("Notes / Description")
        submit = st.form_submit_button("Save Expense")

        if submit and amount > 0:
            add_expense(st.session_state.username, date, category, amount, notes)
            st.success("Expense saved successfully! ✅")

    # Fetch User Expenses
    df = get_user_expenses(st.session_state.username)

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📋 Registered Expenses")
            st.dataframe(df, use_container_width=True)

            total = df["Amount (€)"].sum()
            st.metric(label="💰 Total Spending", value=f"{total:.2f} €")

        with col2:
            st.markdown("### 📉 Expense Breakdown by Category")
            fig = px.pie(df, values="Amount (€)", names="Category", title="Expenses Distribution", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 No expenses recorded yet. Use the sidebar menu to add your first expense!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 12px; font-family: sans-serif; color: #888888; font-size: 14px;'>
        Developed by <strong style='color: #4CAF50; font-size: 15px;'>Ali Albshti</strong> 
        &nbsp;|&nbsp;
        GitHub: <a href='https://github.com/libyansniper' target='_blank' style='color: #2196F3; text-decoration: none; font-weight: bold;'>@libyansniper</a>
    </div>
    """,
    unsafe_allow_html=True
)

