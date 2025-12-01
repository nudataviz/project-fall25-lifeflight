from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from pathlib import Path
from config import config
from utils.heatmap import generate_city_demand_heatmap, map_to_html
from utils.getData import read_data
from utils.responseTime import calculate_response_time
from utils.veh_count import calculate_veh_count
from utils.predicting.predict_demand import cross_validate_prophet
from utils.predicting.predict_demand import prophet_predict
from utils.predicting.predict_demand import extract_forecast_data
from utils.predicting.predict_demand import cross_validate_prophet
from utils.seasonality_1_2 import get_seasonality_heatmap
from utils.demographics_1_3 import get_demographics_elasticity
from utils.event_impact_1_4 import get_event_impact_analysis, get_all_events
from utils.weather_risk_2_4 import get_weather_risk_analysis
from utils.scenario_whatif_2_1 import simulate_scenario, get_base_locations, compare_scenarios
from utils.scenario.get_boxplot_2_1 import get_boxplot
from utils.pareto_sensitivity_2_3 import get_pareto_sensitivity_analysis
from utils.base_siting_2_2 import get_base_siting_analysis
from utils.kpi_bullets_4_1 import get_kpi_bullets
from utils.trend_wall_4_2 import get_trend_wall_data
from utils.cost_benefit_4_3 import get_cost_benefit_throughput_data
from utils.safety_spc_4_4 import get_safety_spc_data
from utils.scenario.get_time_diff import get_time_diff_seconds

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS for cross-origin requests from frontend
CORS(app)

@app.route('/api/veh_count', methods=['GET'])
def get_veh_count():
    """Get veh count data"""
    df = read_data()
    veh_count = calculate_veh_count(df,2023)
    
    # Map vehicle codes to names
    veh_name_map = {
        'LF1': 'Helicopter based out of Bangor',
        'LF2': 'Helicopter based out of Lewiston',
        'LF3': 'Airplane based out of Bangor',
        'LF4': 'Helicopter based out of Sanford'
    }
    
    # Transform data to include vehicle names
    for item in veh_count:
        veh_code = item['id']
        if veh_code in veh_name_map:
            item['id'] = f"{veh_name_map[veh_code]} ({veh_code})"
    
    return jsonify({
        'status': 'success',
        'message': 'Veh count data fetched successfully',
        'data': veh_count
    })

# ======== dashboard page =========
@app.route('/api/heatmap',methods=['GET'])
def get_heatmap():
    """Get heatmap visualization"""
    df = read_data()
    map_obj = generate_city_demand_heatmap(df)
    html_map = map_to_html(map_obj)

    return html_map

