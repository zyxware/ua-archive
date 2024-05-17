# Google Universal Analytics Data Archiving

This Python script fetches data using the Google Analytics Reporting API v4 and writes it to a CSV file. It is designed to retrieve specific metrics and dimensions within a certain date range for a particular view (profile). This script can be used to automate your UA backup process. It has the capability to resume the download if you hit the API limit or any other errors.

# Universal Analytics End Of Life

Universal Analytics (UA) stopped processing data on July 1st, 2023. Google has announced a complete shutdown of the UA interface and APIs on July 1st, 2024. If you have already transitioned to Google Analytics 4 for your website data collection, this script can assist you in downloading data from your Universal Analytics properties. Downloading data from UA is not as straightforward as you might think. Google imposes a limit of 50,000 API calls per day, and if you have years of data to download with numerous dimensions and metrics, and this script make it easier for you to download your reports from UA before it is gone.

Also see [3 Free Tools to Backup Google Universal Analytics Reports](https://www.zyxware.com/article/6707/3-free-tools-to-backup-google-universal-analytics-reports)

Also check:
- [Universal Analytics Data: Should You Backup or Let Go?](https://www.zyxware.com/article/6613/universal-analytics-historical-data-backup) - This article talks about the key considerations and options available for backup.

This is a Free Software licenced under GNU GPL v2.0 or above. Please see [What is Free Software?](https://www.zyxware.com/article/6488/what-free-software)

## Requirements

- Python 3
- `googleapiclient`
- `oauth2client`
- `pyyaml`
- `argparse`

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
    pip install google-api-python-client oauth2client pyyaml argparse
    ```

3. **Service Account and API Key:**
   - Set up a service account in Google Cloud Console. - [Follow Google Documentation](https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py) for the detailed instructions.
   - Download the JSON key file.
   - Rename the file to `ua-archive.json` and place it in the project directory.

4. **Configure the Script:**
   - Copy `settings.yml.default` to `settings.yml` and update `api_key` with the name of the JSON file generated and `view_id` with your UA property's view ID.
   - Edit the `reports_config.yml` to add the reports you want to generate.
   - Refer to `reports_config.yml.example` for additional parameters like `metrics_filter`, `page_size`, and `sampling_level`.

## Usage

### Run the Script

Run the script with Python:

```sh
python analytics_reporter.py --report_id 1 --start 2023-01-01 --end 2023-01-31
```
`report_id` should be the ID in the `reports_config.yml`.

After successful execution, a CSV file named `<property_name>_<view_id>_<report_id>_<report_name>_report.csv` will be generated in the project directory.

### Custom Settings File

To use a custom settings file, provide the `--settings` argument. This is useful if you want to manage downloading reports from multiple properties by having separate settings files for each property:

```sh
python3 analytics_reporter.py --settings custom_settings.yml --report_id 1 --start 2023-01-01 --end 2023-01-31
```

### Generate All Reports

To generate all reports specified in the `reports_config.yml`, simply omit the `--report_id` argument:

```sh
python3 analytics_reporter.py --start 2023-01-01 --end 2023-01-31
```

The script will generate CSV files for all reports specified in the `reports_config.yml`.

### Progress Tracking and Resuming Downloads

The script tracks progress for each report in a `progress.log` file. If the script is interrupted or encounters an error, it can resume from where it left off:

```sh
python3 analytics_reporter.py --report_id 1 --start 2023-01-01 --end 2023-01-31
```

The script will automatically resume downloading from the last saved progress.

### Debugging

Try removing the <view-id>_progress.log file and the csv files generated to restart the download. Check the settings.yml, reports_config.yml files and make sure that the values are correct. Also refer the settings.yml.default and reports_config.yml.example.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to add issues and merge requests.

## Contact Us

If you are looking for professional support on archiving your UA data, please [contact us](https://www.zyxware.com/contact-us).
