# Credit_Union_CAFT_report_converter
Used to convert Credit Union Central (Canada) CAFT reports from PDF to CSV files (Excel, google sheet, etc.)

# Prerequisites
Initial setup requires installation of the following.

```bash
$ pip3 install pdfplumber
```

# Usage

```bash
$ python3 main.py --help
main.py -r <report type> -f <input file name, use wildcard for multiple files> -o <output file name>
````

Command line Examples

```bash

$ python3 main.py -r AFTR0003 -f "*2002*.pdf" -o output.csv

$ python3 main.py -r CAFT002 -f "*2002*.pdf" -o output.csv

$ -r CAFT002 -f "/Users/me/2022/01-Jan/Crys*.pdf" -o /Users/me/2022/01-Jan/temp_output.csv
```
