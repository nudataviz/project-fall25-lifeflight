from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from pathlib import Path
from config import config
from utils.getData import read_data
from utils.predicting.predict_demand import cross_validate_prophet
from utils.predicting.predict_demand import prophet_predict
from utils.predicting.predict_demand import extract_forecast_data
from utils.seasonality_1_2 import get_seasonality_heatmap
from utils.scenario.get_time_diff import get_time_diff_seconds

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS for cross-origin requests from frontend
CORS(app)

# ======== dashboard page =========

@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    """Get indicator data"""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', '4_kpi_dashboard', 'merge_oasis_master_202408.csv'))
    # total missions count
    total_missions = df['yearwithrc'].nunique()
    total_missions_formatted = f"{total_missions:,}" 
    # total cities covered
    total_cities_covered = df['PU City'].nunique()
    
    return jsonify({
        'status': 'success',
        'message': 'Indicator data fetched successfully',
        'data': {
            'total_missions': total_missions_formatted,
            'total_cities_covered': total_cities_covered,
        }
    })

# ======== dashboard page distribution =========
@app.route('/api/get_24hour_distribution', methods=['GET'])
def get_24hour_distribution():
    """Get 24 hour distribution data"""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', '4_kpi_dashboard', 'merge_oasis_master_202408.csv'))
    
    df['disptime_dt'] = pd.to_datetime(df['disptime'], errors='coerce', format='%m/%d/%Y %H:%M:%S')
    df['Hour'] = df['disptime_dt'].dt.hour
    df['Weekday'] = df['disptime_dt'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['Date'] = df['disptime_dt'].dt.date  # extract date to calculate daily average  
    
    df['response_time_seconds'] = get_time_diff_seconds(df, 'disptime', 'enrtime')
    df['response_time'] = df['response_time_seconds'] / 60.0 
    
    df = df[
        (df['Hour'].notna()) & 
        (df['response_time'].notna()) &
        (df['response_time'] >= 0) &
        (df['response_time'] < 500) 
    ].copy()
    
    # 24-hour mission distribution by hour
    count_df = df.groupby('Hour').size().reset_index(name='count')
    
    # weekly mission distribution by weekday, calculate average missions per day
    # first calculate total missions and number of days for each weekday
    weekday_stats = df.groupby('Weekday').agg({
        'Date': 'nunique',  # number of unique dates for this weekday
        'disptime_dt': 'count'  # total missions for this weekday
    }).reset_index()
    weekday_stats.columns = ['Weekday', 'day_count', 'total_count']
    weekday_stats['count'] = (weekday_stats['total_count'] / weekday_stats['day_count']).round(2)  # average missions per day
    
    # weekday name mapping (0=Monday, 6=Sunday)
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_stats['WeekdayName'] = weekday_stats['Weekday'].apply(lambda x: weekday_names[int(x)])
    
    # make sure all 7 days are in the result
    all_weekdays = pd.DataFrame({
        'Weekday': range(7),
        'WeekdayName': weekday_names
    })
    weekday_df = all_weekdays.merge(weekday_stats[['Weekday', 'count']], on='Weekday', how='left').fillna(0)
    
    # calculate response time stats: mean and std
    response_time_stats = df.groupby('Hour')['response_time'].agg([
        ('mean', 'mean'),
        ('std', 'std')
    ]).reset_index()
    
    all_hours = pd.DataFrame({'Hour': range(24)})
    count_df = all_hours.merge(count_df, on='Hour', how='left').fillna(0)
    response_time_df = all_hours.merge(response_time_stats, on='Hour', how='left').fillna(0)
    
    # calculate upper and lower bounds: mean ± std
    response_time_df['response_time'] = response_time_df['mean'].round(2)
    response_time_df['std'] = response_time_df['std'].fillna(0).round(2)
    response_time_df['upper'] = (response_time_df['mean'] + response_time_df['std']).round(2)
    response_time_df['lower'] = (response_time_df['mean'] - response_time_df['std']).round(2)
    # make sure lower bound is not negative
    response_time_df['lower'] = response_time_df['lower'].clip(lower=0)
    
    # convert data types
    count_df['Hour'] = count_df['Hour'].astype(int)
    count_df['count'] = count_df['count'].astype(int)
    weekday_df['Weekday'] = weekday_df['Weekday'].astype(int)
    weekday_df['count'] = weekday_df['count'].round(2)
    response_time_df['Hour'] = response_time_df['Hour'].astype(int)
    
    return jsonify({  
        'status': 'success',
        'data': {
            'hourly_distribution': count_df[['Hour', 'count']].to_dict(orient='records'),
            'weekday_distribution': weekday_df[['Weekday', 'WeekdayName', 'count']].to_dict(orient='records'),
            'response_time': response_time_df[['Hour', 'response_time', 'upper', 'lower', 'std']].to_dict(orient='records')
        }
    })

# ======== dashboard page mission count for each base =========
@app.route('/api/get_mission_count_for_each_base', methods=['GET'])
def get_mission_count_for_each_base():
    """Get mission count for each base"""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', '4_kpi_dashboard', 'merge_oasis_master_202408.csv'))
    df = df[df['lfomTransport (Did LFOM transport patient)'] == 'yes']
    df['base'] = df['airUnit'].fillna(df['groundUnit'])
    base_counts = df['base'].value_counts().sort_values(ascending=False)
    return jsonify({
        'status': 'success',
        'data': base_counts.to_dict()
    })
# ======== demand forecasting page =========
@app.route('/api/predict_demand_v2', methods=['POST'])
def predict_demand_v2():
    """Predict demand using Prophet model"""
    
    data = request.get_json() or {}
    
    periods = int(data.get('periods', 12)) 
    extra_vars = data.get('extra_vars', [])
    growth = data.get('growth', 'linear')
    yearly_seasonality = data.get('yearly_seasonality', True)
    seasonality_mode = data.get('seasonality_mode', 'additive')
    changepoint_prior_scale = float(data.get('changepoint_prior_scale', 0.05))
    seasonality_prior_scale = float(data.get('seasonality_prior_scale', 10.0))
    interval_width = float(data.get('interval_width', 0.95))
    regressor_prior_scale = float(data.get('regressor_prior_scale', 0.05))
    regressor_mode = data.get('regressor_mode', 'additive')
    
    backend_dir = Path(__file__).parent
    
    data_path = backend_dir / 'data' / '1_demand_forecasting' / '1_1_history_data_v2.csv'
    prophet_data = pd.read_csv(data_path)
    prophet_data['date'] = pd.to_datetime(prophet_data['date'])
    print(extra_vars)
    forecast, model, train_data = prophet_predict(
        data=prophet_data,
        freq='M', 
        extra_vars=extra_vars,
        periods=periods,
        growth=growth,
        yearly_seasonality=yearly_seasonality,
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        interval_width=interval_width,
        regressor_prior_scale=regressor_prior_scale,
        regressor_mode=regressor_mode,
        backend_dir=backend_dir
    )
    
    extracted_data = extract_forecast_data(forecast, train_data)
    cv_metrics = cross_validate_prophet(model, train_data)
    
    return jsonify({
        'status': 'success',
        'data': {
            'forecast_data': extracted_data['forecast_data'],
            'historical_actual': extracted_data['historical_actual'],
            'components': extracted_data['components'],
            'cv_metrics': cv_metrics
        }
    })


@app.route('/api/get_corr_matrix', methods=['GET'])
def get_corr_matrix():
    """Get correlation matrix data for visualization"""
    backend_dir = Path(__file__).parent
    corr_matrix_path = backend_dir / 'data' / '1_demand_forecasting' / '1_1_corr_matrix.csv'
    
    try:
        corr_matrix = pd.read_csv(corr_matrix_path, index_col=0)
        
        variables = corr_matrix.index.tolist()
        
        matrix_data = []
        for var in variables:
            row = []
            for col_var in variables:
                row.append(float(corr_matrix.loc[var, col_var]))
            matrix_data.append(row)
        
        count_correlations = {}
        if 'count' in corr_matrix.index:
            for var in variables:
                if var != 'count':
                    count_correlations[var] = float(corr_matrix.loc[var, 'count'])
        
        return jsonify({
            'status': 'success',
            'data': {
                'variables': variables,
                'matrix': matrix_data,
                'count_correlations': count_correlations
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to load correlation matrix: {str(e)}'
        }), 500

# ======== forecasting demand page - seasonality heatmap =========
@app.route('/api/seasonality_heatmap', methods=['GET'])
def get_seasonality_heatmap_api():
    try:
        year = int(request.args.get('year', 2023))
        location_level = request.args.get('location_level', 'system')
        location_value = request.args.get('location_value', None)
        month = request.args.get('month', None)
        
        if month:
            month = int(month)
            if month < 1 or month > 12:
                return jsonify({
                    'status': 'error',
                    'message': 'Month must be between 1 and 12'
                }), 400
        
        if year < 2012 or year > 2023:
            return jsonify({
                'status': 'error',
                'message': 'Year must be between 2012 and 2023'
            }), 400
        
        if location_level not in ['system', 'state', 'county', 'city']:
            return jsonify({
                'status': 'error',
                'message': 'location_level must be one of: system, state, county, city'
            }), 400
        
        result = get_seasonality_heatmap(year, location_level, location_value, month)
        
        heatmap_data = result['heatmap_data']
        metadata = result['metadata']
        
        if month is None:
            months_data = {}
            for item in heatmap_data:
                m = item['month']
                if m not in months_data:
                    months_data[m] = []
                months_data[m].append(item)
            
            month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            formatted_data = []
            for m in sorted(months_data.keys()):
                month_items = months_data[m]
                weekday_data = {}
                for item in month_items:
                    wd = item['weekday']
                    if wd not in weekday_data:
                        weekday_data[wd] = []
                    weekday_data[wd].append({
                        'hour': item['hour'],
                        'missions_per_1000': item['missions_per_1000'],
                        'count': item['count']
                    })
                
                heatmap_rows = []
                for wd in range(7): 
                    hour_values = weekday_data.get(wd, [])
                    hour_dict = {item['hour']: item for item in hour_values}
                    values = []
                    for h in range(24):
                        if h in hour_dict:
                            values.append({
                                'hour': h,
                                'missions_per_1000': hour_dict[h]['missions_per_1000'],
                                'count': hour_dict[h]['count']
                            })
                        else:
                            values.append({
                                'hour': h,
                                'missions_per_1000': 0,
                                'count': 0
                            })
                    heatmap_rows.append({
                        'weekday': wd,
                        'values': sorted(values, key=lambda x: x['hour'])
                    })
                
                formatted_data.append({
                    'month': m,
                    'month_name': month_names[m - 1],
                    'heatmap': heatmap_rows
                })
        else:
            month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            weekday_data = {}
            for item in heatmap_data:
                wd = item['weekday']
                if wd not in weekday_data:
                    weekday_data[wd] = []
                weekday_data[wd].append({
                    'hour': item['hour'],
                    'missions_per_1000': item['missions_per_1000'],
                    'count': item['count']
                })
            
            heatmap_rows = []
            for wd in range(7):
                hour_values = weekday_data.get(wd, [])
                hour_dict = {item['hour']: item for item in hour_values}
                values = []
                for h in range(24):
                    if h in hour_dict:
                        values.append({
                            'hour': h,
                            'missions_per_1000': hour_dict[h]['missions_per_1000'],
                            'count': hour_dict[h]['count']
                        })
                    else:
                        values.append({
                            'hour': h,
                            'missions_per_1000': 0,
                            'count': 0
                        })
                heatmap_rows.append({
                    'weekday': wd,
                    'values': sorted(values, key=lambda x: x['hour'])
                })
            
            formatted_data = [{
                'month': month,
                'month_name': month_names[month - 1],
                'heatmap': heatmap_rows
            }]
        
        all_values = [item['missions_per_1000'] for item in heatmap_data]
        peak_item = max(heatmap_data, key=lambda x: x['missions_per_1000']) if heatmap_data else None
        
        stats = {
            'total_missions': metadata['total_missions'],
            'avg_missions_per_1000': float(np.mean(all_values)) if all_values else 0,
            'max_missions_per_1000': float(np.max(all_values)) if all_values else 0,
            'min_missions_per_1000': float(np.min(all_values)) if all_values else 0,
            'peak_time': {
                'month': peak_item.get('month', month) if peak_item else None,
                'weekday': peak_item['weekday'] if peak_item else None,
                'hour': peak_item['hour'] if peak_item else None
            } if peak_item else None
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'heatmap_data': formatted_data,
                'metadata': metadata,
                'stats': stats
            }
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get seasonality heatmap: {str(e)}'
        }), 500
    
