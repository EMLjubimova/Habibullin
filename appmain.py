from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from app import models, schemas, auth, crud
from app.database import engine, get_db
from app.routers import items, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WebServer + API",
    description="Контрольная работа. REST API с авторизацией и БД",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(items.router)

@app.get("/")
def root():
    return {
        "message": "Добро пожаловать в WebServer API",
        "docs": "/docs",
        "endpoints": ["/users", "/items", "/token"]
    }

@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}