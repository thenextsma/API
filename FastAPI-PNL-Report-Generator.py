#!/usr/bin/env python
# coding: utf-8

# In[9]:


from fastapi import FastAPI, HTTPException, UploadFile, File
from starlette.responses import FileResponse
from pydantic import BaseModel, Field
import json
import pdfkit
from jinja2 import Template
import os
from typing import List, Optional
from datetime import datetime

class Cell(BaseModel):
    Value: Optional[str]

class Row(BaseModel):
    RowType: str
    Cells: List[Cell]

class Section(BaseModel):
    Title: Optional[str] = None  
    Rows: Optional[List[Row]] = None 

class Report(BaseModel):
    ReportID: str
    ReportName: str
    ReportType: str
    ReportTitles: List[str]
    Rows: List[Section]

class TotalProfitAndLossData(BaseModel):
    Reports: List[Report]

app = FastAPI()

@app.post("/upload-and-generate-pl-report/")
async def upload_and_generate_pl_report(file: UploadFile = File(...)):
    if file.content_type != "application/json":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JSON file.")

    content = await file.read()
    try:
        data = json.loads(content)
        validated_data = TotalProfitAndLossData(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error parsing JSON data: {str(e)}")

    json_output = {
        "title": "Profit & Loss Statement",
        "sections": []
    }

    for report in data.get("Reports", []):
        if report["ReportID"] == "ProfitAndLoss":
            for section in report.get("Rows", []):
                if section["RowType"] == "Section":
                    section_data = {
                        "title": section.get("Title", ""),
                        "rows": []
                    }
                    for row in section.get("Rows", []):
                        if row["RowType"] in ["Row", "SummaryRow"]:
                            cells = row.get("Cells", [])
                            description = cells[0].get("Value", "") if len(cells) > 0 else ""
                            amount = cells[1].get("Value", "") if len(cells) > 1 else ""
                            section_data["rows"].append({
                                "description": description,
                                "amount": amount
                            })
                    json_output["sections"].append(section_data)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Profit and Loss Statement</title>
        <style>
            body {
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
            }
            h1, h2 {
                margin: 0;
                padding: 0;
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
            .section-title {
                background-color: #e7e7e7;
                font-weight: bold;
            }
            .summary-row {
                font-weight: bold;
            }
            .amount {
                text-align: right;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ json_output['title'] }}</h1>
            <!-- Add other header elements if needed -->
        </div>
        <table>
            {% for section in json_output['sections'] %}
            <tr class="section-title">
                <td colspan="2">{{ section['title'] }}</td>
            </tr>
            {% for row in section['rows'] %}
            <tr class="{{ 'summary-row' if 'Total' in row['description'] else '' }}">
                <td>{{ row['description'] }}</td>
                <td class="amount">{{ row['amount'] }}</td>
            </tr>
            {% endfor %}
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_content = template.render(json_output=json_output)

   
    path_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdf_filename = "pl_report.pdf"

    try:
        pdfkit.from_string(html_content, pdf_filename, configuration=config)

        if not os.path.exists(pdf_filename):
            raise HTTPException(status_code=500, detail="PDF file not found after creation.")

        return FileResponse(pdf_filename, filename=pdf_filename, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# In[ ]:




