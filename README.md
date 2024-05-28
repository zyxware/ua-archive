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
- `pandas`

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
    pip install google-api-python-client oauth2client pyyaml argparse pandas
    ```

3. **Service Account and API Key:**
   - Set up a service account in Google Cloud Console. - [Follow Google Documentation](https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py) for the detailed instructions.
   - Download the JSON key file.
   - Rename the file to `ua-archive.json` and place it in the project directory.

### Configure the Script

1. **Copy and Update Settings:**
   - Copy `settings.yml.default` to `settings.yml`:
     ```bash
     cp settings.yml.default settings.yml
     ```
   - Update the following fields in `settings.yml`:
     - `reports_config`: Replace with the name of file where you define the reports. See reports_config.yml.example
     - `api_key`: Replace with the name of the generated JSON file (`ua-archive.json`).
     - `view_id`: Replace with the view ID of your UA property. You can find the view ID in Universal Analytics under settings and view settings.
     - `property_name`: Replace with the UA property name.

     Example `settings.yml`:
     ```yaml
     analytics_settings:
       reports_config: "reports_config.yml"
       api_key: "ua-archive.json"
       view_id: "123456789"
       property_name: "Your UA Property Name"
     ```

2. **Reports Configuration:**
   - Copy `reports_config.yml.example` to `reports_config.yml`:
     ```bash
     cp reports_config.yml.example reports_config.yml
     ```
   - Edit the `reports_config.yml` file to add the reports you want to generate. You can use `ua-reports.yml` or `10-useful-reports.yml` as additional examples.

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

### Avoid Sampling

The Google Analytics Reporting API may return a sample of sessions if the date range is very large or the number of records in a query is very large. To address this, we have included a wrapper script `ua_backup.py`, which can take the same list of arguments as `analytics_reporter.py`. This script will split the date range into smaller chunks based on the value in the `--report_level` argument. The available options are 'day', 'week', 'month', and 'year'.

**Example:**

```sh
python3 ua_backup.py --report_id 1 --start 2020-01-01 --end 2023-01-31 --report_level day
```

This will run the query for each day and store the results as separate CSV files in the output folder. The script `merge_report.py` can be used to merge all the individual CSV files into a single CSV file.

```sh
python3 merge_report.py output/123423_ua-property full_report
```

You will get the merged CSV report in the `full_report` folder.

**Note:** The system uses `ua-backup-execution.log` to keep track of the last script executed to resume execution if any error occurs. It also uses `quota_exceeded.log` to track whether the quota was exceeded. The `<view-id>_progress.log` is used to track individual reports. If you want to execute the script as a fresh one, starting from the beginning, you should remove these log files.

### Debugging

Try removing the <view-id>_progress.log file and the csv files generated to restart the download. Check the settings.yml, reports_config.yml files and make sure that the values are correct. Also refer the settings.yml.default and reports_config.yml.example.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to add issues and merge requests.

## Contact Us

If you are looking for professional support on archiving your UA data, please [contact us](https://www.zyxware.com/contact-us).
