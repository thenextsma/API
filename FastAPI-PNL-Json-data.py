#!/usr/bin/env python
# coding: utf-8

# In[118]:


from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from typing import Optional
import json

app = FastAPI()

def calculate_dates(selection, start_date, end_date):
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
    elif selection == 'Custom date':
        start_date = None
        end_date = None
    else:
        start_date = None
        end_date = None

    # Format dates to YYYY-MM-DD format
    start_date_str = start_date.strftime('%Y-%m-%d') if start_date else 'None'
    end_date_str = end_date.strftime('%Y-%m-%d') if end_date else 'None'

    return start_date_str, end_date_str
        
def process_profit_and_loss(data, start_date, end_date, periods):
    report = data["Reports"][0]
    header_cells = report["Rows"][0]["Cells"]
    header_dates = [cell["Value"] for cell in header_cells[1:]]  # Exclude the first cell

    # Reduce the header dates based on the specified periods
    reduced_header_dates = header_dates[-periods:]

    # Initialize the result dictionary
    result = {"data": []}

    # Extract data for each section
    for section in report["Rows"]:
        if section["RowType"] == "Section":
            section_data = {}
            section_data["particulars"] = section["Title"]
            # Initialize the data dictionary with empty values for reduced header dates
            section_data.update({date: None for date in reduced_header_dates})

            for row in section["Rows"]:
                if row["RowType"] in ["Row", "SummaryRow"]:
                    cell_values = [cell["Value"] for cell in row["Cells"]]
                    if len(cell_values) >= len(header_dates) + 1:
                        # Extracting values for each reduced header date
                        section_data.update({header_dates[i]: cell_values[i + 1] for i in range(len(header_dates)) if header_dates[i] in reduced_header_dates})

            result["data"].append(section_data)

    # Return the result
    return result

@app.get("/PNL/")
async def get_pnl(Range: str, periods: int, custom_start: Optional[str] = None, custom_end: Optional[str] = None):
    try:
        start_date, end_date = calculate_dates(Range, custom_start, custom_end)
        print(f"Start Date: {start_date}, End Date: {end_date}")

        full_path = '/Users/mustafa/Downloads/year.json'
        with open(full_path) as file:
            data = json.load(file)

        processed_data = process_profit_and_loss(data, start_date, end_date, periods)
        return processed_data
    except Exception as e:
        return {"error": str(e)}


# In[ ]:





# In[ ]:





# In[ ]:




