import csv
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from datetime import datetime

def format_date(date_str):
    """Convert date from 'YYYYMMDD' to 'YYYY-MM-DD' format."""
    try:
        return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
    except ValueError:
        return date_str  # Return the original string if it can't be converted

def get_data(api_key, view_id, dimensions, metrics, start_date, end_date):
    # Initialize service
    credentials = ServiceAccountCredentials.from_json_keyfile_name(api_key)
    service = build('analyticsreporting', 'v4', credentials=credentials)

    # Build request
    request = service.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'dimensions': [{'name': d} for d in dimensions],
                    'metrics': [{'expression': m} for m in metrics]
                }
            ]
        }
    )

    try:
        response = request.execute()
        report = response.get('reports', [])[0]  # Assuming one report request

        column_header_entries = report['columnHeader']['dimensions'] + \
                                [entry['name'] for entry in report['columnHeader']['metricHeader']['metricHeaderEntries']]

        rows = report.get('data', {}).get('rows', [])
        
        formatted_data = []
        for row in rows:
            formatted_row = {}
            dimensions_data = row['dimensions']
            metrics_data = row['metrics'][0]['values']
            all_data = dimensions_data + metrics_data
            for i, header in enumerate(column_header_entries):
                if header == 'ga:date':
                    formatted_row[header] = format_date(all_data[i])
                else:
                    formatted_row[header] = all_data[i]
            formatted_data.append(formatted_row)

        return formatted_data
    except HttpError as error:
        print(f"Error fetching data: {error}")
        return []

def write_to_csv(data, output_file):
    
    if not data:
        print("No data to write to CSV.")
        return

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# Configure parameters
api_key = "ua-property.json"
view_id = "YOUR PROPERTY VIEW ID"  # Replace with your view ID
dimensions = ["ga:source", "ga:medium", "ga:date"]
metrics = ["ga:users", "ga:pageviews", "ga:sessions"]
start_date = "2023-01-01"
end_date = "2023-01-31"
output_file = "UA_report.csv"

# Fetch and write data to CSV
data = get_data(api_key, view_id, dimensions, metrics, start_date, end_date)

if data:
    write_to_csv(data, output_file)
    print(f"Successfully saved data to CSV file: {output_file}")
else:
    print("No data received from Google Analytics.")
