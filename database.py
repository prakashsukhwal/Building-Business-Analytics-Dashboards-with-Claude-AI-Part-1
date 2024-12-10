from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Float)
    region = Column(String)
    product = Column(String)
    user_id = Column(Integer)

# Create database engine
engine = create_engine('sqlite:///sales.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Function to populate database with sample data
def populate_sample_data():
    session = Session()
    
    # Check if data already exists
    if session.query(Sale).first() is not None:
        session.close()
        return
    
    # Generate sample data
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(365)]
    regions = ['North', 'South', 'East', 'West']
    products = ['Product A', 'Product B', 'Product C']
    
    for i in range(1000):  # Generate 1000 sales records
        sale = Sale(
            date=np.random.choice(dates),
            amount=np.random.normal(1000, 200),
            region=np.random.choice(regions),
            product=np.random.choice(products),
            user_id=1
        )
        session.add(sale)
    
    session.commit()
    session.close()

# Initial data population
populate_sample_data()