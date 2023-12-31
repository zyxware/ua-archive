"""
Data Fetcher

Author: Vimal Joseph
More Information: https://www.zyxware.com/article/6662/backup-universal-analytics-data-python

This script fetch the required data using Google Analytics API.
"""
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError

def get_data(api_key, view_id, dimensions, metrics, start_date, end_date, date_formatter, page_size=1000, next_page_token=None, sample_size='DEFAULT'):
    # Initialize service
    credentials = ServiceAccountCredentials.from_json_keyfile_name(api_key)
    service = build('analyticsreporting', 'v4', credentials=credentials)

    try:
        # Build and execute request
        request = service.reports().batchGet(
            body={
                'reportRequests': [
                    {
                        'viewId': view_id,
                        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                        'dimensions': [{'name': d} for d in dimensions],
                        'metrics': [{'expression': m} for m in metrics],
                        'pageSize': page_size,
                        'pageToken': next_page_token,
                        'samplingLevel': sample_size
                    }
                ]
            }
        )
        response = request.execute()
        report = response.get('reports', [])[0]  # Assuming one report request

        # Process report data
        formatted_data = []
        column_header_entries = report['columnHeader']['dimensions'] + \
                                [entry['name'] for entry in report['columnHeader']['metricHeader']['metricHeaderEntries']]
        rows = report.get('data', {}).get('rows', [])

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

        return formatted_data, new_next_page_token

    except HttpError as error:
        print(f"Error fetching data: {error}")
        return [], None

