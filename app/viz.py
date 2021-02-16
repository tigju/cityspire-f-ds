"""Data visualization functions"""

import plotly.express as px
from fastapi import APIRouter
import pandas as pd

router = APIRouter()


# upload data from csv
df_cities_historical = pd.read_csv(
    'notebooks/rentals/data/historical_rentals.csv', parse_dates=['date'], index_col=['date'])
df_cities_historical.drop(columns=['Unnamed: 0'], inplace=True)

df_cities_forecast = pd.read_csv(
    "notebooks/rentals/data/forecasted_rentals_cities.csv", index_col=0)
df_states_forecast = pd.read_csv(
    "notebooks/rentals/data/forecasted_rentals_states.csv",  index_col=0)

avg_state_hist = df_cities_historical.groupby('state').resample('M').mean()
avg_hist = avg_state_hist.reset_index()


@router.post('/visualize-price')
async def visualize_rent(city, state):
    """
    Visualize Rental Price Historical and Forecast date per City/State

    ### Response
    JSON string to render with react-plotly.js
    """

    city = city.lower().title()
    state = state.lower().title()

    subset_hist = df_cities_historical[df_cities_historical['city'] == city]
    subset_avg = avg_hist[avg_hist['state'] == state]
    subset_forecast = df_cities_forecast[df_cities_forecast['city'] == city]
    subset_state = df_states_forecast[df_states_forecast['state'] == state]

    fig = px.line(title=f'Rental Price in {city}, {state}')
    fig.add_scatter(x=subset_hist.index, y=subset_hist['price'],
                name='historical price', mode='lines', line=dict(color='blue', width=3))
    fig.add_scatter(x=subset_forecast['date'], y=subset_forecast['price'],
                name='forecast price', mode='lines', line=dict(color='red', width=3, dash='dot'))
    fig.add_scatter(x=subset_avg['date'], y=subset_avg['price'],
                name='historical average per state', line=dict(color='black', width=3))
    fig.add_scatter(x=subset_state['date'], y=subset_state['price'],
                name='forecast average per state', mode='lines', line=dict(color='gray', width=3, dash='dot'))
    fig.update_layout(xaxis=dict(range=['2018-01-01', '2022-12-01']))

    return fig.to_json()
