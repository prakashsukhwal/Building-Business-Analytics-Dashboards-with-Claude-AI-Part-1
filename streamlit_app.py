import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Authentication
if 'token' not in st.session_state:
    st.title("Login")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        ### Demo Credentials
        Username: demo  
        Password: password
        """)
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            try:
                response = requests.post(
            "http://localhost:8000/token",
            data={
                "username": username,
                "password": password
            },
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
                if response.status_code == 200:
                    st.session_state.token = response.json()["access_token"]
                    st.rerun()  # Changed from st.experimental_rerun()
                else:
                    st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
    st.stop()

# Main app (only shown after authentication)
st.title("📊 Sales Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Date range picker
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(datetime.now() - timedelta(days=30), datetime.now())
)

# Fetch data from API
headers = {"Authorization": f"Bearer {st.session_state.token}"}
params = {
    "start_date": date_range[0].strftime('%Y-%m-%d'),
    "end_date": date_range[1].strftime('%Y-%m-%d')
}
response = requests.get(
    "http://localhost:8000/sales",
    headers=headers,
    params=params
)

if response.status_code != 200:
    st.error("Failed to fetch data")
    st.stop()

# Convert API data to DataFrame
df = pd.DataFrame(response.json())
df['date'] = pd.to_datetime(df['date'])

# Create metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Sales",
        value=f"${df['amount'].sum():,.0f}",
        delta=f"{df['amount'].mean():,.0f} avg"
    )

with col2:
    st.metric(
        label="Number of Transactions",
        value=f"{len(df):,}",
        delta=f"{len(df)/30:.1f} per day"
    )

with col3:
    st.metric(
        label="Average Sale",
        value=f"${df['amount'].mean():,.2f}",
        delta=f"{df['amount'].std():,.2f} std"
    )

with col4:
    st.metric(
        label="Highest Sale",
        value=f"${df['amount'].max():,.2f}",
        delta=f"{df['amount'].max() - df['amount'].mean():,.2f} from avg"
    )

# Create tabs for different visualizations
tab1, tab2 = st.tabs(["Sales Trend", "Regional Analysis"])

with tab1:
    # Daily sales trend
    daily_sales = df.groupby('date')['amount'].sum().reset_index()
    fig1 = px.line(
        daily_sales,
        x='date',
        y='amount',
        title='Daily Sales Trend'
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    # Regional sales breakdown
    regional_sales = df.groupby('region')['amount'].sum().reset_index()
    fig2 = px.pie(
        regional_sales,
        values='amount',
        names='region',
        title='Sales by Region'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Add interactive data table
st.subheader("Detailed Data View")
st.dataframe(
    df.sort_values('date', ascending=False),
    use_container_width=True,
    hide_index=True
)

# Add download button
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Data as CSV",
    data=csv,
    file_name="sales_data.csv",
    mime="text/csv"
)