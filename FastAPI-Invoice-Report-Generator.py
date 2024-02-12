#!/usr/bin/env python
# coding: utf-8

# In[4]:


from fastapi import FastAPI, HTTPException, UploadFile, File
from starlette.responses import FileResponse
from pydantic import BaseModel, Field
import json
from typing import List
from datetime import date
import pdfkit
from jinja2 import Template
import os

# Define your data models
class InvoiceItem(BaseModel):
    Name: str
    AmountDue: float
    InvoiceNumber: str = Field(..., alias='Invoice Number')
    Date: date
    DueDate: date = Field(..., alias='Due Date')
    DaysFromToday: int = Field(..., alias='Days from Today')

class InvoiceStats(BaseModel):
    MaxDaysFromToday: int = Field(..., alias='Max Days from Today')
    MaxAmountDue: float = Field(..., alias='Max Amount Due')

class AverageStats(BaseModel):
    AverageDays: float = Field(..., alias='Average Days')
    AverageAmountDue: float = Field(..., alias='Average Amount Due')

class AgeingItem(BaseModel):
    Ageing: str
    Amount: float

class TotalInvoiceData(BaseModel):
    invoices: List[InvoiceItem]
    invoice: InvoiceStats
    average: AverageStats
    ageing: List[AgeingItem]

app = FastAPI()

@app.post("/upload-and-generate-report/")
async def upload_and_generate_report(file: UploadFile = File(...)):
    if file.content_type != "application/json":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JSON file.")
    
    content = await file.read()
    try:
        data = json.loads(content)
        validated_data = TotalInvoiceData(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error parsing JSON data: {str(e)}")

    # HTML Template with styling
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Invoice Table</title>
        <style>
            body {
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                color: black;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Invoice ID</th>
                    <th>Amount</th>
                    <th>Date of Issue</th>
                    <th>Due Date</th>
                    <th>Due Days</th>
                </tr>
            </thead>
            <tbody>
                {% for item in invoices %}
                <tr>
                    <td>{{ item.Name }}</td>
                    <td>{{ item.InvoiceNumber }}</td>
                    <td>${{ "%.2f"|format(item.AmountDue) }}</td>
                    <td>{{ item.Date }}</td>
                    <td>{{ item.DueDate }}</td>
                    <td>{{ item.DaysFromToday }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    # Generate the HTML content
    template = Template(html_template)
    html_content = template.render(invoices=validated_data.invoices)

    # Define path to the wkhtmltopdf binary
    path_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdf_filename = "invoice_report.pdf"

    try:
        pdfkit.from_string(html_content, pdf_filename, configuration=config)

        # Check if the file was created
        if not os.path.exists(pdf_filename):
            raise HTTPException(status_code=500, detail="PDF file not found after creation.")

        return FileResponse(pdf_filename, filename=pdf_filename, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# In[ ]:




