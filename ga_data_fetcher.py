"""
Data Fetcher

Author: Vimal Joseph
More Information: https://www.zyxware.com/article/6662/backup-universal-analytics-data-python

This script fetch the required data using Google Analytics API.
"""
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
import logging

def get_data(api_key, view_id, dimensions, metrics, start_date, end_date, date_formatter, page_size=5000, next_page_token=None, sample_size='DEFAULT', metric_filter=False):
    # Initialize service
    credentials = ServiceAccountCredentials.from_json_keyfile_name(api_key)
    service = build('analyticsreporting', 'v4', credentials=credentials)

    # Prepare the report request body
    report_request = {
        'viewId': view_id,
        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
        'dimensions': [{'name': d} for d in dimensions],
        'metrics': [{'expression': m} for m in metrics],
        'pageSize': page_size,
        'pageToken': next_page_token,
        'samplingLevel': sample_size,
    }

    # Add metric filters if provided and not False
    if metric_filter:
        report_request['metricFilterClauses'] = [{
            'filters': metric_filter
        }]

    # Build and execute the full request
    try:
        response = service.reports().batchGet(
            body={'reportRequests': [report_request]}
        ).execute()

        report = response.get('reports', [])[0]  # Assuming one report request

        # Process report data
        formatted_data = []
        column_header_entries = report['columnHeader']['dimensions'] + \
                                [entry['name'] for entry in report['columnHeader']['metricHeader']['metricHeaderEntries']]
        rows = report.get('data', {}).get('rows', [])
        samples_read_counts = report.get('data', {}).get('samplesReadCounts', [])
        sampling_space_sizes = report.get('data', {}).get('samplingSpaceSizes', [])
        is_sampled = bool(samples_read_counts and sampling_space_sizes)
        sampling_info = {
            'is_sampled': is_sampled,
            'samples_read_counts': samples_read_counts,
            'sampling_space_sizes': sampling_space_sizes
        }

        for row in rows:
            formatted_row = {}
            dimensions_data = row['dimensions']
            metrics_data = row['metrics'][0]['values']
            all_data = dimensions_data + metrics_data
            for i, header in enumerate(column_header_entries):
                if header == 'ga:date':
                    formatted_row[header] = date_formatter(all_data[i])
                else:
                    formatted_row[header] = all_data[i]
            formatted_data.append(formatted_row)

        # Get the next page token, if any
        new_next_page_token = report.get('nextPageToken', None)

        return formatted_data, new_next_page_token, sampling_info, False

    except HttpError as error:
        if error.resp.status == 429:
            logging.error("Quota Error: Quota exceeded. Please try again later.")
            return [], None, {'is_sampled': False, 'samples_read_counts': [], 'sampling_space_sizes': []}, True
        else:
            logging.error(f"Error fetching data: {error}")
            return [], None, {'is_sampled': False, 'samples_read_counts': [], 'sampling_space_sizes': []}, False
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return [], None, {'is_sampled': False, 'samples_read_counts': [], 'sampling_space_sizes': []}, False

