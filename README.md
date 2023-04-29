# Credit_Union_CAFT_report_converter
Used to convert Credit Union Central (Canada) CAFT reports from PDF to CSV files (Excel, google sheet, etc.)


Examples

```
$ python3 main.py --help

main.py -r <report type> -f <input file name, use wildcard for multiple files> -o <output file name>

$ python3 main.py -r AFTR0003 -f "*2002*.pdf" -o output.csv
```
