import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.core.config import settings

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a contract document (.docx or .pdf) for analysis.
    """
    # 1. Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed.")

    # 2. Ensure upload directory exists
    upload_path = settings.UPLOAD_DIR
    os.makedirs(upload_path, exist_ok=True)
    
    # 3. Create a secure file path
    file_path = os.path.join(upload_path, file.filename)

    # 4. Save the file to the server
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # 5. Create a record in the database
    db_document = Document(
        filename=file.filename,
        file_path=file_path,
        document_type=file.content_type,
        upload_date=datetime.now()
        # user_id will be added later when we have auth
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document