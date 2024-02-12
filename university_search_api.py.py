#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install fastapi nest-asyncio pyngrok uvicorn')


# In[6]:


from fastapi import FastAPI
import requests
import pandas as pd


# In[7]:


app = FastAPI()


# In[8]:


@app.get("/universities/")
def get_universities(country: str):
    url = f"http://universities.hipolabs.com/search?country={country.replace(' ', '+')}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data)
    
    result_json = df.to_json(orient="records")
    
    return result_json


# In[ ]:





# In[ ]:





# In[ ]:




