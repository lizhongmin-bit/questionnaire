from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from .db import SessionLocal, settings


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(x_admin_token: str = Header(default="")):
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或权限不足")