# ======== scenario modeling page - heatmap by base locations =========
@app.route('/api/heatmap_by_base', methods=['GET'])
def get_heatmap_by_base():
    """Get heatmap data by base locations"""
    try:
        dataset = request.args.get('dataset', 'Roux(2012-2023)')
        base_places = request.args.get('base_places', 'ALL')
        from utils.scenario.get_heatmap import get_heatmap_by_base_data
        
        # Get heatmap data
        map_data = get_heatmap_by_base_data(dataset, base_places)
        
        # Return JSON with heatmap data
        return jsonify({
            'status': 'success',
            'heatmap_data': map_data['heatmap_data']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate heatmap: {str(e)}'
        }), 500

@app.route('/api/get_master_response_time', methods=['GET'])
def get_master_response_time():
    """Get master data with response time"""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', '1_demand_forecasting', 'FlightTransportsMaster.csv'))
    # enrtime: vehicle departure time
    # atstime: vehicle arrival time at scene
    df = df[['enrtime', 'atstime','PU State','PU City','TASC Primary Asset ']]
    df = df[df['PU State'] == 'Maine']
    # only keep cities with more than 30 samples
    df = df[df['PU City'].isin(df['PU City'].value_counts().index[df['PU City'].value_counts() > 30])]
    df['time_diff_seconds'] = get_time_diff_seconds(df, 'enrtime', 'atstime')

    df['time_diff_minutes'] = (df['time_diff_seconds'] / 60).round(3)
    # df['time_diff_hours'] = (df['time_diff_minutes'] / 3600).round(3)

    # clean data
    df = df[(df['time_diff_seconds']>0) & (df['time_diff_minutes']<400)]
    df = df[df['TASC Primary Asset '].notna()]
    print(df['time_diff_minutes'].describe())


    df = df.replace({np.nan: None, pd.NA: None})
    
    data = df.to_dict(orient='records')

    for record in data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    return jsonify({
        'status': 'success',
        'data': data
    })


