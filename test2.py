import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Suppress HTTPS warnings
urllib3.disable_warnings(InsecureRequestWarning)

# OpenSearch URL for listing all indexes
url = "https://140.160.1.66:9200/_cat/indices?format=json"

# Send request
response = requests.get(
    url,
    auth=HTTPBasicAuth("", ""),
    verify=False  # ignore SSL certificate
)

# Print the response
print(response.text)
