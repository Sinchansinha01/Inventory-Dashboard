# Inventory Optimization Dashboard (Enhanced Version)
# Built using Python + Streamlit + Pandas + Google Sheets + Prophet (Forecasting)

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from prophet import Prophet

st.set_page_config(page_title="Inventory Optimization Dashboard", layout="wide")

# --- Google Sheets Setup ---
# Define your Google Sheets credentials and sheet details
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your_google_service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("InventoryData").sheet1  # Ensure your sheet is named correctly

# Load inventory data from Google Sheets
data = sheet.get_all_records()
inventory_df = pd.DataFrame(data)

# Data type conversion and cleaning
inventory_df['Last Restock Date'] = pd.to_datetime(inventory_df['Last Restock Date'])
inventory_df['Current Stock'] = pd.to_numeric(inventory_df['Current Stock'], errors='coerce')
inventory_df['Reorder Point'] = pd.to_numeric(inventory_df['Reorder Point'], errors='coerce')
inventory_df['Monthly Sales Avg'] = pd.to_numeric(inventory_df['Monthly Sales Avg'], errors='coerce')

# Page Title
st.title("📦 Inventory Optimization Dashboard")
st.markdown("Optimize stock levels, reduce overstocking, and prevent stockouts.")

# Sidebar filters
st.sidebar.header("🔍 Filters")
category_filter = st.sidebar.multiselect("Filter by Category", options=inventory_df['Category'].unique(), default=inventory_df['Category'].unique())
filtered_df = inventory_df[inventory_df['Category'].isin(category_filter)]

# Stock status and restock calculations
filtered_df['Stock Status'] = filtered_df.apply(lambda row: '✅ OK' if row['Current Stock'] > row['Reorder Point'] else '⚠️ Reorder', axis=1)
filtered_df['Days Since Restock'] = (datetime.today() - filtered_df['Last Restock Date']).dt.days

# Summary stats
col1, col2, col3 = st.columns(3)
col1.metric("Total SKUs", len(filtered_df))
col2.metric("SKUs to Reorder", (filtered_df['Stock Status'] == '⚠️ Reorder').sum())
col3.metric("Average Stock", int(filtered_df['Current Stock'].mean()))

# Inventory table
st.subheader("📊 Inventory Overview")
st.dataframe(filtered_df.sort_values(by='Stock Status', ascending=False), use_container_width=True)

# Download option
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Inventory Report",
    data=csv,
    file_name='inventory_report.csv',
    mime='text/csv',
)

# --- Forecasting Section ---
st.markdown("---")
st.subheader("📈 Demand Forecasting")
sku_to_forecast = st.selectbox("Select SKU to Forecast", filtered_df['SKU'].unique())

# Dummy sales history data for selected SKU (you'll need to replace this with actual sales history)
# In real setup, pull SKU-wise monthly historical sales from Google Sheets or another source
sales_data = pd.DataFrame({
    'ds': pd.date_range(start='2023-01-01', periods=18, freq='M'),
    'y': np.random.randint(20, 150, size=18)
})

# Forecast using Prophet
model = Prophet()
model.fit(sales_data)
future = model.make_future_dataframe(periods=6, freq='M')
forecast = model.predict(future)

st.write(f"Forecasted demand for {sku_to_forecast} (next 6 months):")
st.line_chart(forecast.set_index('ds')[['yhat']])

# Roadmap section
st.markdown("---")
st.subheader("🚀 Future Features")
st.markdown("""
- 🔔 Email alerts for reorder points
- 🧮 EOQ (Economic Order Quantity) calculator
- 📦 Live integration with POS/WMS APIs
""")
