# backend/utils/predicting/predict_demand.py
import joblib
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from prophet import Prophet


def prophet_predict(data: pd.DataFrame, freq: str = 'M',
                    extra_vars: list[str] = [],
                    periods: int = 12, # use the number of months to predict
                    growth: str = 'linear',
                    yearly_seasonality: bool = True,
                    seasonality_mode: str = 'additive', # seasonality mode, additive or multiplicative
                    changepoint_prior_scale: float = 0.05, # large value means more sensitive, may overfit
                    seasonality_prior_scale: float = 10.0, 
                    interval_width: float = 0.95,
                    regressor_prior_scale: float = 0.05, # larger will be more sensitive
                    regressor_mode: str = 'additive',
                    backend_dir: Path = None,
                    ):

    train_data = data[data['count'].notna()].copy()
    future_data = data[data['count'].isna()].copy()
    prophet_data = train_data[['date', 'count']].copy()
    prophet_data.columns = ['ds', 'y']
    
    # if periods > 12 and backend_dir is not None, read future data file
    if periods > 12 and backend_dir is not None:
        import math
        last_train_date = prophet_data['ds'].max()
        start_year = 2024  # start
        years_needed = math.ceil(periods / 12)  
        end_year = start_year + years_needed - 1  
        
        
        required_years = list(range(2025, end_year + 1))
        
        future_pop_path = backend_dir / 'data' / '1_demand_forecasting' / '1_1_future_pop.csv'
        if future_pop_path.exists():
            future_pop_df = pd.read_csv(future_pop_path)
            future_pop_df = future_pop_df[
                future_pop_df['year'].isin(required_years)
            ].copy()
            
            if len(future_pop_df) == 0:
                raise ValueError(
                    f"No data found for {required_years} in future data file."
                )
            
            future_pop_df['date'] = pd.to_datetime(
                future_pop_df[['year', 'month']].assign(day=1)
            )
            
            # merge to future_data
            if len(future_data) > 0:
                future_data_2024 = future_data[
                    pd.to_datetime(future_data['date']).dt.year == 2024
                ].copy()
                future_data = pd.concat([
                    future_data_2024,
                    future_pop_df[['date'] + [col for col in future_pop_df.columns if col not in ['date', 'year', 'month', 'NAME', 'state']]]
                ], ignore_index=True)
            else:
                future_data = future_pop_df[['date'] + [col for col in future_pop_df.columns if col not in ['date', 'year', 'month', 'NAME', 'state']]].copy()
            
            if 'count' not in future_data.columns:
                future_data['count'] = pd.NA
        else:
            raise FileNotFoundError(
                f"Future data file not found: {future_pop_path}"
            )
    
    # if logistic growth, add cap column
    if growth == 'logistic':
        max_value = prophet_data['y'].max()
        cap_value = max_value * 1.5 # default value is 1.5
        prophet_data['cap'] = cap_value
    
    # extra variables
    if extra_vars:
        for var in extra_vars:
            if var in train_data.columns:
                prophet_data[var] = pd.to_numeric(train_data[var], errors='coerce')
            else:
                print(f"Variable '{var}' not found in data, skipping.")
    model = Prophet(
        growth=growth,
        yearly_seasonality=yearly_seasonality,
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        interval_width=interval_width,
    )
    # add regressors
    if extra_vars:
        for var in extra_vars:
            if var in prophet_data.columns:
                model.add_regressor(
                    var,
                    prior_scale=regressor_prior_scale,
                    mode=regressor_mode
                )
    model.fit(prophet_data)

    # create future dataframe 
    if len(future_data) > 0:
        last_train_date = prophet_data['ds'].max()
        last_future_date = future_data['date'].max()
        months_needed = (last_future_date.year - last_train_date.year) * 12 + \
                       (last_future_date.month - last_train_date.month)
        # if periods > 12, use the maximum range of future_data; otherwise, only predict the specified number of months
        if periods > 12:
            periods = max(periods, months_needed)
        else:
            # only predict one year, no data after 2025 in future_data
            periods = min(periods, 12)
    
    # use make_future_dataframe to create future dataframe with history data
    future = model.make_future_dataframe(periods=periods, freq=freq)
    
    future['ds'] = future['ds'].dt.to_period('M').dt.start_time
    
    # if logistic growth, add cap to future
    if growth == 'logistic':
        if 'cap' in prophet_data.columns:
            cap_value = prophet_data['cap'].iloc[0] 
            future['cap'] = cap_value
    
    # add regressors to future
    if extra_vars:
        for var in extra_vars:
            if var in prophet_data.columns:
                var_values = {}
                
                for _, row in prophet_data.iterrows():
                    var_values[row['ds']] = row[var]
                
                if len(future_data) > 0:
                    for _, row in future_data.iterrows():
                        var_values[pd.Timestamp(row['date'])] = pd.to_numeric(row[var], errors='coerce')
                
                last_val = prophet_data[var].iloc[-1]
                future[var] = future['ds'].apply(
                    lambda x: var_values.get(x, last_val) if x in var_values else last_val
                )

    forecast = model.predict(future)
    return forecast, model, prophet_data


