import argparse
import subprocess
import datetime
import signal
import os
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

interrupted = False
log_file = "ua-backup-execution.log"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Wrapper script for analytics-reporter.py')
    parser.add_argument('--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--settings', type=str, help='Path to settings YAML file')
    parser.add_argument('--report_id', type=int, help='ID of the report to generate')
    parser.add_argument('--report_level', type=str, choices=['day', 'week', 'month', 'year'], required=True, help='Report level to split date range')
    args = parser.parse_args()
    return args

def date_range(start_date, end_date, delta):
    """Generate a range of dates."""
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += delta

def split_date_range(start, end, report_level):
    """Split the date range based on the report level."""
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d")

    periods = []
    if report_level == 'day':
        delta = datetime.timedelta(days=1)
        for current_start in date_range(start_date, end_date, delta):
            current_end = current_start + delta - datetime.timedelta(days=1)
            periods.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
    elif report_level == 'week':
        delta = datetime.timedelta(weeks=1)
        for current_start in date_range(start_date, end_date, delta):
            current_end = current_start + delta - datetime.timedelta(days=1)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
    elif report_level == 'month':
        def add_months(dt, months):
            month = dt.month - 1 + months
            year = dt.year + month // 12
            month = month % 12 + 1
            day = min(dt.day, [31, 29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            return dt.replace(year=year, month=month, day=day)
        current_start = start_date
        while current_start <= end_date:
            current_end = add_months(current_start, 1) - datetime.timedelta(days=1)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
            current_start = current_end + datetime.timedelta(days=1)
    elif report_level == 'year':
        delta = datetime.timedelta(days=365)  # Approximation
        for current_start in date_range(start_date, end_date, delta):
            current_end = current_start + delta - datetime.timedelta(days=1)
            if current_end > end_date:
                current_end = end_date
            periods.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))

    return periods

def log_execution(start_date, end_date, sequence):
    """Log the execution details to the log file."""
    with open(log_file, 'a') as f:
        f.write(f"{start_date},{end_date},{sequence}\n")

def check_quota_exceeded():
    """Check if quota exceeded file exists and is less than 24 hours old."""
    quota_log_file = f"quota_exceeded.log"
    if os.path.exists(quota_log_file):
        with open(quota_log_file, 'r') as log_file:
            lines = log_file.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_exceed_time = datetime.strptime(last_line, '%Y-%m-%d %H:%M:%S')
                if datetime.now() - last_exceed_time < timedelta(hours=24):
                    logging.info("Quota was exceeded less than 24 hours ago. Exiting.")
                    return True
    return False

def read_last_execution():
    """Read the last execution details from the log file."""
    if not os.path.exists(log_file):
        return None, None, None
    with open(log_file, 'r') as f:
        lines = f.readlines()
        if not lines:
            return None, None, None
        last_line = lines[-1]
        last_start, last_end, last_sequence = last_line.strip().split(',')
        return last_start, last_end, int(last_sequence)

def run_analytics_reporter(start_date, end_date, settings, report_id, sequence):
    """Run the analytics_reporter.py script with the provided arguments."""
    global interrupted
    logger.info(f"Running analytics_reporter.py for period: {start_date} to {end_date}")
    cmd = [
        'python', 'analytics_reporter.py',
        '--start', start_date,
        '--end', end_date,
        '--sequence', str(sequence)
    ]
    if settings is not None:
        cmd.extend(['--settings', settings])
    if report_id is not None:
        cmd.extend(['--report_id', str(report_id)])

    logger.info(f"Command: {cmd}")  # Debugging statement
    process = subprocess.Popen(cmd)
    try:
        process.wait()
        log_execution(start_date, end_date, sequence)  # Log the execution after successful run
    except KeyboardInterrupt:
        interrupted = True
        logger.info("Interrupt received. Waiting for the current report to complete...")

def signal_handler(sig, frame):
    """Signal handler for SIGINT."""
    global interrupted
    interrupted = True
    logger.info("Interrupt received. Current execution will finish before exiting.")

def main():
    """Main function to parse arguments, split date range, and call analytics-reporter.py for each period."""
    global interrupted
    args = parse_arguments()

    signal.signal(signal.SIGINT, signal_handler)

    last_start, last_end, last_sequence = read_last_execution()

    if last_start and last_end and last_sequence:
        # Resume from the last logged entry
        periods = split_date_range(last_start, args.end, args.report_level)
        start_sequence = last_sequence
    else:
        # Start from the beginning
        periods = split_date_range(args.start, args.end, args.report_level)
        start_sequence = 1

    for sequence, (start_date, end_date) in enumerate(periods, start=start_sequence):
        if interrupted:
            break
        if check_quota_exceeded():
            logging.info("Quota was exceeded recently. Exiting.")
            break
        run_analytics_reporter(start_date, end_date, args.settings, args.report_id, sequence)

    if interrupted:
        logger.info("Execution was interrupted. Exiting after completing the current report.")

if __name__ == "__main__":
    main()
