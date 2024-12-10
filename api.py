# api.py
from fastapi import FastAPI, Depends, HTTPException, Form  # Add Form to imports
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
import jwt
from typing import List
from database import Session, Sale
from sqlalchemy import func

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Add this new root route
@app.get("/")
async def root():
    return {"message": "Sales Dashboard API is running"}
SECRET_KEY = "your-secret-key"

@app.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):  # Modified this line
    # In a real app, verify credentials against database
    if username == "demo" and password == "password":
        token = jwt.encode(
             {
                "sub": username, 
                "exp": datetime.now(timezone.utc) + timedelta(hours=24)  # Updated this line
            },
            SECRET_KEY
        )
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.get("/sales")
async def get_sales(
    token: str = Depends(oauth2_scheme),
    start_date: str = None,
    end_date: str = None
):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session = Session()
    query = session.query(Sale)
    
    if start_date:
        query = query.filter(Sale.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Sale.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    sales = query.all()
    
    # Convert to dictionary format
    sales_data = [{
        'id': sale.id,
        'date': sale.date.strftime('%Y-%m-%d'),
        'amount': float(sale.amount),
        'region': sale.region,
        'product': sale.product
    } for sale in sales]
    
    session.close()
    return sales_data