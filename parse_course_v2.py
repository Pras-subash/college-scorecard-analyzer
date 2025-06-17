import json
import requests
# Add at the top of your script
import sys
import os

# At the start of your script, after imports
if sys.stdout.isatty():
    os.system('clear')
# URL of the JSON data
#url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.state=WA&per_page=3000&school.name=University%20of%20Washington-Seattle&api_key=913egurbOgZ8aZ1vqln39S3H2ON5etWQQJahRyvN"
url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.state=WA&per_page=3000000&api_key=913egurbOgZ8aZ1vqln39S3H2ON5etWQQJahRyvN"

# Send a GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()  # Parse JSON content
else:
    print("Failed to retrieve JSON:", response.status_code)

for r in data.get("results"):
    print("\n ===== \n")
    l = r["latest"]
    admissions = l["admissions"]
    print(f"Admissions SAT : {json.dumps(admissions['sat_scores'], indent=4)} \n ACT: {json.dumps(admissions['act_scores'], indent=4)}")
    # Check if 'programs' and 'cip_4_digit' exist
    if "programs" in l and "cip_4_digit" in l["programs"]:
        for p in l["programs"]["cip_4_digit"]:
            print(f"Courses offered by {r['school']['name']}")
            print(f"Code : {p['code']}")
            print(f"Title: {p['title']}")
            print(f"Title: {p['credential']['title']}")
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