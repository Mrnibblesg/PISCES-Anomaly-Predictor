# PISCES-Anomaly-Predictor
An application that utilizes PISCES data to predict system anomalies, drawing from relevant research and the Orion ML project. (https://github.com/sintel-dev/Orion)


The goal is to Implement an open source framework/project that helps analysts detect and predict network anomalies.
We've implemented TadGAN, which is a time-series anomaly detection using GANs.
We've implemented TadGAN for the examples and on multivariate test data from this project, however, without access to OpenSearch there was a lack of high-quality data to use.
OpenSearch data was restricted for most of the quarter and access was revoked before the deadline and without warning, so we opted to use a secondary dataset.
However, it wasn't quite as usable due to a mismatch in what we were expecting to use as features and the actual features presented, not to mention the timestamps weren't fine-grained enough, so we couldn't clean it up properly.
We ended up using this dataset: (https://www.unb.ca/cic/datasets/ids-2017.html)

Our original approach was as follows:
- The user uses run_query.py with an IP. That IP is then used to query OpenSearch for that host's data over a time frame.
- query_tooling.py fitlers the time data and extracts extra time-series features that aren't present in Suricata.
- The collected data would then be passed to the TadGAN pipeline where it trains on that host's patterns and predicts anomalous patterns that arise freom that host's behavior.
- The TadGAN model would then predict the anomalous time frames.

We expected to predict on two cases. Network-wide and per-host.
The expected features to grab/compute:
- Amount of flows active at the given time
- Byte transfer at the given time
- Number of packets sent
- Alerts generated
- Domains queried

The features we had to compromise for, and focus our efforts on detecting a DDoS:
- Total Fwd packets
- Total Bwd packets
- Fwd packet length mean
- Bwd packet length mean
- Byte transfer

Query_tooling.py contains a test case inside a main guard to simulate actual results from OpenSearch.
tests/multi.py contains code which is supposed to tune a TadGAN pipeline for multivariate data.

# How to use
## Prerequisites
- A python environment <3.12 (Tested on 3.10.19 & 3.11.2)
    - You can't install orion-ml without this requirement.
- The aforementioned dataset (https://www.unb.ca/cic/datasets/ids-2017.html), extracted and with the file selected for loading & use in TadGAN multi.py
- numpy, pandas, csv, requests, json
- (If OpenSearch worked) a .env file with OpenSearch credentials.

## To use
- Run run_query.py with the desired host IP you'd like to investigate as well as a destination file for results.
- Run query_tooling.py to test feature extraction with mock data.
- Run multi.py to test TadGAN anomaly training & scoring. (Non-functional)

