"""Machine learning functions"""

from fastapi import APIRouter
from joblib import load
import pandas as pd
from pydantic import BaseModel, PositiveFloat, PositiveInt

from datetime import datetime
from dateutil.relativedelta import *
from sklearn.preprocessing import OrdinalEncoder
from sklearn.linear_model import LinearRegression


router = APIRouter()

# getting data for transforming purpose
data = pd.read_csv('notebooks/rentals/data/test.csv')
# load linear regression pickle
linear_model = load('notebooks/rentals/rental_model.joblib')
# load OrdinalEncoder pickle
encoder = load('notebooks/rentals/encoder.joblib')


class Rent(BaseModel):
    """Parse and validate apartment info"""
    city: str
    state: str


@router.post('/rent_linear_prediction')
async def linear_predict(rent: Rent):
    """
    Forecast apartment rent for 3, 6, 12 months 
    This is just Linear model. It won't show great forecast accuracy 
    Created to determine base line and for test purposes.
    """
    city = rent.city.lower().title()
    state = rent.state.lower().title()

    now = datetime.today()
    # get date 3 months, 6 months, 12 months in the future for our forecasting
    month_3 = now + relativedelta(months=+3)
    month_6 = now + relativedelta(months=+6)
    month_12 = now + relativedelta(months=+12)

    # create 4 separate dfs based on data provided for linear regression model
    df0 = pd.DataFrame(
        data={"Month": now.month, "Year": now.year, "City": city}, index=[0])

    df1 = pd.DataFrame(data={"Month": month_3.month,
                             "Year": month_3.year, "City": city}, index=[0])

    df2 = pd.DataFrame(data={"Month": month_6.month,
                             "Year": month_6.year, "City": city}, index=[0])

    df3 = pd.DataFrame(data={"Month": month_12.month,
                             "Year": month_12.year, "City": city}, index=[0])

    # create dummy variables for cities
    dum_data0 = pd.get_dummies(df0, prefix=[""], prefix_sep="", columns=[
                               "City"], drop_first=False)
    dum_data1 = pd.get_dummies(df1, prefix=[""], prefix_sep="", columns=[
                               "City"], drop_first=False)
    dum_data2 = pd.get_dummies(df2, prefix=[""], prefix_sep="", columns=[
                               "City"], drop_first=False)
    dum_data3 = pd.get_dummies(df3, prefix=[""], prefix_sep="", columns=[
                               "City"], drop_first=False)

    # encode state variable
    encoded_state = encoder.transform([[state]])
    dum_data0["Encoded_States"] = encoded_state
    dum_data1["Encoded_States"] = encoded_state
    dum_data2["Encoded_States"] = encoded_state
    dum_data3["Encoded_States"] = encoded_state

    # get the data excluding target (just to get columns names later)
    X_data = data.drop(columns=['Price'])
    # get missing columns
    missing_cols = set(X_data.columns) - set(dum_data1.columns)

    # fill up dataframe with missing colunmns
    for c in missing_cols:
        dum_data0[c] = 0
        dum_data1[c] = 0
        dum_data2[c] = 0
        dum_data3[c] = 0

    # Ensure the order of columns in the dataframes is the same as in data
    dum_data0 = dum_data0[X_data.columns]
    dum_data1 = dum_data1[X_data.columns]
    dum_data2 = dum_data2[X_data.columns]
    dum_data3 = dum_data3[X_data.columns]

    # predict prices 
    pred0 = float(linear_model.predict(dum_data0)[0])
    pred1 = float(linear_model.predict(dum_data1)[0])
    pred2 = float(linear_model.predict(dum_data2)[0])
    pred3 = float(linear_model.predict(dum_data3)[0])

    # get historical data
    sub = data[(data[city] == 1) & (data["Year"] == 2020)]
    date_col = pd.to_datetime(sub[['Year', 'Month']].assign(DAY=1))
    sub["date"] = date_col.apply(lambda x: x.date().strftime("%Y-%m-%d"))
    sub.index = pd.RangeIndex(start=1, stop=12, step=1)
    last_year_price = sub[["date", "Price"]].to_dict(orient="index")

    a = {"city": city, "price": {"historical": last_year_price,
                                 "today": {"price": pred0, "date": str(now.date())},
                                 "forecast_3": {"price": pred1, "date": str(month_3.date())},
                                 "forecast_6": {"price": pred2, "date": str(month_6.date())},
                                 "forecast_12": {"price": pred3, "date": str(month_12.date())}}}
    
    return a