@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    """Get indicator data"""
    df = read_data()
    # 1 total missions
    total_missions = df['yearwithrc'].nunique()
    total_missions_formatted = f"{total_missions:,}" 
    # 2 Total Cities Covered
    total_cities_covered = df['PU City'].nunique()
    # 3 Monthly Average Response Time
    mart_str = calculate_response_time(df,2023,12)
    # 4 Yearly Average Response Time
    yart_str = calculate_response_time(df,2023)
    
    def extract_minutes_seconds(timedelta_str):
        if timedelta_str == "N/A":
            return "N/A"
        try:
            td = pd.Timedelta(timedelta_str)
            total_seconds = int(td.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes} min {seconds} sec"
        except:
            return "N/A"
    
    mart = extract_minutes_seconds(mart_str)
    yart = extract_minutes_seconds(yart_str)
    
    return jsonify({
        'status': 'success',
        'message': 'Indicator data fetched successfully',
        'data': {
            'total_missions': total_missions_formatted,
            'total_cities_covered': total_cities_covered,
            'mart': mart,
            'yart': yart
        }
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
    """Get heatmap by base locations"""
    try:
        dataset = request.args.get('dataset', 'Roux(2012-2023)')
        base_places = request.args.get('base_places', 'ALL')
        from utils.scenario.get_heatmap import generate_heatmap_by_base
        
        # Generate heatmap HTML
        html_map = generate_heatmap_by_base(dataset, base_places)
        
        # Return HTML
        return html_map
        
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
    # 只留有10个样本以上的城市：
    df = df[df['PU City'].isin(df['PU City'].value_counts().index[df['PU City'].value_counts() > 30])]
    df['time_diff_seconds'] = get_time_diff_seconds(df, 'enrtime', 'atstime')

    df['time_diff_minutes'] = (df['time_diff_seconds'] / 60).round(3)
    # df['time_diff_hours'] = (df['time_diff_minutes'] / 3600).round(3)

    #clean
    df = df[(df['time_diff_seconds']>0) & (df['time_diff_minutes']<400)]
    df = df[df['TASC Primary Asset '].notna()]
    print(df['time_diff_minutes'].describe())


    # Replace NaN with None for JSON serialization
    df = df.replace({np.nan: None, pd.NA: None})
    
    # Convert to dict and handle NaN values
    data = df.to_dict(orient='records')
    
    # Additional cleanup: replace any remaining NaN/NaT values
    for record in data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/hourly_departure', methods=['GET'])
def get_hourly_departure():
    """Get hourly departure density data"""
    
    df = read_data()
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['Year'] = df['tdate'].dt.year
    df = df[df['Year'] == 2023]

    df['enrtime_dt'] = pd.to_datetime(df['enrtime'], errors='coerce').dt.time
    df.dropna(subset=['enrtime_dt'], inplace=True)
    df['enr_hour'] = pd.to_datetime(df['enrtime_dt'].astype(str)).dt.hour
    
    def get_season(month):
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Autumn'
        else:
            return 'Winter'
    
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['season'] = df['tdate'].dt.month.apply(get_season)
    
    all_hours = list(range(24))
    
    overall_counts = df['enr_hour'].value_counts().sort_index()
    overall_density = overall_counts / overall_counts.sum()
    
    overall_data = []
    for hour in all_hours:
        count = int(overall_counts.get(hour, 0))
        density = float(overall_density.get(hour, 0))
        overall_data.append({
            'hour': hour,
            'count': count,
            'density': density
        })
    
    
    season_data = {}
    for season in ['Spring', 'Summer', 'Autumn', 'Winter']:
        season_df = df[df['season'] == season]
        season_counts = season_df['enr_hour'].value_counts().sort_index()
        season_density = season_counts / season_counts.sum()
        
        season_hourly = []
        for hour in all_hours:
            count = int(season_counts.get(hour, 0))
            density = float(season_density.get(hour, 0))
            season_hourly.append({
                'hour': hour,
                'count': count,
                'density': density
            })
        season_data[season] = season_hourly
    
    return jsonify({
        'status': 'success',
        'data': {
            'overall': overall_data,
            'by_season': season_data
        }
    })



@app.route('/api/demographics_elasticity', methods=['GET'])
def get_demographics_elasticity_api():
    try:
        year = int(request.args.get('year', 2023))
        start_year = request.args.get('start_year_for_growth', None)
        end_year = request.args.get('end_year_for_growth', None)
        independent_vars_str = request.args.get('independent_vars', 'pct_65plus,growth_rate')
        
        if start_year:
            start_year = int(start_year)
        if end_year:
            end_year = int(end_year)
        
        independent_vars = [v.strip() for v in independent_vars_str.split(',')]
        
        if year < 2012 or year > 2023:
            return jsonify({
                'status': 'error',
                'message': 'Year must be between 2012 and 2023'
            }), 400
        
        result = get_demographics_elasticity(
            year=year,
            start_year_for_growth=start_year,
            end_year_for_growth=end_year,
            independent_vars=independent_vars
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get demographics elasticity data: {str(e)}'
        }), 500

@app.route('/api/event_impact', methods=['GET'])
def get_event_impact_api():
    try:
        event_id = request.args.get('event_id', None)
        
        if not event_id:
            return jsonify({
                'status': 'error',
                'message': 'event_id is required'
            }), 400
        
        location_level = request.args.get('location_level', 'county')
        location_value = request.args.get('location_value', None)
        window_months = int(request.args.get('window_months', 12))
        
        if location_level not in ['county', 'city', 'system']:
            return jsonify({
                'status': 'error',
                'message': 'location_level must be county, city, or system'
            }), 400
        
        if window_months < 1 or window_months > 24:
            return jsonify({
                'status': 'error',
                'message': 'window_months must be between 1 and 24'
            }), 400
        
        result = get_event_impact_analysis(
            event_id=event_id,
            location_level=location_level,
            location_value=location_value,
            window_months=window_months
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get event impact data: {str(e)}'
        }), 500


@app.route('/api/events', methods=['GET'])
def get_events_api():
    try:
        events = get_all_events()
        return jsonify({
            'status': 'success',
            'data': events
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get events: {str(e)}'
        }), 500

