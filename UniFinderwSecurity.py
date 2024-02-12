#!/usr/bin/env python
# coding: utf-8

# In[5]:


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import requests
import pandas as pd
import streamlit as st

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Define security with HTTPBasic
security = HTTPBasic()

# Define a function to check credentials
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "user")
    correct_password = secrets.compare_digest(credentials.password, "password")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Define your FastAPI route for university search
@app.get("/universities/")
def get_universities(country: str):
    url = f"http://universities.hipolabs.com/search?country={country.replace(' ', '+')}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data)
    
    result_json = df.to_json(orient="records")
    
    return result_json

# Streamlit interface
st.title('University Search')
country = st.text_input('Enter a country name')
if st.button('Search'):
    df = pd.read_json(requests.get(f'http://127.0.0.1:8001/universities/?country={country}').json())
    st.table(df)
else:
    st.error('Error')

# Define a route for documentation with password protection
@app.get("/docs")
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

# Define a route for OpenAPI JSON with password protection
@app.get("/openapi.json")
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title="FastAPI", version="0.1.0", routes=app.routes)


# In[ ]:




