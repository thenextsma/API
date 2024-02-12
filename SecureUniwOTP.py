#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os
import pyotp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import streamlit as st
import secrets
import requests
import pandas as pd

# FastAPI app
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Security with HTTPBasic
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv('MY_APP_USERNAME'))
    correct_password = secrets.compare_digest(credentials.password, os.getenv('MY_APP_PASSWORD'))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Function to send OTP email
def send_otp_email(email, otp):
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_address or not email_password:
        print("Email credentials are not set.")
        return

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(email_address, email_password)
            subject = "OTP Authentication"
            message = f"Your OTP is: {otp}"
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            smtp.sendmail(email_address, email, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

# Streamlit interface
st.title('University Search')

# Initialize Streamlit session state for OTP
if 'otp_sent' not in st.session_state:
    st.session_state['otp_sent'] = False
if 'otp' not in st.session_state:
    st.session_state['otp'] = None

# Step 1: Ask for username
username = st.text_input('Enter your username')
if username:
    # Step 2: Ask for password
    password = st.text_input('Enter your password', type='password')
    if password:
        # Step 3: Send OTP only once per session
        if not st.session_state['otp_sent']:
            otp = pyotp.TOTP(pyotp.random_base32()).now()
            send_otp_email(username, otp)  # Send OTP to the receiver's email
            st.session_state['otp'] = otp  # Save the OTP in session state
            st.session_state['otp_sent'] = True  # Mark OTP as sent

        # Step 4: Ask for OTP
        otp_input = st.text_input('Enter OTP', type='password')
        if otp_input and st.session_state['otp'] == otp_input:
            # Authenticated, proceed to request data
            country = st.text_input('Enter a country name')
            if country:
                st.write(f"Authenticated with username: {username}")
                st.write(f"Country: {country}")
        else:
            st.error('Authentication failed. Please check your credentials and OTP.')

# Step 5: Define the FastAPI route to get universities
@app.get("/universities/")
def get_universities(
    country: str, username: str = Depends(get_current_username)
):
    url = f"http://universities.hipolabs.com/search?country={country.replace(' ', '+')}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data)

    result_json = df.to_json(orient="records")

    return result_json


# In[ ]:




