from datetime import datetime, timedelta
from fastapi import FastAPI
from typing import Optional
import requests  # For making HTTP requests
from oauthlib.oauth2 import BackendApplicationClient  # For OAuth2
from requests_oauthlib import OAuth2Session 
import json


def calculate_dates(selection, custom_start=None, custom_end=None):
    if Range == 'This month':
        start_date = datetime.now().date().replace(day=1)
        end_date = datetime.now().date()
    elif Range == 'This quarter':
        start_date = datetime.now().date().replace(month=(datetime.now().date().month - 1) // 3 * 3 + 1, day=1)
        end_date = datetime.now().date()
    elif Range == 'This financial year':
        start_date = datetime.now().date().replace(month=1, day=1)
        end_date = datetime.now().date()
    elif Range == 'Last month':
        start_date = (datetime.now().date() - timedelta(days=1)).replace(day=1)
        end_date = datetime.now().date() - timedelta(days=1)
    elif Range == 'Last quarter':
        start_date = (datetime.now().date() - timedelta(days=1)).replace(month=(datetime.now().date().month - 1) // 3 * 3 + 1, day=1)
        end_date = datetime.now().date() - timedelta(days=1)
    elif Range == 'Last financial year':
        start_date = (datetime.now().date() - timedelta(days=1)).replace
    elif selection == 'Custom_date' and custom_start and custom_end:
        start_date = datetime.strptime(custom_start, "%Y-%m-%d")
        end_date = datetime.strptime(custom_end, "%Y-%m-%d")
    else:
        return None, None  # Default case if no valid selection is found

    return start_date, end_date


app = FastAPI()


def profit_and_loss_modified(selection,start_date,end_date):
    this_month = datetime.now().date().replace(day=1)
    this_quarter = this_month.replace(month=(this_month.month - 1) // 3 * 3 + 1, day=1)
    this_financial_year = this_month.replace(month=1, day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1) ## Not coming proper
    last_quarter = (this_quarter - timedelta(days=1)).replace(day=1) #this also not
    last_financial_year = this_financial_year - timedelta(days=1)
    last_financial_year_start = last_financial_year.replace(month=1, day=1)

    # Generate start and end dates based on the selection
    if selection == 'This month':
        start_date = this_month
        end_date = datetime.now().date()
    elif selection == 'This quarter':
        start_date = this_quarter
        end_date = datetime.now().date()
    elif selection == 'This financial year':
        start_date = this_financial_year
        end_date = datetime.now().date()
    elif selection == 'Last month':
        start_date = last_month
        end_date = this_month - timedelta(days=1)
    elif selection == 'Last quarter':
        start_date = last_quarter
        end_date = this_quarter - timedelta(days=1)
    elif selection == 'Last financial year':
        start_date = last_financial_year_start
        end_date = last_financial_year
    elif selection == 'Month to date':
        start_date = this_month
        end_date = datetime.now().date()
    elif selection == 'Quarter to date':
        start_date = this_quarter
        end_date = datetime.now().date()
    elif selection == 'Financial year to date':
        start_date = this_financial_year
        end_date = datetime.now().date()
    elif selection == 'Custom_date':
        start_date = datetime.strptime(custom_start, "%Y-%m-%d")
        end_date = d.strptime(custom_end, "%Y-%m-%d")
def fetch_profit_and_loss(start_date, end_date,timeframe,periods):
    response_finn = requests.get("")
    finn_token = response_finn.json()

    url = f"https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss?fromDate={start_date}&toDate={end_date}&timeframe={timeframe}&periods={periods}"

    headers = {
        'xero-tenant-id': "76f6e92f-37e4-4d28-9236-8672c09fc367",
        "accept": "application/json",
        'Authorization': f'Bearer {finn_token}',
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error fetching data from Xero: {response.text}")
        
@app.get("/PNL/")
async def get_insights(Range: str, Period: int, Timeframe: str, custom_start: Optional[str] = None, custom_end: Optional[str] = None):
    start_date, end_date = calculate_dates(Range, custom_start, custom_end)
    if start_date is None or end_date is None:
        raise HTTPException(status_code=400, detail="Invalid date range")

    profit_and_loss_modified(Range, start_date, end_date)

    pnl_data = fetch_profit_and_loss(start_date, end_date, Timeframe, Period)
    return pnl_data