# ======== scenario modeling page - range map =========
@app.route('/api/get_range_map', methods=['GET'])
def get_range_map_api():
    """Get range map data (heatmap data and base locations) and statistics"""
    try:
        # Get parameters - baseValue can be multiple values
        base_value = request.args.getlist('baseValue')  # Use getlist for multiple values
        if not base_value:
            base_value = ['BANGOR', 'PORTLAND']  # Default
        
        radius = request.args.get('radius', 50.0, type=float)
        expected_time = request.args.get('expectedTime', 20.0, type=float)  # note: frontend sends expectedTime
        
        from utils.scenario.get_range_map import (
            get_range_map_data, 
            calculate_range_statistics
        )
        
        # Get map data (heatmap data and base locations)
        map_data = get_range_map_data(base_value, radius, expected_time)
        
        # Calculate statistics
        stats = calculate_range_statistics(base_value, radius, expected_time)
        
        # Return map data and statistics
        return jsonify({
            'status': 'success',
            'heatmap_data': map_data['heatmap_data'],
            'base_locations': map_data['base_locations'],
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get range map: {str(e)}'
        }), 500


# ======== scenario modeling page - special base evaluation =========
@app.route('/api/get_special_base_speeds', methods=['GET'])
def get_special_base_speeds():
    """Get median speeds for all special bases"""
    try:
        from utils.scenario.get_special_base_stats import calculate_special_base_speeds
        
        speeds = calculate_special_base_speeds()
        
        return jsonify({
            'status': 'success',
            'speeds': speeds
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get special base speeds: {str(e)}'
        }), 500


