# Google Universal Analytics Data Archiving

This Python script fetches data using the Google Analytics Reporting API v4 and writes it to a CSV file. It is designed to retrieve specific metrics and dimensions within a certain date range for a particular view (profile). This script is suitable for simple use cases, such as when you only need data over a short timeline or with a small number of dimensions or metrics.

# Universal Analytics End Of Life

Universal Analytics (UA) stopped processing data on July 1st, 2023. Google has announced a complete shutdown of the UA interface and APIs on July 1st, 2024. If you have already transitioned to Google Analytics 4 for your website data collection, this script can assist you in downloading data from your Universal Analytics properties. Downloading data from UA is not as straightforward as you might think. Google imposes a limit of 50,000 API calls per day, and if you have years of data to download with numerous dimensions and metrics, the script can quickly become complex.

## Matomo

For a more streamlined approach and a UA-like interface to navigate data downloads, consider using Matomo. Matomo is a web analytics solution equipped with a plugin for exporting UA data. Once set up, Matomo handles the backup, allowing you to generate reports as needed through its user-friendly interface.

While there might be some limitations due to the aggregated nature of data downloaded from the Google Analytics API, Matomo captures approximately 90% of the essential data you may want to retain. This includes preserving custom dimensions, eCommerce data, goal data, and more for future reference.

We have successfully assisted many of our customers with downloading UA data to Matomo. If you are considering keeping your Universal Analytics Data, Matomo is an excellent option. We offer UA historical data migration using Matomo as a service. If you are interested, you can checkout a demo here: [Matomo Dashboard](https://engage.zyxware.com/matomo-dashboard)

Also check
- [Universal Analytics Data: Should You Backup or Let Go?](https://www.zyxware.com/article/6613/universal-analytics-historical-data-backup) - This article talks about the key considerations and options available for backup.

## Requirements

- Python 3
- `googleapiclient`
- `oauth2client`

## Setup and Installation

1. **Clone the Repository:**

```sh
git clone https://github.com/zyxware/ua-archive.git
cd ua-archive
```


2. **Install Dependencies:**
It's recommended to use a virtual environment:


```sh
python -m venv venv
source venv/bin/activate
pip install google-api-python-client oauth2client
```

3. **Service Account and API Key:**
- Set up a service account in Google Cloud Console. - [Follow Google Documentation](https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py) for the detailed instructions.
- Download the JSON key file.
- Rename the file to `ua-archive.json` and place it in the project directory.

4. **Configure the Script:**
- Open the script in a text editor.
- Modify the parameters at the bottom of the script (`api_key`, `view_id`, `dimensions`, `metrics`, `start_date`, `end_date`, `output_file`) as needed.

## Usage

Run the script with Python:

```sh
python ua_archive.py
```
After successful execution, a CSV file named `UA_report.csv` will be generated in the project directory.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issue page if you want to contribute.

## Contact Us

If you are looking for profressional support on archiving your UA data, please [contact us](https://www.zyxware.com/contact-us)
