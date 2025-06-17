"""
College Scorecard Web Application

A Flask-based web application that provides a user interface for querying the Department of 
Education's College Scorecard API. This application allows users to search for college programs
and view detailed information about admissions, tuition, and program earnings.

Technical Details:
    - Framework: Flask
    - Port: 8001
    - Host: 0.0.0.0 (accessible from other devices on network)
    - CORS: Enabled for all routes

Setup:
    1. Install dependencies:
       pip install -r requirements.txt
    
    2. Ensure apikey.txt exists with your api.data.gov API key
    
    3. Run the application:
       python app.py

Usage:
    1. Access the web interface at:
       http://localhost:8001
    
    2. Use the search form to query:
       - State code (2 letters, e.g., WA)
       - School name (optional)
       - Program title (optional)

API Endpoints:
    - GET /: Main search interface
    - POST /search: Search endpoint for college data

Dependencies:
    - Flask
    - Flask-CORS
    - requests
    - pathlib

Author: Prasanna Subash
Date: 6/16/2025
Version: 1.0
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Add this import
import json
import requests
import urllib.parse
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_college_data(state_code, school_name, program_title):
    """Get college data from the API"""
    base_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json"
    
    # Read API key
    api_key = Path('apikey.txt').read_text().strip()
    
    # Build parameters
    params = ["per_page=3000000", f"api_key={api_key}"]
    if state_code:
        params.insert(0, f"school.state={state_code}")
    if school_name:
        params.insert(1, f"school.name={urllib.parse.quote(school_name)}")
    
    url = f"{base_url}?" + "&".join(params)
    
    try:
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    state_code = request.form.get('state_code', 'WA').upper()
    school_name = request.form.get('school_name', '')
    program_title = request.form.get('program_title', '').lower()
    
    data = get_college_data(state_code, school_name, program_title)
    if not data:
        return jsonify({'error': 'Failed to fetch data'})
    
    results = []
    for r in data.get("results", []):
        school = {
            'name': r['school']['name'],
            'admissions': {
                'sat': r['latest']['admissions']['sat_scores'],
                'act': r['latest']['admissions']['act_scores']
            },
            'programs': []
        }
        
        # Add tuition data
        try:
            school['tuition'] = {
                'in_state': r['latest']['cost']['tuition']['in_state'],
                'out_of_state': r['latest']['cost']['tuition']['out_of_state']
            }
        except (KeyError, TypeError):
            school['tuition'] = None
        
        # Add matching programs
        if "programs" in r['latest'] and "cip_4_digit" in r['latest']["programs"]:
            for p in r['latest']["programs"]["cip_4_digit"]:
                if not program_title or program_title in p['title'].lower():
                    program = {
                        'code': p['code'],
                        'title': p['title'],
                        'credential': p['credential']['title'],
                        'earnings': {}
                    }
                    
                    # Add earnings data
                    for year in ['1_yr', '4_yr', '5_yr', 'highest']:
                        if year in p["earnings"] and "overall_median_earnings" in p["earnings"][year]:
                            program['earnings'][year] = p["earnings"][year]["overall_median_earnings"]
                    
                    school['programs'].append(program)
        
        results.append(school)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)