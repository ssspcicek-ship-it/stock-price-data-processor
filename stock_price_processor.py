"""Second development stage of the Stock Price Data Processor."""

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


def calculate_price_change(record):
    """Return the difference between closing and opening prices."""
    return record["close"] - record["open"]


def calculate_percentage_change(record):
    """Return the daily price change as a percentage."""
    return calculate_price_change(record) / record["open"] * 100


def display_records(records):
    """Show stock records in a readable table."""
    if not records:
        print("\nThere are no records to display.")
        return

    line = "-" * 93
    print()
    print(line)
    print(
        f"{'Symbol':<8} {'Date':<12} {'Open':>9} {'Close':>9} "
        f"{'Change':>10} {'Change %':>10} {'Volume':>11}"
    )
    print(line)

    for record in records:
        price_change = calculate_price_change(record)
        percentage_change = calculate_percentage_change(record)
        print(
            f"{record['symbol']:<8} {record['date'].isoformat():<12} "
            f"{record['open']:>9.2f} {record['close']:>9.2f} "
            f"{price_change:>+10.2f} {percentage_change:>+9.2f}% "
            f"{record['volume']:>11,d}"
        )

    print(line)
    print(f"Records shown: {len(records)}")


def company_symbol_exists(records, symbol):
    """Use linear search to check whether a company symbol exists."""
    for record in records:
        if record["symbol"] == symbol:
            return True
    return False


def filter_stock_records(
    records,
    symbol="",
    start_date=None,
    end_date=None,
    minimum_price=None,
    maximum_price=None,
):
    """Use linear search to return records that match all filters."""
    matching_records = []

    for record in records:
        if symbol and record["symbol"] != symbol:
            continue
        if start_date and record["date"] < start_date:
            continue
        if end_date and record["date"] > end_date:
            continue
        if minimum_price is not None and record["close"] < minimum_price:
            continue
        if maximum_price is not None and record["close"] > maximum_price:
            continue

        matching_records.append(record)

    return matching_records


def display_company_list(records):
    """Show each available company once."""
    companies = {}
    for record in records:
        companies[record["symbol"]] = record["company"]

    print("\nAvailable companies:")
    for symbol in companies:
        print(f"  {symbol} - {companies[symbol]}")


def get_optional_date(prompt):
    """Ask for an optional date and repeat after invalid input."""
    while True:
        date_text = input(prompt).strip()
        if date_text == "":
            return None

        try:
            return parse_date(date_text)
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, for example 2026-06-01.")


def get_optional_price(prompt):
    """Ask for an optional positive price."""
    while True:
        price_text = input(prompt).strip()
        if price_text == "":
            return None

        try:
            price = float(price_text)
            if price < 0:
                print("The price cannot be negative.")
            else:
                return price
        except ValueError:
            print("Invalid price. Enter a number or press Enter to skip it.")


def get_company_symbol(records):
    """Ask for an optional valid company symbol."""
    while True:
        symbol = input("Company symbol: ").strip().upper()

        if symbol == "":
            return ""

        if company_symbol_exists(records, symbol):
            return symbol

        print("Unknown symbol. Enter a listed symbol or press Enter for all.")


def ask_for_filters(records):
    """Collect filter values from the user."""
    display_company_list(records)
    print("Press Enter to skip any filter.")

    symbol = get_company_symbol(records)
    start_date = get_optional_date("Start date (YYYY-MM-DD): ")

    while True:
        end_date = get_optional_date("End date (YYYY-MM-DD): ")
        if start_date and end_date and end_date < start_date:
            print("The end date cannot be before the start date.")
        else:
            break

    minimum_price = get_optional_price("Minimum closing price: ")

    while True:
        maximum_price = get_optional_price("Maximum closing price: ")
        if (
            minimum_price is not None
            and maximum_price is not None
            and maximum_price < minimum_price
        ):
            print("The maximum price cannot be lower than the minimum price.")
        else:
            break

    return filter_stock_records(
        records,
        symbol,
        start_date,
        end_date,
        minimum_price,
        maximum_price,
    )


def get_menu_choice():
    """Ask for one valid main-menu choice."""
    while True:
        choice = input("Choose an option (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            return choice
        print("Invalid choice. Please enter a number from 1 to 4.")


def display_main_menu(current_count, total_count):
    """Show the available actions in this development stage."""
    print("\n" + "=" * 50)
    print("STOCK PRICE DATA PROCESSOR")
    print(f"Current records: {current_count} of {total_count}")
    print("=" * 50)
    print("1. View current records")
    print("2. Filter records")
    print("3. Reset filters")
    print("4. Exit")


def main():
    """Load the data and run the first command-line menu."""
    all_records = load_stock_data(DATA_FILE)

    if not all_records:
        print("The program cannot start because no valid records were loaded.")
        return

    current_records = all_records.copy()
    print(f"Loaded {len(all_records)} valid stock records.")

    while True:
        display_main_menu(len(current_records), len(all_records))
        choice = get_menu_choice()

        if choice == "1":
            display_records(current_records)
        elif choice == "2":
            current_records = ask_for_filters(all_records)
            print(f"Matching records: {len(current_records)}")
        elif choice == "3":
            current_records = all_records.copy()
            print("All filters have been reset.")
        else:
            print("Program closed. Goodbye.")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed safely.")
