#!/usr/bin/env python
# coding: utf-8

# In[4]:


from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

def find_start_end_date(period, custom_start=None, custom_end=None):
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    if period == "lastmonth":
        if current_month == 1:
            start_month = 12
            start_year = current_year - 1
        else:
            start_month = current_month - 1
            start_year = current_year

        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(current_year, current_month, 1) - timedelta(days=1)

    elif period == "three_month":
        start_month = (current_month - 3 - 1) % 12 + 1
        start_year = current_year if current_month > 3 else current_year - 1

        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(current_year, current_month, 1) - timedelta(days=1)

    elif period == "six_month":
        start_month = (current_month - 6 - 1) % 12 + 1
        start_year = current_year if current_month > 6 else current_year - 1

        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(current_year, current_month, 1) - timedelta(days=1)

    elif period == "last_year":
        start_date = datetime(current_year - 1, 1, 1)
        end_date = datetime(current_year - 1, 12, 31)

    elif period == "custom":
        try:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d')
            end_date = datetime.strptime(custom_end, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid custom date format. Use YYYY-MM-DD")

    else:
        raise ValueError("Invalid period specified")

    return start_date, end_date

@app.get("/get_dates/")
async def get_dates(period: str, custom_start: Optional[str] = None, custom_end: Optional[str] = None):
    try:
        start_date, end_date = find_start_end_date(period, custom_start, custom_end)
        return {"start_date": start_date.strftime('%Y-%m-%d'), "end_date": end_date.strftime('%Y-%m-%d')}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# In[ ]:




