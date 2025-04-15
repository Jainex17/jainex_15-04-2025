from fastapi import APIRouter, HTTPException
from app.api.tasks import generate_report
from celery.result import AsyncResult
from pydantic import BaseModel
from app.api.tasks import celery_app
import pandas as pd
import time
import os

router = APIRouter()

@router.get("/")
def read_root():
    return {"Message": "Hello World"}

@router.get("/trigger_report")
def trigger_report():
    try:
        report = generate_report.delay()
        return {"report_id": str(report.id)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while generating report"
        )

class ReportRequest(BaseModel):
    report_id: str

@router.post("/get_report")
def get_report(request: ReportRequest):
    try:
        if not request.report_id:
            raise HTTPException(
                status_code=400,
                detail="Report ID is required"
            )
        
        task = AsyncResult(request.report_id, app=celery_app)
        
        if not task.ready():
            return {
                "status": "Running"
            }

        if task.failed():
            raise HTTPException(
                status_code=500,
                detail="Report generation failed"
            )

        res = task.get()
        print(res)
        df = pd.DataFrame(res)
        csv_filename = f"report_{int(time.time())}.csv"
        csv_path = os.path.join("reports", csv_filename)
        df.to_csv(csv_path, index=False)
        
        return {
            "report_data": res
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while fetching report"
        )