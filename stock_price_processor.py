"""First development stage of the Stock Price Data Processor."""

import csv
from datetime import datetime
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_FILE = PROJECT_FOLDER / "data" / "stock_prices.csv"

REQUIRED_COLUMNS = [
    "symbol",
    "company",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def parse_date(date_text):
    """Convert a YYYY-MM-DD string into a date value."""
    return datetime.strptime(date_text, "%Y-%m-%d").date()


def load_stock_data(file_path):
    """Read stock records from a CSV file and skip invalid rows."""
    records = []

    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as input_file:
            reader = csv.DictReader(input_file)

            if reader.fieldnames is None:
                print("Error: The data file has no column headings.")
                return []

            missing_columns = []
            for column in REQUIRED_COLUMNS:
                if column not in reader.fieldnames:
                    missing_columns.append(column)

            if missing_columns:
                print("Error: Missing columns: " + ", ".join(missing_columns))
                return []

            for line_number, row in enumerate(reader, start=2):
                try:
                    record = {
                        "symbol": row["symbol"].strip().upper(),
                        "company": row["company"].strip(),
                        "date": parse_date(row["date"].strip()),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]),
                    }

                    if not record["symbol"] or not record["company"]:
                        raise ValueError("symbol and company cannot be empty")

                    records.append(record)

                except (AttributeError, KeyError, TypeError, ValueError) as error:
                    print(f"Warning: Line {line_number} was skipped ({error}).")

    except FileNotFoundError:
        print(f"Error: The data file was not found: {file_path}")
    except PermissionError:
        print(f"Error: Permission was denied when reading: {file_path}")
    except (OSError, csv.Error) as error:
        print(f"Error: The data file could not be read ({error}).")

    return records


def main():
    """Load the CSV data and report the result."""
    records = load_stock_data(DATA_FILE)

    if records:
        print(f"Loaded {len(records)} valid stock records.")
    else:
        print("No valid stock records were loaded.")


if __name__ == "__main__":
    main()