@app.route('/api/scenario_simulate', methods=['POST'])
def simulate_scenario_api():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        fleet_size = int(data.get('fleet_size', 3))
        crews_per_vehicle = int(data.get('crews_per_vehicle', 2))
        base_locations = data.get('base_locations', ['BANGOR'])
        missions_per_vehicle_per_day = int(data.get('missions_per_vehicle_per_day', 3))
        service_radius_miles = float(data.get('service_radius_miles', 50.0))
        sla_target_minutes = int(data.get('sla_target_minutes', 20))
        base_operational_cost_per_year = float(data.get('base_operational_cost_per_year', 500000.0))
        vehicle_cost_per_year = float(data.get('vehicle_cost_per_year', 100000.0))
        crew_cost_per_year = float(data.get('crew_cost_per_year', 80000.0))
        
        if fleet_size < 1 or fleet_size > 20:
            return jsonify({
                'status': 'error',
                'message': 'fleet_size must be between 1 and 20'
            }), 400
        
        if crews_per_vehicle < 1 or crews_per_vehicle > 5:
            return jsonify({
                'status': 'error',
                'message': 'crews_per_vehicle must be between 1 and 5'
            }), 400
        
        if service_radius_miles < 10 or service_radius_miles > 200:
            return jsonify({
                'status': 'error',
                'message': 'service_radius_miles must be between 10 and 200'
            }), 400
        
        if sla_target_minutes < 5 or sla_target_minutes > 60:
            return jsonify({
                'status': 'error',
                'message': 'sla_target_minutes must be between 5 and 60'
            }), 400
        
        result = simulate_scenario(
            fleet_size=fleet_size,
            missions_per_vehicle_per_day=missions_per_vehicle_per_day,
            crews_per_vehicle=crews_per_vehicle,
            base_locations=base_locations,
            service_radius_miles=service_radius_miles,
            sla_target_minutes=sla_target_minutes,
            base_operational_cost_per_year=base_operational_cost_per_year,
            vehicle_cost_per_year=vehicle_cost_per_year,
            crew_cost_per_year=crew_cost_per_year
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to simulate scenario: {str(e)}'
        }), 500


@app.route('/api/boxplot', methods=['GET'])
def get_boxplot_api():
    try:
        result = get_boxplot()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get boxplot: {str(e)}'
        }), 500

@app.route('/api/base_locations', methods=['GET'])
def get_base_locations_api():
    try:
        bases = get_base_locations()
        return jsonify({
            'status': 'success',
            'data': bases
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get base locations: {str(e)}'
        }), 500


@app.route('/api/scenario_compare', methods=['POST'])
def compare_scenarios_api():
    try:
        data = request.get_json()
        
        if not data or 'scenarios' not in data:
            return jsonify({
                'status': 'error',
                'message': 'scenarios array is required'
            }), 400
        
        scenarios_list = data['scenarios']
        
        if len(scenarios_list) < 1:
            return jsonify({
                'status': 'error',
                'message': 'At least one scenario is required'
            }), 400
        
        simulated_scenarios = []
        for scenario_params in scenarios_list:
            result = simulate_scenario(
                fleet_size=int(scenario_params.get('fleet_size', 3)),
                missions_per_vehicle_per_day=int(scenario_params.get('missions_per_vehicle_per_day', 3)),
                crews_per_vehicle=int(scenario_params.get('crews_per_vehicle', 2)),
                base_locations=scenario_params.get('base_locations', ['BANGOR']),
                service_radius_miles=float(scenario_params.get('service_radius_miles', 50.0)),
                sla_target_minutes=int(scenario_params.get('sla_target_minutes', 20)),
                base_operational_cost_per_year=float(scenario_params.get('base_operational_cost_per_year', 500000.0)),
                vehicle_cost_per_year=float(scenario_params.get('vehicle_cost_per_year', 100000.0)),
                crew_cost_per_year=float(scenario_params.get('crew_cost_per_year', 80000.0))
            )
            simulated_scenarios.append(result)
        
        # Compare scenarios
        comparison = compare_scenarios(simulated_scenarios)
        
        return jsonify({
            'status': 'success',
            'data': {
                'comparison': comparison,
                'scenarios': simulated_scenarios
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to compare scenarios: {str(e)}'
        }), 500

@app.route('/api/pareto_sensitivity', methods=['GET', 'POST'])
def get_pareto_sensitivity_api():
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        base_locations = data.get('base_locations', ['BANGOR', 'PORTLAND'])
        if isinstance(base_locations, str):
            base_locations = [b.strip() for b in base_locations.split(',')]
        
        radius_min = float(data.get('radius_min', 20))
        radius_max = float(data.get('radius_max', 100))
        radius_step = float(data.get('radius_step', 10))
        sla_min = int(data.get('sla_min', 10))
        sla_max = int(data.get('sla_max', 30))
        sla_step = int(data.get('sla_step', 5))
        fleet_size = int(data.get('fleet_size', 3))
        crews_per_vehicle = int(data.get('crews_per_vehicle', 2))
        missions_per_vehicle_per_day = int(data.get('missions_per_vehicle_per_day', 3))
        
        weights = data.get('weights')
        if isinstance(weights, dict):
            total = sum(weights.values())
            if total > 0:
                weights = {k: v / total for k, v in weights.items()}
        
        result = get_pareto_sensitivity_analysis(
            base_locations=base_locations,
            radius_min=radius_min,
            radius_max=radius_max,
            radius_step=radius_step,
            sla_min=sla_min,
            sla_max=sla_max,
            sla_step=sla_step,
            fleet_size=fleet_size,
            crews_per_vehicle=crews_per_vehicle,
            missions_per_vehicle_per_day=missions_per_vehicle_per_day,
            weights=weights
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get Pareto sensitivity analysis: {str(e)}'
        }), 500

