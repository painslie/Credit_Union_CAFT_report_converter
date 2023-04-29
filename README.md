# Credit_Union_CAFT_report_converter
Used to convert CAFT pdf reports to CSV files (Excel)


Examples

```
$ python3 main.py --help

main.py -r <report type> -f <input file name, use wildcard for multiple files> -o <output file name>

$ python3 main.py -r AFTR0003 -f "*2002*.pdf" -o output.csv
```