def prepare_prophet_data(backend_dir: Path) -> pd.DataFrame:
    data_path = backend_dir / 'data' / '1_demand_forecasting' / 'data.csv'
    df = pd.read_csv(data_path, encoding='latin1')
    
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df = df[df['tdate'].notna()]
    df = df[df['tdate'] >= '2013-01-01']
    
    monthly_data = df.groupby(df['tdate'].dt.to_period('M')).size().reset_index(name='count')
    monthly_data['date'] = monthly_data['tdate'].astype(str) + '-01'
    monthly_data['date'] = pd.to_datetime(monthly_data['date'])
    monthly_data = monthly_data[['date', 'count']].sort_values('date').reset_index(drop=True)
    
    pop_monthly_path = backend_dir / 'data' / '1_demand_forecasting' / 'acs1_population_2013_2023_age_group.csv'
    if pop_monthly_path.exists():
        pop_monthly = pd.read_csv(pop_monthly_path)
        if 'date' in pop_monthly.columns:
            pop_monthly['date'] = pd.to_datetime(pop_monthly['date'])
            # Merge population data
            monthly_data = monthly_data.merge(
                pop_monthly,
                on='date',
                how='left'
            )
    
    return monthly_data


def extract_forecast_data(forecast: pd.DataFrame, train_data: pd.DataFrame) -> Dict[str, Any]:
    forecast_data = []
    for _, row in forecast.iterrows():
        forecast_data.append({
            'date': row['ds'].strftime('%Y-%m-%d'),
            'predicted': float(row['yhat']),
            'lower': float(row['yhat_lower']),
            'upper': float(row['yhat_upper'])
        })
    
    historical_actual = []
    for _, row in train_data.iterrows():
        historical_actual.append({
            'date': row['ds'].strftime('%Y-%m-%d'),
            'actual': float(row['y'])
        })
    
    
    components = {}
    
    # Trend
    if 'trend' in forecast.columns:
        components['trend'] = [
            {'date': row['ds'].strftime('%Y-%m-%d'), 'value': float(row['trend'])}
            for _, row in forecast.iterrows()
        ]
    
    # Yearly seasonality
    if 'yearly' in forecast.columns:
        components['yearly'] = [
            {'date': row['ds'].strftime('%Y-%m-%d'), 'value': float(row['yearly'])}
            for _, row in forecast.iterrows()
        ]
    # Extra regressors
    extra_regressors = {}
    excluded_cols = ['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend', 'yearly', 'weekly', 'daily', 
                     'additive_terms', 'multiplicative_terms', 'y']
    for col in forecast.columns:
        if col not in excluded_cols and col in train_data.columns:
            var_name = col
            extra_regressors[var_name] = [
                {'date': row['ds'].strftime('%Y-%m-%d'), 'value': float(row[col])}
                for _, row in forecast.iterrows()
            ]
    
    if extra_regressors:
        components['extra_regressors'] = extra_regressors
    
    return {
        'forecast_data': forecast_data,
        'historical_actual': historical_actual,
        'components': components
    }


def cross_validate_prophet(model: Prophet, prophet_data: pd.DataFrame) -> Dict[str, Any]:
    """
    for cross validation of Prophet model
    """
    from prophet.diagnostics import cross_validation, performance_metrics
    
    # cross validation
    df_cv = cross_validation(
        model,
        initial='730 days',  # 2 years
        period='365 days',   # 1 year
        horizon='365 days'   # 1 year
    )
    
    df_p = performance_metrics(df_cv)
    
    # extract average metrics
    metrics = {
        'mape': float(df_p['mape'].mean()),
        'mae': float(df_p['mae'].mean()),
        'rmse': float(df_p['rmse'].mean()),
        'coverage': float(df_p['coverage'].mean()) if 'coverage' in df_p.columns else None
    }
    
    return metrics
