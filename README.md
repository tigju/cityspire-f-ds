#### All data for rental prices, crime data, population and walkability score is stored in RDS Postgres database on AWS.
#### Api endpoints retrieves data from database, except for linear prediction. 

### Endpoints:

*GET:*

**/rental-historical-data**  (Fetches all historical rental data for 2014-2020 years)

**/rental-forecast-cities**  (Fetches all rental data forecasted for next 2 years)

**/rental-forecast-states**  (Fetches rental price average per state forecasted for next 2 years)

**/walkability-score**       (Fetches all walkability data)

**/crime-rate**              (Fetches crime data for 10 cities)

*POST:*

**/predict**                 (Fetches all data (rental price, walkability, crime rate, population) per city/state and combines it in one endpoint)  

**/rent_linear_prediction** (Forecast apartment rent for 3, 6, 12 months This is just Linear model. It won't show great forecast accuracy Created to determine base line and for test purposes)

**/visualize-price**        (Visualize Rental Price Historical and Forecast date per City/State)
