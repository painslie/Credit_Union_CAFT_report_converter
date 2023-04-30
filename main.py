import pdfplumber
import datetime
import csv

import glob

import sys
import getopt

# Function to convert Credit Union CAFT pdf reports to CSV files.
#
#

# Initial setup:
# pip install pdfplumber

# Class of different styles/colors
class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    RESET = '\033[0m'


def get_commandline_arguments(argv):

    arg_report_type = ""
    arg_input_file_wildcard = ""
    arg_output_file = ""
    arg_help = "{0} -r <report type> -f <input file name, use wildcard for multiple files> -o <output file name>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hr:f:o:", ["help", "report_type=",
        "input_file_wildcard=", "output_file="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-r", "--report_type"):
            arg_report_type = arg
        elif opt in ("-f", "--input_file_wildcard"):
            arg_input_file_wildcard = arg
        elif opt in ("-o", "--output_file"):
            arg_output_file = arg

    print('Report Type:               ', arg_report_type)
    print('Input Path\File (wildcard):', arg_input_file_wildcard)
    print('Output Path\File:          ', arg_output_file, '\n')

    return(arg_report_type, arg_input_file_wildcard, arg_output_file)


def main(arg_report_type, arg_input_file_wildcard, arg_output_file):

    rows = []
    fields = []
    grand_total = 0

    arr_of_files = (glob.glob(arg_input_file_wildcard))

    if arr_of_files:
        for file in arr_of_files:
            with pdfplumber.open(file) as pdf:
                pdfToString = ""
                for page in pdf.pages:
                    pdfToString += page.extract_text()
                    pdfToString += "\n"
                pdf.close()
                print(file)
                if arg_report_type == "AFTR0003":
                    rows_result, fields, statement_total_result = parse_AFTR0003_pdf_to_string(pdfToString)
                elif arg_report_type == "CAFT002":
                    rows_result, fields, statement_total_result = parse_CAFT002_pdf_to_string(pdfToString)

                rows += rows_result
                grand_total += statement_total_result

        print("\n" + style.CYAN + "Grand Total:", round(grand_total,2))

        # write to CSV file
        with open(arg_output_file, 'w') as f:
            write = csv.writer(f)   # Create a CSV writer object that will write to the file 'f'
            write.writerow(fields)  # Write the field names (column headers) to the first row of the CSV file
            write.writerows(rows)   # Write all of the rows of data to the CSV file
    else:
        print("\nError: No files found for:", arg_input_file_wildcard)

def parse_AFTR0003_pdf_to_string(pdfToString):

    reportType = ""
    fields = ""
    rows = []
    payment_check_sum = 0

    for line in pdfToString.splitlines():
        line_list = line.split(" ")

        # Confirm if report type is AFTR0003; as soon as keyword is found,
        if line.find("AFTR0003") > -1:
            reportType = "CAFT_AFTR0003"
            fields = ['Cross Reference', 'Due Date', 'TX Type', 'Transit Route', 'Account Number', 'Amount', 'Item Trace No.', 'Payee Name', 'Invalid Field Numbers']

        # Parse AFTR0003 report line
        if reportType == "CAFT_AFTR0003":
            if line.find("470D") > -1:
                payment_check_sum = float(line_list[5]) + payment_check_sum

                # Convert from Julian date to regular date
                line_list[1] = datetime.datetime.strptime(line_list[1], '%y%j').strftime("%Y-%m-%d")

                # Convert ' OR ' to '-OR-' so it parses properly
                if len(line_list) > 8:
                    if line_list[8] == "OR":
                        line_list[7] += '-OR-' + line_list[9]
                        del line_list[9]  # remove last item
                        del line_list[8]  # remove 2nd last item

                rows.append(line_list)

            # Check sums for AFTR0003 report
            if line.find("TOTAL") > -1:
                statement_total = float(line_list[3].replace(',',''))  # remove comma from value

                if line.find("PAYMENTS") > -1:
                    if statement_total == payment_check_sum:
                        # line_list[0] is usually = 'TOTAL', line_list[1] is e.g., = 'REVERSALS', line_list[3] is the amount
                        print("{:<2} {:<17} {:<10} {:<10}".format(' ', line_list[0] + ' ' + line_list[1], line_list[3], style.GREEN + "✔ Balanced!" + style.RESET))
                    else:
                        print("{:<2} {:<17} {:<10} {:<30} {:<30}  {:<1}".format(' ', "TOTAL PAYMENTS:", statement_total, style.RED + "✘ ERROR: Not balanced!  Check Sum:", payment_check_sum,  style.RESET))
                else:
                    if statement_total == 0:
                        print("{:<2} {:<17} {:<10} {:<10}".format(' ', line_list[0] + ' ' + line_list[1], line_list[3], style.GREEN + "✔" + style.RESET))
                    else:
                        print("  ", line_list[0], line_list[1], line_list[3], " x Error: no trx found!")

    return(rows, fields, payment_check_sum)

def parse_CAFT002_pdf_to_string(pdfToString):

    reportType = ""
    fields = ""
    rows = []
    payment_check_sum = 0
    statement_total = 0

    last_row = pdfToString.count('\n')
    current_row = 0

    for line in pdfToString.splitlines():
        current_row += 1
        line_list = line.split(" ")

        # Confirm if report type is CAFT 002; as soon as keyword is found,
        if line.find("CAFT 002") > -1:
            reportType = "CAFT002"
            fields = ['Payee', 'Cross Ref', 'ID', 'Route', 'Transit', 'Account', 'Amount', 'Rec Type', 'TX Type',
                      'Due Date', 'Freq', 'Expiry Date', 'Sundry Information']

        # Parse CAFT002 report line
        if reportType == "CAFT002":
            if line.find("470") > -1:
                # Concatentate the 1st two values
                if line_list.index("470") == 8:
                    pass
                elif line_list.index("470") == 9:
                    line_list[0] += line_list[1]
                    del line_list[1]
                elif line_list.index("470") == 10:
                    line_list[0] += line_list[1] + line_list[2]
                    del line_list[2]
                    del line_list[1]

                elif line_list.index("470") == 11:
                    # Convert ' OR ' to '-OR-' so it parses properly
                    if line_list[2] == "OR":
                        line_list[0] += line_list[1] + '-OR-' + line_list[3]
                    del line_list[3]
                    del line_list[2]
                    del line_list[1]

                line_list[6] = float(line_list[6].replace(',', ''))  # remove comma from value
                payment_check_sum = float(line_list[6]) + payment_check_sum

                print(line_list.index("470"), line_list[0], line_list[6])

                # Convert date, e.g., from '2023-Jan-27' date to '2023-01-27'
                line_list[9] = datetime.datetime.strptime(line_list[9], "%Y-%b-%d").strftime("%Y-%m-%d")
                if len(line_list) >= 12:
                    line_list[11] = datetime.datetime.strptime(line_list[11], "%Y-%b-%d").strftime("%Y-%m-%d")

                rows.append(line_list)

            # Check Net Total if the last row of the statement
            if line.find("Net Total") > -1:
                statement_total += float(line_list[2].replace(',',''))  # remove comma from value

                if current_row == last_row:
                    if round(statement_total,2) == round(payment_check_sum,2):
                        print("{:<17} {:<10} {:<10}".format('   Net Total:', round(statement_total,2), style.GREEN + "✔ Balanced!" + style.RESET))
                    else:
                        print("{:<17} {:<10} {:<30} {:<30}  {:<1}".format('   Net Total:', round(statement_total,2),
                                                                                style.RED + "✘ ERROR: Not balanced!  Check Sum:",
                                                                                round(payment_check_sum,2), style.RESET))

    return(rows, fields, payment_check_sum)


# Driver Code
if __name__ == '__main__':

    arg_report_type, arg_input_file_wildcard, arg_output_file = get_commandline_arguments(sys.argv)

    # Calling main() function
    main(arg_report_type, arg_input_file_wildcard, arg_output_file)