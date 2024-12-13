from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None