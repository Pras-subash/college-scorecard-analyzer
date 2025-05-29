"""
A script to query and display college program information from the College Scorecard API.
This script retrieves information about colleges and their programs using the Department of
Education's College Scorecard API. It allows users to search by state, school name, and
program title, displaying admission statistics (SAT/ACT scores) and program details including
earnings data for various timeframes.
User Inputs:
    - state_code (str): Two-letter state code (defaults to WA)
    - school_name (str): Name of the institution (optional)
    - program_title (str): Specific program to search for (optional)
API Requirements:
    - Requires a valid api.data.gov API key
    - Uses the College Scorecard v1 API endpoint
Output Information:
    - School admission statistics (SAT and ACT scores)
    - Program details:
        - Program code
        - Title name
        - Credential type
        - Earnings data (1-year, 4-year, 5-year, and highest median earnings)
Dependencies:
    - json: For JSON data handling
    - requests: For making HTTP requests
    - sys: For terminal detection
    - os: For terminal clearing
    - urllib.parse: For URL encoding
Note:
    If no state code and school name are provided, defaults to University of Washington-Seattle
    in WA state to avoid a global search.

API Key Setup Instructions:
1. Visit https://api.data.gov/signup/
2. Fill out the registration form
3. You will receive your API key via email
4. Create a file named 'apikey.txt' in the same directory as this script
5. Paste your API key into apikey.txt (single line, no quotes)
6. Save the file

Note: Keep your API key private and never commit it to version control.
Rate Limits: The API has a limit of 1000 requests per hour per API key.
Documentation: https://collegescorecard.ed.gov/data/documentation/
"""

import json
import requests
import sys
import os
import urllib.parse
import requests.exceptions
import socket

# Clear the console if running in a terminal 
if sys.stdout.isatty():
    os.system('clear')

# Prompt for state code input
state_code = input("Enter 2-letter state code (default WA): ").strip().upper()
    
# Prompt for school name input
school_name = input('Enter school name (leave blank for all schools in state): ').strip()

# Prompt for program title input
program_title = input('Enter program title to search (leave blank for all programs): ').strip().lower()

#default to UW rather than doing a global search
if not state_code and not school_name:
    state_code = "WA"
    school_name = "University of Washington-Seattle"

# Build the URL dynamically
base_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json"
# Read API key from file
with open('apikey.txt', 'r') as f:
    api_key = f.read().strip()

params = [
    "per_page=3000000",
    f"api_key={api_key}"
]

if state_code:
    params.insert(0, f"school.state={state_code}")
if school_name:
    school_name_encoded = urllib.parse.quote(school_name)
    params.insert(1, f"school.name={school_name_encoded}")

url = f"{base_url}?" + "&".join(params)

# Add error handling around the request
try:
    # Send a GET request
    response = requests.get(url, timeout=10)  # Add timeout
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse JSON content
    else:
        print(f"Failed to retrieve JSON. Status code: {response.status_code}")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print("Error: Unable to connect to the API. Please check your internet connection.")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("Error: Request timed out. Please try again.")
    sys.exit(1)
except socket.gaierror:
    print("Error: Unable to resolve the API hostname. Please check your internet connection.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

#print(json.dumps(data, indent=4))

for r in data.get("results"):
    print("\n ===== \n")
    l = r["latest"]
    admissions = l["admissions"]
    print(f"{r['school']['name']} Admissions SAT : {json.dumps(admissions['sat_scores'], indent=4)} \n {r['school']['name']} ACT: {json.dumps(admissions['act_scores'], indent=4)}")
    
    # Tuition with error handling
    try:
        in_state = l['cost']['tuition']['in_state']
        out_state = l['cost']['tuition']['out_of_state']
        if in_state is not None and out_state is not None:
            print(f"Tuition and Fees: ${in_state:,} (In-State), ${out_state:,} (Out-of-State)")
        else:
            print("Tuition data not available")
    except (KeyError, TypeError):
        print("Tuition data not available")
    
    # Check if 'programs' and 'cip_4_digit' exist
    
    if "programs" in l and "cip_4_digit" in l["programs"]:
        for p in l["programs"]["cip_4_digit"]:
            # Only print if no title filter or title matches search
            if not program_title or program_title in p['title'].lower():
                print(f"Courses offered by {r['school']['name']}")
                print(f"Code : {p['code']}")
                print(f"Title Name: {p['title']}")
                print(f"Title Type: {p['credential']['title']}")
                if "1_yr" in p["earnings"] and "overall_median_earnings" in p["earnings"]["1_yr"]:
                    earnings = p["earnings"]["1_yr"]["overall_median_earnings"]
                    if earnings is not None:
                        print(f"First year earnings: ${earnings:,.2f}")
                    else:
                        print("First year earnings: Data not available")
                if "4_yr" in p["earnings"] and "overall_median_earnings" in p["earnings"]["4_yr"]:
                    earnings = p["earnings"]["4_yr"]["overall_median_earnings"]
                    if earnings is not None:
                        print(f"Fourth year earnings: ${earnings:,.2f}")
                    else:
                        print("Fourth year earnings: Data not available")
                if "5_yr" in p["earnings"] and "overall_median_earnings" in p["earnings"]["5_yr"]:
                    earnings = p["earnings"]["5_yr"]["overall_median_earnings"]
                    if earnings is not None:
                        print(f"Fifth year earnings: ${earnings:,.2f}")
                    else:
                        print("Fifth year earnings: Data not available")
                if "highest" in p["earnings"] and "overall_median_earnings" in p["earnings"]["highest"]:
                    earnings = p["earnings"]["highest"]["overall_median_earnings"]
                    if earnings is not None:
                        print(f"Fifth year earnings: ${earnings:,.2f}")
                    else:
                        print("Fifth year earnings: Data not available")
                print("\n ----- \n")
    else:
        print("No program data available.\n")