# ======== scenario modeling page - range map =========
@app.route('/api/get_range_map', methods=['GET'])
def get_range_map_api():
    """Get range map with heatmap, service radius circles, and statistics"""
    try:
        # Get parameters - baseValue can be multiple values
        base_value = request.args.getlist('baseValue')  # Use getlist for multiple values
        if not base_value:
            base_value = ['BANGOR', 'PORTLAND']  # Default
        
        radius = request.args.get('radius', 50.0, type=float)
        expected_time = request.args.get('expectedTime', 20.0, type=float)  # 注意前端传的是 expectedTime
        
        from utils.scenario.get_range_map import (
            generate_range_map, 
            calculate_range_statistics
        )
        
        # Generate map HTML
        html_map = generate_range_map(base_value, radius, expected_time)
        
        # Calculate statistics
        stats = calculate_range_statistics(base_value, radius, expected_time)
        
        # Return both map HTML and statistics
        # Since we need to return HTML for iframe, we'll return HTML with embedded data
        # Or we can return JSON with map HTML as a field
        return jsonify({
            'status': 'success',
            'map_html': html_map,
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
        base_cities_input = request.args.get('baseCities', None)  # Optional, comma-separated cities
        
        # Parse and validate cities on backend
        valid_cities = []
        if base_cities_input:
            from utils.heatmap import get_city_coordinates
            city_coords = get_city_coordinates(isOnlyMaine=True)
            city_coords_set = set(city.upper().strip() for city in city_coords.keys())
            
            # Parse comma-separated cities
            cities = base_cities_input.split(',')
            for city in cities:
                normalized = city.strip().upper()
                if normalized and normalized in city_coords_set:
                    valid_cities.append(normalized)
            # 新的城市，是列表里所有的城市（去重）
            valid_cities = list(set(valid_cities))
        
        if not center_type:
            return jsonify({
                'status': 'error',
                'message': 'centerType parameter is required'
            }), 400
        
        from utils.scenario.get_special_base_stats import (
            calculate_special_base_statistics,
            get_special_base_data
        )
        from utils.scenario.get_range_map import generate_range_map
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
        
        # Generate map with all base cities
        if base_cities_list:
            html_map = generate_range_map(base_cities_list, radius, expected_time,center_type)
        else:
            html_map = None
        
        return jsonify({
            'status': 'success',
            'map_html': html_map,
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
    

@app.route('/api/base_siting', methods=['POST'])
def get_base_siting_api():
    try:
        data = request.get_json() or {}
        
        existing_bases = data.get('existing_bases', ['BANGOR'])
        candidate_base = data.get('candidate_base')
        service_radius_miles = float(data.get('service_radius_miles', 50.0))
        sla_target_minutes = int(data.get('sla_target_minutes', 20))
        fleet_size = int(data.get('fleet_size', 3))
        crews_per_vehicle = int(data.get('crews_per_vehicle', 2))
        missions_per_vehicle_per_day = int(data.get('missions_per_vehicle_per_day', 3))
        coverage_threshold_minutes = int(data.get('coverage_threshold_minutes', 20))
        
        result = get_base_siting_analysis(
            existing_bases=existing_bases,
            candidate_base=candidate_base,
            service_radius_miles=service_radius_miles,
            sla_target_minutes=sla_target_minutes,
            fleet_size=fleet_size,
            crews_per_vehicle=crews_per_vehicle,
            missions_per_vehicle_per_day=missions_per_vehicle_per_day,
            coverage_threshold_minutes=coverage_threshold_minutes
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get base siting analysis: {str(e)}'
        }), 500

@app.route('/api/weather_risk', methods=['GET'])
def get_weather_risk_api():
    try:
        method = request.args.get('method', 'precipitation')
        aggregation_level = request.args.get('aggregation_level', 'day')
        
        if method not in ['precipitation', 'temperature', 'combined']:
            return jsonify({
                'status': 'error',
                'message': 'method must be precipitation, temperature, or combined'
            }), 400
        
        if aggregation_level not in ['day', 'month', 'week']:
            return jsonify({
                'status': 'error',
                'message': 'aggregation_level must be day, month, or week'
            }), 400
        
        result = get_weather_risk_analysis(
            method=method,
            aggregation_level=aggregation_level
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get weather risk data: {str(e)}'
        }), 500

@app.route('/api/kpi_bullets', methods=['GET'])
def get_kpi_bullets_api():
    try:
        year = int(request.args.get('year', 2023))
        sla_target_minutes = int(request.args.get('sla_target_minutes', 20))
        include_historical = request.args.get('include_historical', 'true').lower() == 'true'
        
        result = get_kpi_bullets(
            year=year,
            sla_target_minutes=sla_target_minutes,
            include_historical=include_historical
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get KPI bullets: {str(e)}'
        }), 500

@app.route('/api/trend_wall', methods=['GET'])
def get_trend_wall_api():
    try:
        current_year = int(request.args.get('current_year', 2023))
        current_month = request.args.get('current_month')
        current_month = int(current_month) if current_month else None
        forecast_months = int(request.args.get('forecast_months', 6))
        
        result = get_trend_wall_data(
            current_year=current_year,
            current_month=current_month,
            forecast_months=forecast_months
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get trend wall data: {str(e)}'
        }), 500

