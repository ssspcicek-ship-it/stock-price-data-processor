STOCK PRICE DATA PROCESSOR
IY499 Practical Programming Assignment

STUDENT INFORMATION

Name: Suat Pembeçiçek
P number: P507017
Student ID: 303066702
Course code: IY499

ONLINE REPOSITORY

https://github.com/ssspcicek-ship-it/stock-price-data-processor

DECLARATION OF OWN WORK

I confirm that this submission is my own work. Any copied code, data, or ideas
from another source have been clearly identified and referenced.

REQUIRED SUBMISSION PARAGRAPH

Your project should be submitted as a .zip file with all your source code and
your README included. The README should be either a .txt or a .docx file.

PROGRAM DESCRIPTION 

The Stock Price Data Processor is a command-line Python program that reads
historical stock records from a CSV file. It uses a list of dictionaries to
store the records. The user can view the data, filter it by company, date
range, or closing-price range, and sort the current results by date, closing
price, or percentage price change. The program can also show the records with
the highest or lowest daily price changes. A recursive binary search checks
company symbols, while bubble sort is used to order the data. These algorithms
are included to show searching, sorting, recursion, and Big-O concepts from the
module. The menu checks invalid input and asks the user to try again instead of
ending unexpectedly. The user can create a simple text bar chart of a
company's closing prices and save the current results to a new CSV file. Output
files are placed in the output folder, which is created automatically. The
included dataset contains fictional companies and sample values made for this
assignment. It can be replaced with another CSV file that uses the same column
headings.

FILES

stock_price_processor.py
    Main Python program.

data/stock_prices.csv
    Sample input dataset used by the program.

output/
    Created automatically when the program saves a CSV file or text chart.

PACKAGES AND LIBRARIES

No third-party packages are required. The program uses these Python standard
library modules:

- csv
- datetime
- pathlib

INSTALLATION

1. Install Python 3.10 or a later version.
2. Extract the submission ZIP file.
3. Open a Terminal or Command Prompt in the Stock_Price_Data_Processor folder.

No pip installation is needed.

HOW TO RUN THE PROGRAM

On macOS or Linux, run:

python3 stock_price_processor.py

On Windows, run:

py stock_price_processor.py

HOW TO USE THE PROGRAM

Choose an option from the numbered menu. Press Enter when a filter should not
be used. A price filter uses the closing price. Saved CSV files and text charts
are written to the output folder. Use option 7 to restore all records and
option 8 to close the program.

ALGORITHMS

- Filtering uses linear search: O(n).
- Company validation uses recursive binary search: O(log n).
- Record sorting uses bubble sort: O(n^2).

DATA AND REFERENCES

The sample dataset is original fictional data created for this assignment. No
online code snippets or external datasets are used.
