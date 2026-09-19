from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User,Document
from app.core.security import user_from_token
bearer=HTTPBearer()
def current_user(creds: HTTPAuthorizationCredentials=Depends(bearer), db: Session=Depends(get_db)):
    try: user_id=user_from_token(creds.credentials)
    except Exception: raise HTTPException(401,detail={"code":"INVALID_AUTH","message":"Invalid or expired token."})
    user=db.get(User,user_id)
    if not user: raise HTTPException(401,detail={"code":"INVALID_AUTH","message":"Invalid token user."})
    return user
def owned_document(document_id:str, db:Session=Depends(get_db), user:User=Depends(current_user)):
    doc=db.get(Document,document_id)
    if not doc or (doc.uploaded_by != user.id and user.role != "ADMIN"): raise HTTPException(404,detail={"code":"DOCUMENT_NOT_FOUND","message":"Document not found."})
    return doc
