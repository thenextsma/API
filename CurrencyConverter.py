import pandas as pd
import requests
import streamlit as st

# Function to convert currency
def convert_currency(df):
    exchange_rate_url = 'https://open.er-api.com/v6/latest/USD'
    exchange_rate_response = requests.get(exchange_rate_url)
    exchange_rate_data = exchange_rate_response.json()
    exchange_rates = exchange_rate_data.get('rates', {})

    def convert_to_usd(row):
        currency = row['Currency']
        invoice_amount_lc = row['Invoice Amount (LC)']

        if currency == 'USD':
            return invoice_amount_lc, f"1 USD = 1 {currency}"  

        exchange_rate = exchange_rates.get(currency)

        if exchange_rate:
            return invoice_amount_lc / exchange_rate, f"1 USD = {exchange_rate:.2f} {currency}"
        else:
            return None, None 
        
    df['Invoice Amount (USD)'], df['Exchange Rate'] = zip(*df.apply(convert_to_usd, axis=1))
    return df

# Streamlit UI
st.title('Currency Conversion App')
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if st.button('Convert Currency'):
        df = convert_currency(df)
        st.write('Updated Data:')
        st.dataframe(df)
