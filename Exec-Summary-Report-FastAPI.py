#!/usr/bin/env python
# coding: utf-8

# In[7]:


from fastapi import FastAPI, HTTPException, UploadFile, File
from starlette.responses import FileResponse
from pydantic import BaseModel
import json
import pdfkit
from typing import List, Optional

from typing import Optional, List
from pydantic import BaseModel

class Cell(BaseModel):
    Value: Optional[str]

class Row(BaseModel):
    RowType: str
    Cells: List[Cell]

class Section(BaseModel):
    Title: Optional[str] = None  # Make Title optional
    Rows: Optional[List[Row]] = None  # Make Rows optional

class Report(BaseModel):
    ReportID: str
    ReportName: str
    ReportType: str
    ReportTitles: List[str]
    Rows: List[Optional[Section]]  # Allow for optional sections

class ExecutiveSummaryData(BaseModel):
    Reports: List[Report]
app = FastAPI()

@app.post("/upload-and-generate-executive-summary/")
async def upload_and_generate_executive_summary(file: UploadFile = File(...)):
    content = await file.read()
    try:
        data = json.loads(content)
        validated_data = ExecutiveSummaryData(**data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error parsing JSON data: {str(e)}")

    summary_data = prepare_executive_summary(validated_data)
    html_template = create_html_template(summary_data)

    pdf_filename = "executive_summary.pdf"
    pdfkit.from_string(html_template, pdf_filename)

    return FileResponse(pdf_filename, filename=pdf_filename, media_type='application/pdf')

def prepare_executive_summary(data: ExecutiveSummaryData):
    summary = []
    for report in data.Reports:
        if report.ReportID == "ExecutiveSummary":
            for section in report.Rows:
                if section.Rows:  # Check if Rows is not None
                    section_summary = {"title": section.Title, "rows": []}
                    for row in section.Rows:
                        if row.RowType == "Row":
                            cells = row.Cells
                            description = cells[0].Value if len(cells) > 0 else ""
                            values = [cell.Value for cell in cells[1:]]
                            section_summary["rows"].append({"description": description, "values": values})
                    summary.append(section_summary)
    return summary


def create_html_template(summary_data):
    html = '<html><head><title>Executive Summary</title><style>'
    html += '''
        body { font-family: Arial, sans-serif; }
        h1, h2 { text-align: center; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .section-title { font-weight: bold; }
        .amount { text-align: right; }
        .column-header-large, .column-data-large { width: 40%; }  /* Larger width for the first column */
        .column-header-small, .column-data-small { width: 20%; }  /* Smaller width for the last three columns */
    '''
    html += '</style></head><body>'
    html += '<h1>Executive Summary</h1>'
    for section in summary_data:
        html += f"<h2>{section['title']}</h2>"
        html += '<table>'
        html += '<tr>'
        html += '<th class="column-header-large">Particulars</th>'
        html += '<th class="column-header-small">Dec 2023</th>'
        html += '<th class="column-header-small">Nov 2023</th>'
        html += '<th class="column-header-small">Variance</th>'
        html += '</tr>'
        for row in section["rows"]:
            html += '<tr>'
            html += f"<td class='column-data-large'>{row['description']}</td>"
            html += f"<td class='column-data-small'>{row['values'][0]}</td>"
            html += f"<td class='column-data-small'>{row['values'][1]}</td>"
            html += f"<td class='column-data-small'>{row['values'][2]}</td>"
            html += '</tr>'
        html += '</table>'
    html += '</body></html>'
    return html



# In[ ]:




