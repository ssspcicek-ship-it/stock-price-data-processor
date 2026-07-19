"""Stock Price Data Processor for the IY499 programming assignment."""

import csv
from datetime import datetime
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_FILE = PROJECT_FOLDER / "data" / "stock_prices.csv"
OUTPUT_FOLDER = PROJECT_FOLDER / "output"

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
    """Convert YYYY-MM-DD text into a date value."""
    return datetime.strptime(date_text, "%Y-%m-%d").date()


def load_stock_data(file_path):
    """Read stock records from a CSV file and skip invalid rows safely."""
    records = []
    skipped_rows = 0

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
                print("Error: The data file is missing these columns:")
                print(", ".join(missing_columns))
                return []

            for line_number, row in enumerate(reader, start=2):
                try:
                    symbol = (row.get("symbol") or "").strip().upper()
                    company = (row.get("company") or "").strip()
                    record_date = parse_date((row.get("date") or "").strip())
                    open_price = float(row["open"])
                    high_price = float(row["high"])
                    low_price = float(row["low"])
                    close_price = float(row["close"])
                    volume = int(row["volume"])

                    if not symbol or not company:
                        raise ValueError("symbol and company cannot be empty")

                    if min(open_price, high_price, low_price, close_price) <= 0:
                        raise ValueError("prices must be greater than zero")

                    if high_price < max(open_price, close_price):
                        raise ValueError("high price is too low")

                    if low_price > min(open_price, close_price):
                        raise ValueError("low price is too high")

                    if volume < 0:
                        raise ValueError("volume cannot be negative")

                    record = {
                        "symbol": symbol,
                        "company": company,
                        "date": record_date,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "volume": volume,
                    }
                    records.append(record)

                except (TypeError, ValueError, KeyError) as error:
                    skipped_rows += 1
                    print(f"Warning: Line {line_number} was skipped ({error}).")

    except FileNotFoundError:
        print(f"Error: The data file was not found: {file_path}")
        return []
    except PermissionError:
        print(f"Error: Permission was denied when reading: {file_path}")
        return []
    except (OSError, csv.Error) as error:
        print(f"Error: The data file could not be read ({error}).")
        return []

    if skipped_rows > 0:
        print(f"Skipped invalid rows: {skipped_rows}")

    return records


def calculate_price_change(record):
    """Return the difference between closing and opening prices."""
    return record["close"] - record["open"]


def calculate_percentage_change(record):
    """Return the daily price change as a percentage."""
    return calculate_price_change(record) / record["open"] * 100


def get_company_lookup(records):
    """Create a dictionary that connects each symbol to a company name."""
    companies = {}
    for record in records:
        companies[record["symbol"]] = record["company"]
    return companies


def bubble_sort_text(values):
    """Return text values in alphabetical order using bubble sort."""
    sorted_values = values.copy()
    number_of_values = len(sorted_values)

    for end_position in range(number_of_values - 1, 0, -1):
        swapped = False
        for index in range(end_position):
            if sorted_values[index] > sorted_values[index + 1]:
                sorted_values[index], sorted_values[index + 1] = (
                    sorted_values[index + 1],
                    sorted_values[index],
                )
                swapped = True

        if not swapped:
            break

    return sorted_values


def recursive_binary_search(values, target, low_position, high_position):
    """Find a target in sorted text values by using recursion."""
    if low_position > high_position:
        return -1

    middle_position = (low_position + high_position) // 2

    if values[middle_position] == target:
        return middle_position

    if target < values[middle_position]:
        return recursive_binary_search(
            values, target, low_position, middle_position - 1
        )

    return recursive_binary_search(
        values, target, middle_position + 1, high_position
    )


def company_symbol_exists(records, symbol):
    """Check a company symbol with recursive binary search."""
    company_symbols = list(get_company_lookup(records).keys())
    company_symbols = bubble_sort_text(company_symbols)
    position = recursive_binary_search(
        company_symbols, symbol, 0, len(company_symbols) - 1
    )
    return position != -1


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
    """Show the valid company symbols and names."""
    company_lookup = get_company_lookup(records)
    symbols = bubble_sort_text(list(company_lookup.keys()))

    print("\nAvailable companies:")
    for symbol in symbols:
        print(f"  {symbol} - {company_lookup[symbol]}")


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


