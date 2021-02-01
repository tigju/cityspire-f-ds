"""Machine learning functions"""

from fastapi import APIRouter
from joblib import load
import pandas as pd
from pydantic import BaseModel, PositiveFloat, PositiveInt

router = APIRouter()
model = load('app/model.joblib')
print(f'Scikit-learn model of type {type(model)} was loaded')

class Apartment(BaseModel):
    """Parse and validate apartment info"""
    beds: PositiveInt
    baths: PositiveFloat
    
    def to_df(self):
        """Convert to pandas dataframe with 1 row"""
        return pd.DataFrame([dict(self)])

@router.post('/predict_rent')
async def rent(apartment: Apartment):
    """
    Predict apartment rent from number of beds & baths 
    """
    price = model.predict(apartment.to_df())
    return {'predicted_price': price[0]}

