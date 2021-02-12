"""Database functions"""

import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
import sqlalchemy

import pandas as pd

router = APIRouter()


async def get_db() -> sqlalchemy.engine.base.Connection:
    """Get a SQLAlchemy database connection.
    
    Uses this environment variable if it exists:  
    DATABASE_URL=dialect://user:password@host/dbname

    Otherwise uses a SQLite database for initial local development.
    , default='sqlite:///temporary.db'
    """
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    engine = sqlalchemy.create_engine(database_url)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@router.get('/info')
async def get_url(connection=Depends(get_db)):
    """Verify we can connect to the database, 
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """
    url_without_password = repr(connection.engine.url)
    return {'database_url': url_without_password}


@router.get('/rental-historical-data')
async def read_historical_rentals(connection=Depends(get_db)):
    """
    Fetches historical rental data for 2014-2020 years per city/state
    for future use when utilizing graphs
    """
    query = f"""
            SELECT city, state, price, date
            FROM historical_rentals; 
            """
    df = pd.read_sql(query, connection)

    if len(df) > 0:
        return df.to_dict(orient='records')
    else:
        return f'Error. Data is not found.'


@router.get('/rental-forecast-cities')
async def read_rental_cities(connection=Depends(get_db)):
    """
    Fetches rental data forecasted for next 2 years  per city/state
    """
    query = f"""
            SELECT city, state, price, date
            FROM forecasted_rentals_cities; 
            """
    df = pd.read_sql(query, connection)

    if len(df) > 0:
        return df.to_dict(orient='records')
    else:
        return f'Error. Data is not found.'



@router.get('/rental-forecast-states')
async def read_rental_states(connection=Depends(get_db)):
    """
    Fetches rental price average per state forecasted for next 2 years
    """
    query = f"""
            SELECT state, price, date
            FROM forecasted_rentals_states; 
            """
    df = pd.read_sql(query, connection)

    if len(df) > 0:
        return df.to_dict(orient='records')
    else:
        return f'Error. Data is not found.'



@router.get('/walkability-score')
async def read_walkability(connection=Depends(get_db)):
    """
    Fetches rental price average per state forecasted for next 2 years
    """
    query = f"""
            SELECT city, state, walk_score, transit_score, bike_score, population
            FROM walkability; 
            """
    df = pd.read_sql(query, connection)

    if len(df) > 0:
        return df.to_dict(orient='records')
    else:
        return f'Error. Data is not found.'


@router.get('/crime-rate')
async def read_crime(connection=Depends(get_db)):
    """
    Fetches rental price average per state forecasted for next 2 years
    """
    query = f"""
            SELECT *
            FROM CRIME_DATA
            LIMIT 100; 
            """
    df = pd.read_sql(query, connection)

    if len(df) > 0:
        return df.to_dict(orient='records')
    else:
        return f'Error. Data is not found.'

@router.post('/predict')
async def read_data(city, state, connection=Depends(get_db)):
    """
    Fetches data and combines it in one endpoint. 
    It's only rental data right now, other features will be added
    """
    city = city.lower().title()
    state = state.lower().title()
    query = f"""
            SELECT city, state, price, date
                FROM forecasted_rentals_cities
                WHERE city='{city}';
            """
    df = pd.read_sql(query, connection)
    if len(df) > 0:
        return df.to_dict(orient='records')
    else:
        query = f"""
            SELECT city, price, date
                FROM forecasted_rentals_cities
                WHERE state='{state}';
            """
        df = pd.read_sql(query, connection)
        print(f"Specific City not found. Listed cities per state {state}")
        return df.to_dict(orient='records')