def get_company_symbol(records, allow_blank):
    """Ask for a valid company symbol."""
    while True:
        symbol = input("Company symbol: ").strip().upper()

        if symbol == "" and allow_blank:
            return ""

        if company_symbol_exists(records, symbol):
            return symbol

        if allow_blank:
            print("Unknown symbol. Enter a listed symbol or press Enter for all.")
        else:
            print("Unknown symbol. Enter one of the listed symbols.")


def ask_for_filters(records):
    """Collect filter values from the user."""
    display_company_list(records)
    print("Press Enter to skip any filter.")

    symbol = get_company_symbol(records, allow_blank=True)
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


def get_record_sort_value(record, sort_key):
    """Return the value used to compare two records."""
    if sort_key == "date":
        return record["date"]
    if sort_key == "close":
        return record["close"]
    return calculate_percentage_change(record)


def bubble_sort_records(records, sort_key, descending=False):
    """Return stock records ordered with the bubble sort algorithm."""
    sorted_records = records.copy()
    number_of_records = len(sorted_records)

    for end_position in range(number_of_records - 1, 0, -1):
        swapped = False

        for index in range(end_position):
            left_value = get_record_sort_value(sorted_records[index], sort_key)
            right_value = get_record_sort_value(
                sorted_records[index + 1], sort_key
            )

            wrong_order = left_value > right_value
            if descending:
                wrong_order = left_value < right_value

            if wrong_order:
                sorted_records[index], sorted_records[index + 1] = (
                    sorted_records[index + 1],
                    sorted_records[index],
                )
                swapped = True

        if not swapped:
            break

    return sorted_records