@app.route('/api/cost_benefit_throughput', methods=['GET'])
def get_cost_benefit_throughput_api():
    try:
        start_year = int(request.args.get('start_year', 2020))
        end_year = int(request.args.get('end_year', 2023))
        aggregation = request.args.get('aggregation', 'month')
        
        result = get_cost_benefit_throughput_data(
            start_year=start_year,
            end_year=end_year,
            aggregation=aggregation
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get cost-benefit-throughput data: {str(e)}'
        }), 500

@app.route('/api/safety_spc', methods=['GET'])
def get_safety_spc_api():
    try:
        start_year = int(request.args.get('start_year', 2020))
        end_year = int(request.args.get('end_year', 2023))
        aggregation = request.args.get('aggregation', 'month')
        method = request.args.get('method', '3sigma')
        
        result = get_safety_spc_data(
            start_year=start_year,
            end_year=end_year,
            aggregation=aggregation,
            method=method
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get safety SPC data: {str(e)}'
        }), 500
    

@app.route('/api/test', methods=['GET'])
def get_test_api():
    try:
        df = read_data('Oasis.csv')
        print(df['Add Date'].head())
        df['Add Date'] = pd.to_datetime(df['Add Date'])
        df['Year'] = df['Add Date'].dt.year
        df['Month'] = df['Add Date'].dt.month
        df.rename(columns={'responseDelay (Subjective and with no objective time for them to decide, none or select reason, just gustalt)':'responseDelay'},inplace=True)
        df.rename(columns={'transportByPrimaryQ (Did the appropriate asset transport the patient without delay)':'transportByPrimaryQ'},inplace=True)
        df = df[df['Year'] == 2024]
        df['responseDelay'] = df['responseDelay'].fillna('')
        df['delay_list'] = df['responseDelay'].str.split('|')
        
        df = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})
        df = df[df['respondingAssets'].isin(['l1','l2','l3','l4'])]
        df_exp = df.explode('delay_list')
        df_exp = df_exp[(df_exp['delay_list'] != '')&(df_exp['delay_list']!='noDelays')]
        reason_counts = (
            df_exp['delay_list']
            .value_counts()
            .reset_index()
        )
        reason_counts.columns = ['reason', 'count']
        print(reason_counts.head())
        df_delay_reason = df_exp.groupby(['delay_list','respondingAssets']).size().reset_index(name='count')
        delayData = df_exp.groupby(['respondingAssets','transportByPrimaryQ']).size().reset_index(name='count')
        print(delayData['count'].describe())
        return jsonify({
            'status': 'success',
            'data': df.to_dict(orient='records'),
            'delayData':delayData.to_dict(orient='records'),
            'delayReasonData':reason_counts.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get test data: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

