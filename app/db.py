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
            FROM crime_data
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
    Fetches data and combines it in one endpoint  

    """
    city = city.lower().title()
    state = state.lower().title()
    query_rental = f"""
            SELECT city, state, price, date
            FROM forecasted_rentals_cities
            WHERE city='{city}';
            """
    query_crime = f"""
            SELECT "Violent_Crime_rate", "Property_Crime_rate", "Crime_Overall"
            FROM crime_data
            WHERE "CityName"='{city}';
            """
    query_population = f"""
            SELECT twenty_nineteen_population, ten_year_population_growth_percentage, us_population_rank
            FROM population
            WHERE city='{city}';
            """
    query_walkability = f"""
            SELECT walk_score, bike_score, transit_score
            FROM walkability
            WHERE city='{city}';
            """

    df_rental = pd.read_sql(query_rental, connection)
    df_crime = pd.read_sql(query_crime, connection)
    df_population = pd.read_sql(query_population, connection)
    df_walkability = pd.read_sql(query_walkability, connection)

    if len(df_rental) < 1:
        city_state = {'city': f'{city}', 'state': f'{state}'}
        dates_prices = {
            'rental_forecast': f'no rental data for {city, state}, try major city'}
    else:
        city_state = {'city': df_rental['city']
                      [0], 'state': df_rental['state'][0]}
        dates_prices = {'date_price': df_rental[[
            'date', 'price']].to_dict(orient='records')}

    crime_rates = {'violent_crime_rate': df_crime['Violent_Crime_rate'][0], 'property_crime_rate':
                   df_crime['Property_Crime_rate'][0], 'crime_overall':  df_crime['Crime_Overall'][0]}

    population = {'population': df_population.to_dict(orient='records')}

    walkability = {'walkability': df_walkability.to_dict(orient='records')}

    city_state.update(dates_prices)
    city_state.update(crime_rates)
    city_state.update(population)
    city_state.update(walkability)

    return city_state