def get_menu_choice(prompt, valid_choices):
    """Ask for one value from a list of valid choices."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please select one of the listed options.")


def get_positive_integer(prompt, minimum_value, maximum_value):
    """Ask for an integer inside an accepted range."""
    while True:
        number_text = input(prompt).strip()
        try:
            number = int(number_text)
            if minimum_value <= number <= maximum_value:
                return number
            print(
                f"Enter a whole number from {minimum_value} "
                f"to {maximum_value}."
            )
        except ValueError:
            print("Invalid number. Enter a whole number.")


def ask_for_sort(records):
    """Ask how to sort the current results."""
    if not records:
        print("\nThere are no current records to sort.")
        return records

    print("\nSort by:")
    print("1. Date")
    print("2. Closing price")
    print("3. Percentage price change")
    sort_choice = get_menu_choice("Choose 1-3: ", ["1", "2", "3"])

    sort_keys = {"1": "date", "2": "close", "3": "change"}

    print("\nOrder:")
    print("1. Lowest to highest")
    print("2. Highest to lowest")
    order_choice = get_menu_choice("Choose 1 or 2: ", ["1", "2"])

    sorted_records = bubble_sort_records(
        records,
        sort_keys[sort_choice],
        descending=(order_choice == "2"),
    )
    print("The current records have been sorted.")
    return sorted_records


def show_largest_changes(records):
    """Display records with the highest or lowest daily changes."""
    if not records:
        print("\nThere are no current records to analyse.")
        return

    print("\nPrice change analysis:")
    print("1. Highest percentage changes")
    print("2. Lowest percentage changes")
    change_choice = get_menu_choice("Choose 1 or 2: ", ["1", "2"])

    maximum_count = min(10, len(records))
    count = get_positive_integer(
        f"How many records should be shown (1-{maximum_count})? ",
        1,
        maximum_count,
    )

    sorted_records = bubble_sort_records(
        records,
        "change",
        descending=(change_choice == "1"),
    )
    display_records(sorted_records[:count])


def create_closing_price_chart(records):
    """Create and save a simple text bar chart for one company."""
    if not records:
        print("\nThere is no data available for a chart.")
        return None

    display_company_list(records)
    symbol = get_company_symbol(records, allow_blank=False)
    company_records = filter_stock_records(records, symbol=symbol)
    company_records = bubble_sort_records(company_records, "date")

    maximum_price = max(record["close"] for record in company_records)
    chart_width = 40
    company_name = company_records[0]["company"]

    chart_lines = [
        f"Closing Price Chart: {company_name} ({symbol})",
        "Each # represents a relative part of the highest closing price.",
        "",
    ]

    for record in company_records:
        bar_length = round(record["close"] / maximum_price * chart_width)
        bar = "#" * max(1, bar_length)
        chart_lines.append(
            f"{record['date'].isoformat()} | {record['close']:>7.2f} | {bar}"
        )

    chart_text = "\n".join(chart_lines)
    print()
    print(chart_text)

    try:
        OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_FOLDER / f"{symbol}_closing_price_chart.txt"
        output_file.write_text(chart_text + "\n", encoding="utf-8")
        print(f"\nChart saved to: output/{output_file.name}")
        return output_file
    except (OSError, PermissionError) as error:
        print(f"\nError: The chart could not be saved ({error}).")
        return None


def get_output_filename():
    """Ask for a safe CSV filename without folders or special characters."""
    while True:
        filename = input(
            "Output filename (press Enter for filtered_results.csv): "
        ).strip()

        if filename == "":
            return "filtered_results.csv"

        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        filename_path = Path(filename)
        name_without_extension = filename_path.stem
        valid_characters = all(
            character.isalnum() or character in "-_"
            for character in name_without_extension
        )

        if (
            filename_path.name == filename
            and filename_path.suffix.lower() == ".csv"
            and name_without_extension
            and valid_characters
        ):
            return filename

        print("Use only letters, numbers, hyphens, or underscores in the name.")


def save_records_to_csv(records):
    """Write the current records to a new CSV file."""
    if not records:
        print("\nThere are no current records to save.")
        return None

    filename = get_output_filename()

    try:
        OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_FOLDER / filename

        with output_file.open("w", encoding="utf-8", newline="") as csv_file:
            fieldnames = REQUIRED_COLUMNS + [
                "price_change",
                "percentage_change",
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for record in records:
                output_record = {
                    "symbol": record["symbol"],
                    "company": record["company"],
                    "date": record["date"].isoformat(),
                    "open": f"{record['open']:.2f}",
                    "high": f"{record['high']:.2f}",
                    "low": f"{record['low']:.2f}",
                    "close": f"{record['close']:.2f}",
                    "volume": record["volume"],
                    "price_change": f"{calculate_price_change(record):.2f}",
                    "percentage_change": (
                        f"{calculate_percentage_change(record):.2f}"
                    ),
                }
                writer.writerow(output_record)

        print(f"Records saved to: output/{output_file.name}")
        return output_file

    except (OSError, PermissionError, csv.Error) as error:
        print(f"Error: The records could not be saved ({error}).")
        return None


def group_records_by_company(records):
    """Group stock records by symbol in a dictionary of lists."""
    company_groups = {}

    for record in records:
        symbol = record["symbol"]
        if symbol not in company_groups:
            company_groups[symbol] = []
        company_groups[symbol].append(record)

    return company_groups


def calculate_company_summary(company_records):
    """Calculate useful performance values for one company."""
    sorted_records = bubble_sort_records(company_records, "date")
    first_record = sorted_records[0]
    last_record = sorted_records[-1]

    closing_price_total = 0
    total_volume = 0
    lowest_close = first_record["close"]
    highest_close = first_record["close"]

    for record in sorted_records:
        closing_price_total += record["close"]
        total_volume += record["volume"]

        if record["close"] < lowest_close:
            lowest_close = record["close"]
        if record["close"] > highest_close:
            highest_close = record["close"]

    average_close = closing_price_total / len(sorted_records)
    overall_change = last_record["close"] - first_record["open"]
    overall_percentage_change = overall_change / first_record["open"] * 100

    if overall_percentage_change > 0:
        trend = "Up"
    elif overall_percentage_change < 0:
        trend = "Down"
    else:
        trend = "Flat"

    return {
        "symbol": first_record["symbol"],
        "company": first_record["company"],
        "record_count": len(sorted_records),
        "average_close": average_close,
        "lowest_close": lowest_close,
        "highest_close": highest_close,
        "overall_percentage_change": overall_percentage_change,
        "total_volume": total_volume,
        "trend": trend,
    }


def get_company_summary_sort_value(summary, sort_key):
    """Return the selected comparison value from a company summary."""
    if sort_key == "symbol":
        return summary["symbol"]
    if sort_key == "average_close":
        return summary["average_close"]
    if sort_key == "total_volume":
        return summary["total_volume"]
    return summary["overall_percentage_change"]


def bubble_sort_company_summaries(summaries, sort_key, descending=False):
    """Order company summaries using the bubble sort algorithm."""
    sorted_summaries = summaries.copy()
    number_of_summaries = len(sorted_summaries)

    for end_position in range(number_of_summaries - 1, 0, -1):
        swapped = False

        for index in range(end_position):
            left_value = get_company_summary_sort_value(
                sorted_summaries[index], sort_key
            )
            right_value = get_company_summary_sort_value(
                sorted_summaries[index + 1], sort_key
            )

            wrong_order = left_value > right_value
            if descending:
                wrong_order = left_value < right_value

            if wrong_order:
                sorted_summaries[index], sorted_summaries[index + 1] = (
                    sorted_summaries[index + 1],
                    sorted_summaries[index],
                )
                swapped = True

        if not swapped:
            break

    return sorted_summaries


def build_company_summary_report(summaries, record_count):
    """Create a formatted text report from company summaries."""
    header = (
        f"{'Symbol':<8} {'Company':<22} {'Records':>7} "
        f"{'Avg Close':>10} {'Lowest':>9} {'Highest':>9} "
        f"{'Change %':>10} {'Volume':>12} {'Trend':>7}"
    )
    line = "-" * len(header)

    report_lines = [
        "COMPANY PERFORMANCE SUMMARY",
        f"Records analysed: {record_count}",
        f"Companies included: {len(summaries)}",
        "Overall change compares the first opening price with the last closing price.",
        "",
        line,
        header,
        line,
    ]

    for summary in summaries:
        report_lines.append(
            f"{summary['symbol']:<8} {summary['company']:<22} "
            f"{summary['record_count']:>7} "
            f"{summary['average_close']:>10.2f} "
            f"{summary['lowest_close']:>9.2f} "
            f"{summary['highest_close']:>9.2f} "
            f"{summary['overall_percentage_change']:>+9.2f}% "
            f"{summary['total_volume']:>12,d} "
            f"{summary['trend']:>7}"
        )

    report_lines.append(line)
    return "\n".join(report_lines)


def create_company_performance_report(records):
    """Display and save a comparison report for the current records."""
    if not records:
        print("\nThere are no current records to summarise.")
        return None

    company_groups = group_records_by_company(records)
    summaries = []

    for symbol in company_groups:
        summary = calculate_company_summary(company_groups[symbol])
        summaries.append(summary)

    print("\nSort the company summary by:")
    print("1. Company symbol")
    print("2. Average closing price")
    print("3. Overall percentage change")
    print("4. Total trading volume")
    sort_choice = get_menu_choice("Choose 1-4: ", ["1", "2", "3", "4"])

    sort_keys = {
        "1": "symbol",
        "2": "average_close",
        "3": "change",
        "4": "total_volume",
    }

    print("\nOrder:")
    print("1. Lowest to highest")
    print("2. Highest to lowest")
    order_choice = get_menu_choice("Choose 1 or 2: ", ["1", "2"])

    summaries = bubble_sort_company_summaries(
        summaries,
        sort_keys[sort_choice],
        descending=(order_choice == "2"),
    )
    report_text = build_company_summary_report(summaries, len(records))

    print()
    print(report_text)

    try:
        OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_FOLDER / "company_performance_summary.txt"
        output_file.write_text(report_text + "\n", encoding="utf-8")
        print(f"\nSummary saved to: output/{output_file.name}")
        return output_file
    except (OSError, PermissionError) as error:
        print(f"\nError: The summary could not be saved ({error}).")
        return None


def display_main_menu(current_count, total_count):
    """Show all available program actions."""
    print("\n" + "=" * 56)
    print("STOCK PRICE DATA PROCESSOR")
    print(f"Current records: {current_count} of {total_count}")
    print("=" * 56)
    print("1. View current records")
    print("2. Filter records")
    print("3. Sort current records")
    print("4. Show highest or lowest price changes")
    print("5. Create a closing-price text chart")
    print("6. Save current records to CSV")
    print("7. Create a company performance summary")
    print("8. Reset filters")
    print("9. Exit")


def main():
    """Load the data and run the command-line menu."""
    all_records = load_stock_data(DATA_FILE)

    if not all_records:
        print("The program cannot start because no valid records were loaded.")
        return

    current_records = all_records.copy()
    print(f"Loaded {len(all_records)} valid stock records.")

    while True:
        display_main_menu(len(current_records), len(all_records))
        choice = get_menu_choice("Choose an option (1-9): ", list("123456789"))

        if choice == "1":
            display_records(current_records)
        elif choice == "2":
            current_records = ask_for_filters(all_records)
            print(f"Matching records: {len(current_records)}")
        elif choice == "3":
            current_records = ask_for_sort(current_records)
        elif choice == "4":
            show_largest_changes(current_records)
        elif choice == "5":
            create_closing_price_chart(all_records)
        elif choice == "6":
            save_records_to_csv(current_records)
        elif choice == "7":
            create_company_performance_report(current_records)
        elif choice == "8":
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
