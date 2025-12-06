import requests
import logging
import http.client as http_client
import os
import sys

from requests.auth import HTTPBasicAuth
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

from query_tooling import generate_suricata_query, process_flow_data 

# Suppress warning see below for why
urllib3.disable_warnings(InsecureRequestWarning)

# Debug Logging, uncomment to have verbose logs
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propigate = True

# Hardcoded url for PISCES opensearch server
url = "https://140.160.1.66:9200/_search"

def get_env_dict(env_file):
    d = dict()
    with open(env_file, 'r') as envs:
        for line in envs:
            line = line.strip()
            if line and not line.startswith("#"):
                line = line.split("=", 1)
                d[line[0]] = line[1]
    return d

# Load our environment variables
# OS_USER -- The username used for open search
# OS_PASS -- The password used for open search
assert os.path.exists('.env'), "Missing .env file to hold PISCES credentials"
env_dict = get_env_dict('.env')

username = env_dict['OS_USER']
password = env_dict['OS_PASS']
print(username, password)
assert username != None, "Username is not defined in .env"
assert password != None, "Username is not defined in .env"

assert len(sys.argv) == 3, "Wrong number of cmd line arguments: e.x: python3 run_query.py <query_ip> <output_location>"
query_url = sys.argv[1]
save_file = sys.argv[2]

query = generate_suricata_query(query_url)

try:
    response = requests.get(
        url,
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(username, password),
        data=json.dumps(query),
        #Ignore the SSL Cert (This is why we turned off the requests warning
        verify=False, 
    )
except Exception as e:
    print(f'An error occured with the request: {e}')


print(response)
time_series = process_flow_data(response)
with open(save_file, 'w') as sf:
    sf.write(time_series)
