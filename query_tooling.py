import json
from datetime import datetime

def generate_suricata_query(ip_address):
    """
    Generates an OpenSearch/Elasticsearch query body to find Suricata events
    related to a specific IP address and retrieve byte flow data.
    Args:
        ip_address: The IP address to search for (source or destination).
    Returns:
        A dictionary representing the JSON query body.
    Example useage:
        target_ip = "192.168.1.100"
        opensearch_query = generate_suricata_query(target_ip)
        print(f"OpenSearch Query for IP: {target_ip}")
        print(json.dumps(opensearch_query, indent=2))
    """
    query_body = {
        # Adjust as needed
        "size": 10000,
        "_source": [
            "timestamp",  
            "event_type",
            "dest_ip",
            "src_ip",
            "flow.bytes_toserver",
            "flow.bytes_toclient",
            "flow.pkts_toserver",
            "flow.pkts_toclient"
        ],
        "query": {
            "bool": {
                "must": [
                    {"terms": {"event_type": ["flow", "alert", "stats"]}}
                ],
                "filter": [
                    {
                        "bool": {
                            "should": [
                                # Match the IP as the source
                                {"term": {"src_ip": ip_address}},
                                # Match the IP as the destination
                                {"term": {"dest_ip": ip_address}}
                            ],
                            # Require at least one of the 'should' clauses to be true
                            "minimum_should_match": 1
                        }
                    }
                ]
            }
        },
        # Sort by timestamp for chronological processing
        "sort": [
            {"timestamp": {"order": "asc"}}
        ]
    }
    return query_body

def process_flow_data(opensearch_hits):
    """
    Processes OpenSearch hits from Suricata data into a time series of byte flows.

    Args:
        opensearch_hits: A list of dictionaries, where each dict is a hit
                         from the OpenSearch response (i.e., data from one event).

    Returns:
        A list of tuples (time_ms, total_bytes), where:
        - time_ms (int): Relative time in milliseconds from the first event.
        - total_bytes (int): The sum of bytes_toserver and bytes_toclient for that event.
    """
    if not opensearch_hits:
        return []

    # Get the timestamp of the very first event to use as the baseline (time 0)
    first_timestamp_str = opensearch_hits[0]['_source']['timestamp']
    # ISO 8601 format: 'YYYY-MM-DDTHH:MM:SS.mmmmmm+0000'
    baseline_time = datetime.fromisoformat(first_timestamp_str.replace('+0000', '+00:00'))

    time_series_data = []

    for hit in opensearch_hits:
        source_data = hit.get('_source', {})

        # Calculate Total Bytes
        # Safely get the byte counts, defaulting to 0 if the fields are missing (e.g., non-flow events)
        flow = source_data.get('flow', {})
        bytes_toserver = flow.get('bytes_toserver', 0)
        bytes_toclient = flow.get('bytes_toclient', 0)
        total_bytes = bytes_toserver + bytes_toclient

        # Calculate Relative Time in Milliseconds
        current_timestamp_str = source_data['timestamp'].replace('+0000', '+00:00')
        current_time = datetime.fromisoformat(current_timestamp_str)

        # Calculate the time difference (timedelta object)
        time_difference = current_time - baseline_time

        # Convert timedelta to total milliseconds
        # Total seconds * 1000 + total microseconds / 1000
        time_in_s = int(time_difference.total_seconds())

        # Append to the time series
        time_series_data.append((time_in_s, total_bytes))

    return time_series_data

if __name__ == "__main__":
    # Example Usage (Mock Data)
    # This is a list of events, as they would be returned, in the hits array
    # from an OpenSearch query response.
    mock_opensearch_hits = [
        # First event sets baseline (time 0ms)
        {"_source": {"timestamp": "2025-12-05T20:00:00.123456+0000", "flow": {"bytes_toserver": 1500, "bytes_toclient": 0}}},
        # Second event is 500ms later
        {"_source": {"timestamp": "2025-12-05T20:00:00.623456+0000", "flow": {"bytes_toserver": 0, "bytes_toclient": 8000}}},
        # Third event is 1.5 seconds later (1500ms from the start)
        {"_source": {"timestamp": "2025-12-05T20:00:01.623456+0000", "flow": {"bytes_toserver": 200, "bytes_toclient": 100}}},
        # Event with no flow data (should be ignored)
        {"_source": {"timestamp": "2025-12-05T20:00:02.000000+0000", "event_type": "alert"}},
    ]

    time_series_output = process_flow_data(mock_opensearch_hits)

    print("\n**Time Series Output (time_ms, total_bytes)**")
    for t, b in time_series_output:
        print(f"({t}ms, {b} bytes)")
