import os
import traceback
from uuid import uuid4
from typing import List

import boto3
from fastapi import FastAPI, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
# from sqlalchemy.orm import Session
# from sqlmodel import select
#
# from model import Details
# from database import create_db_and_tables, get_session

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

# # AWS S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "noticefiles")
s3_client = boto3.client("s3")

@app.post("/upload")
async def upload_pdf(
    name: str = Form(...),
    emp_id: int = Form(...),
    upload_file: UploadFile = File(...),
    # session: Session = Depends(get_session)  # Remove if you don't want DB
):
    if upload_file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})

    try:
        # Generate a unique file name
        file_extension = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"

        # Upload the file to S3
        s3_client.upload_fileobj(
            Fileobj=upload_file.file,
            Bucket=S3_BUCKET_NAME,
            Key=unique_filename,
            ExtraArgs={"ContentType": upload_file.content_type}
        )

        # # Optional: store metadata in the database
        # detail = Details(name=name, emp_id=emp_id, file_path=unique_filename)
        # session.add(detail)
        # session.commit()
        # session.refresh(detail)

        return JSONResponse(
            content={
                "message": "PDF uploaded to S3 successfully.",
                "s3_key": unique_filename,
                "name": name,
                "empId": emp_id
            },
            status_code=200
        )

    except Exception as e:
        print("Error uploading to S3:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "File upload failed."})

# @app.get("/app/all/", response_model=List[Details])
# def get_all_uploads(session: Session = Depends(get_session)):
#     try:
#         statement = select(Details)
#         results = session.exec(statement).all()
#         return results
#     except Exception as e:
#         print("Error fetching data from DB:", e)
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# Lambda entry point
handler = Mangum(app)
