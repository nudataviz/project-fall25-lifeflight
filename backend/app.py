from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd
from config import config
from utils.heatmap import generate_city_demand_heatmap, map_to_html
from utils.getData import read_data
from utils.responseTime import calculate_response_time
from utils.veh_count import calculate_veh_count

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
    return jsonify({
        'status': 'success',
        'message': 'Veh count data fetched successfully',
        'data': veh_count
    })

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
    total_missions = df['Incident Number'].nunique()
    # 2 Total Cities Covered
    total_cities_covered = df['PU City'].nunique()
    # 3 Monthly Average Response Time
    mart = calculate_response_time(df,2023,12)
    # 4 Yearly Average Response Time
    yart = calculate_response_time(df,2023)
    return jsonify({
        'status': 'success',
        'message': 'Indicator data fetched successfully',
        'data': {
            'total_missions': total_missions,
            'total_cities_covered': total_cities_covered,
            'mart': mart,
            'yart': yart
        }
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

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Backend is working correctly',
        'data': {
            'timestamp': '2024-01-01T00:00:00Z',
            'test': True
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