@app.route('/api/get_maine_cities', methods=['GET'])
def get_maine_cities():
    """Get list of Maine cities for dropdown selection"""
    try:
        from utils.heatmap import get_city_coordinates
        
        city_coords = get_city_coordinates(isOnlyMaine=True)
        cities = sorted(list(city_coords.keys()))
        
        return jsonify({
            'status': 'success',
            'cities': cities
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get cities: {str(e)}'
        }), 500


@app.route('/api/get_special_base_statistics', methods=['GET'])
def get_special_base_statistics():
    """Get statistics for a specific special base"""
    try:
        center_type = request.args.get('centerType')
        radius = request.args.get('radius', 50.0, type=float)
        expected_time = request.args.get('expectedTime', 20.0, type=float)
        base_cities_input = request.args.get('baseCities', None)  # comma-separated cities, includes default cities
        
        # parse and validate cities on backend
        valid_cities = []
        if base_cities_input:
            from utils.heatmap import get_city_coordinates
            city_coords = get_city_coordinates(isOnlyMaine=True)
            city_coords_set = set(city.upper().strip() for city in city_coords.keys())
            
            # parse comma-separated cities
            cities = base_cities_input.split(',')
            for city in cities:
                normalized = city.strip().upper()
                if normalized and normalized in city_coords_set:
                    valid_cities.append(normalized)
            # new cities list, all cities deduplicated
            valid_cities = list(set(valid_cities))
        
        if not center_type:
            return jsonify({
                'status': 'error',
                'message': 'centerType parameter is required'
            }), 400
        
        from utils.scenario.get_special_base_stats import (
            calculate_special_base_statistics,
        )
        from utils.scenario.get_range_map import get_range_map_data
        from utils.heatmap import get_city_coordinates
        from utils.getData import read_data
        
        # Determine which cities to use
        city_coords = get_city_coordinates(isOnlyMaine=True)
        df = read_data('FlightTransportsMaster.csv')
        df = df[df['PU State'] == 'Maine']
        if 'TASC Primary Asset ' in df.columns:
            df.rename(columns={'TASC Primary Asset ': 'TASC Primary Asset'}, inplace=True)
        df_center = df[df['TASC Primary Asset'] == center_type]
        
        # Get base cities: use valid_cities if provided, otherwise use main base city
        base_cities_list = []
        if valid_cities:
            base_cities_list = valid_cities
        elif len(df_center) > 0:
            city_counts = df_center['PU City'].value_counts(ascending=False)
            main_base_city = city_counts.index[0] if len(city_counts) > 0 else None
            if main_base_city:
                base_cities_list = [main_base_city]
        
        # Calculate statistics with all base cities
        stats = calculate_special_base_statistics(
            center_type, 
            radius, 
            expected_time,
            base_cities_list  # Pass list of cities
        )
        
        # Get map data (heatmap data and base locations) instead of HTML
        map_data = None
        if base_cities_list:
            map_data = get_range_map_data(base_cities_list, radius, expected_time, center_type)
        
        return jsonify({
            'status': 'success',
            'heatmap_data': map_data['heatmap_data'] if map_data else [],
            'base_locations': map_data['base_locations'] if map_data else [],
            'statistics': stats
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_special_base_statistics: {str(e)}")
        print(error_trace)
        return jsonify({
            'status': 'error',
            'message': f'Failed to get special base statistics: {str(e)}',
            'trace': error_trace
        }), 500
    

@app.route('/api/dashboard_info', methods=['GET'])
def get_dashboard_info():
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', '4_kpi_dashboard', 'merge_oasis_master_202408.csv'))
        print(df['Add Date'].head())
        df['Add Date'] = pd.to_datetime(df['Add Date'])
        df['Year'] = df['Add Date'].dt.year
        df['Month'] = df['Add Date'].dt.month
        # rename columns
        df.rename(columns={'responseDelay (Subjective and with no objective time for them to decide, none or select reason, just gustalt)':'responseDelay'},inplace=True)
        df.rename(columns={'transportByPrimaryQ (Did the appropriate asset transport the patient without delay)':'transportByPrimaryQ'},inplace=True)
        df.rename(columns={'appropriateAsset (Who should have gone if available)':'appropriateAsset'},inplace=True)
        df.rename(columns={'reasonL1NoResponse (L1 is Bangor RotorWing, L2 is Lewiston RW, L3 is Bangor FixedWing, L4 is Sanford RW) ':'reasonL1NoResponse'},inplace=True)
        
        # create base field (actual base that handled the mission)
        df['base'] = df['airUnit'].fillna(df['groundUnit'])
        
        df['responseDelay'] = df['responseDelay'].fillna('')
        df['delay_list'] = df['responseDelay'].str.split('|')
        
        # process respondingAssets, split pipe-separated values into list
        # df['respondingAssets'] = df['respondingAssets'].fillna('')
        df['respondingAssets_list'] = df['airUnit'].fillna(df['groundUnit'])
        
        df = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})

        # first explode respondingAssets_list
        df_exp = df.explode('respondingAssets_list')
        # then explode delay_list
        df_exp = df_exp.explode('delay_list')
        # df_exp = df_exp[(df_exp['delay_list'] != '')&(df_exp['delay_list']!='noDelays')]
        delay_reason_counts = (
            df_exp['delay_list']
            .value_counts()
            .reset_index()
        )
        delay_reason_counts.columns = ['reason', 'count']
        print(delay_reason_counts.head())
        df_delay_reason = df_exp.groupby(['delay_list','respondingAssets_list']).size().reset_index(name='count')
        delayData = df_exp.groupby(['respondingAssets_list','transportByPrimaryQ']).size().reset_index(name='count')
        # rename columns to match frontend expectations
        delayData.rename(columns={'respondingAssets_list': 'respondingAssets'}, inplace=True)
        df_delay_reason.rename(columns={'respondingAssets_list': 'respondingAssets'}, inplace=True)


        # count missions where appropriateAsset != base (not completed as expected)
        df_base_count = df.groupby(['appropriateAsset','base']).size().reset_index(name='count')
        df_base_count = df_base_count[df_base_count['appropriateAsset'] != df_base_count['base']]
        
        # calculate total expected missions per base (grouped by appropriateAsset)
        df_expected_total = df.groupby(['appropriateAsset']).size().reset_index(name='total_count')
        
        # calculate missions completed as expected (appropriateAsset == base)
        df_completed_as_expected = df[df['appropriateAsset'] == df['base']].groupby(['appropriateAsset']).size().reset_index(name='completed_count')
        
        # merge data
        df_expected_stats = df_expected_total.merge(
            df_completed_as_expected, 
            on='appropriateAsset', 
            how='left'
        ).fillna(0)
        
        # make sure completed_count is integer
        df_expected_stats['completed_count'] = df_expected_stats['completed_count'].astype(int)
        df_expected_stats['total_count'] = df_expected_stats['total_count'].astype(int)
        
        print("Expected stats:")
        print(df_expected_stats.head())
        
        # count no-response reasons for each base
        no_response_fields = ['reasonL1NoResponse', 'reasonL2NoResponse', 'reasonL3NoResponse', 'reasonL4NoResponse2']
        base_no_response_reasons = {}
        
        # field to base name mapping
        field_to_base = {
            'reasonL1NoResponse': 'LF1',
            'reasonL2NoResponse': 'LF2',
            'reasonL3NoResponse': 'LF3',
            'reasonL4NoResponse2': 'LF4'
        }
        
        for field in no_response_fields:
            # check if field exists
            if field not in df.columns:
                print(f"Warning: Field {field} not found in dataframe")
                continue
                
            # get base name
            base_name = field_to_base.get(field, 'Unknown')
            
            # fill empty values
            df[field] = df[field].fillna('')
            
            # split pipe-separated reasons
            df_field_expanded = df[df[field] != ''].copy()
            
            if len(df_field_expanded) == 0:
                print(f"No data for {field}")
                continue
                
            df_field_expanded['reason_list'] = df_field_expanded[field].str.split('|')
            df_field_expanded = df_field_expanded.explode('reason_list')
            
            # remove base number prefix from reasons (e.g., 1tasked -> tasked, 2oosMedic -> oosMedic)
            df_field_expanded['reason_clean'] = df_field_expanded['reason_list'].str.replace(r'^[1-4]', '', regex=True)
            df_field_expanded['reason_clean'] = df_field_expanded['reason_clean'].str.strip()
            
            # filter out empty values
            df_field_expanded = df_field_expanded[df_field_expanded['reason_clean'] != '']
            
            if len(df_field_expanded) == 0:
                continue
            
            # count reasons
            reason_counts = df_field_expanded['reason_clean'].value_counts().reset_index()
            reason_counts.columns = ['reason', 'count']
            reason_counts['base'] = base_name
            
            if base_name not in base_no_response_reasons:
                base_no_response_reasons[base_name] = []
            base_no_response_reasons[base_name] = reason_counts.to_dict(orient='records')
        
        # convert to list format for frontend
        no_response_data = []
        for base, reasons in base_no_response_reasons.items():
            no_response_data.extend(reasons)
        
        print("No response reasons stats:")
        if len(no_response_data) > 0:
            print(pd.DataFrame(no_response_data).head(20))
        else:
            print("No response reasons data found")
        
        return jsonify({
            'status': 'success',
            'data': df.to_dict(orient='records'),
            'delayData':delayData.to_dict(orient='records'),
            'delayReasonData':delay_reason_counts.to_dict(orient='records'),
            'expectedCompletionData': df_expected_stats.to_dict(orient='records'),
            'noResponseReasonsData': no_response_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get test data: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

