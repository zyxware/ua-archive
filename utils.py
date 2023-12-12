import csv
def format_date(date_str):
    """Convert date from 'YYYYMMDD' to 'YYYY-MM-DD' format."""
    try:
        from datetime import datetime
        return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
    except ValueError:
        return date_str  # Return the original string if it can't be converted

def write_to_csv(data, output_file):
    if not data:
        print("No data to write to CSV.")
        return

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
