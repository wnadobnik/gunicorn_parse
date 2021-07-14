import os.path as file
import getopt, sys
from re import search, match
from datetime import datetime
from pytz import timezone


def get_gunicorn_logs(date_from='', date_to='', logfile=''):
    # date and time pattern (accepts: dd-mm-yyyy_hh-mm-ss). H
    # hours, minutes and seconds can be skipped. For each skipped value 0 is assumed
    date_limits = {}
    date_limits['from'], date_limits['to'], = get_date(date_from, 'from'), get_date(date_to, 'to')
    if date_limits['from'] >= date_limits['to']:
        raise ValueError('"To" date should be later than "from" date')
    results = {}
    results['count'] = 0
    results['total_size'] = 0
    results['responses'] = {}
    location = {}
    if not file.isfile(logfile):
        raise FileExistsError(f"The {logfile} file doesn't exsist!")
    with open(logfile) as f:
        # skip introductory line
        f.readline()
        for line in f:
            # extract the date from the string
            location['date_location_start'] = line.rfind('[')
            location['date_location_end '] = line.rfind(']')
            log_date = datetime.strptime(
                line[location['date_location_start']:
                     location['date_location_end ']],
                '[%d/%b/%Y:%H:%M:%S %z'
            )
            if date_limits['from'] <= log_date <= date_limits['to']:
                # get response code, log it in responses dictionary
                response = search(' \\d{3} ', line).group(0).replace(' ', '')
                if response in results['responses'].keys():
                    results['responses'][response] += 1
                else:
                    results['responses'][response] = 1
                # extract response size if its number starts with 2
                if response[0] == '2':
                    # extract response size
                    location['response_size'] = line.rfind(' ')
                    results['total_size'] += int(line[location['response_size']:])
                results['count'] += 1
        f.close()
        #if from or to date wasn't set at the beginning, get them for calculation

        # get start end end date from the file if none were given

    # calculate average response size, pass zero if no record were found
    results['2xx_responses'] = sum(v for k, v in results['responses'].items() if k[0] == '2')
    results['2xx_avg_size'] = format((results['total_size'] / results['2xx_responses']) / 1000000, ".2f") if results['count'] else 0
    # calculate average of requests pers second)
    results['requests_sec'] = format(results['count'] / (date_limits['to'] - date_limits['from']).total_seconds(), ".2f")

    return results


def get_date(date, date_type):
    # pattern to used to standardize date input and default "from" date
    pattern = '01-01-1900_00-00-00'
    # supplement input date with the pattern to make it fit to the dd-mm-yyyy_hh-mm-ss format
    increment = date + pattern[len(date):]
    #if date was not set, create dummy to keep main loop simple
    if not date:
        if date_type == 'from':
            date_conv = datetime(year=1900, month=1, day=1)
        elif date_type == 'to':
            date_conv = datetime.now()
    elif match(r'^(\d{2}-){2}\d{4}_(\d{2}-){2}\d{2}', increment):
        date_conv = datetime.strptime(increment, '%d-%m-%Y_%H-%M-%S')
    else:
        raise ValueError('Date format is not proper')
    return date_conv.replace(tzinfo=timezone('Europe/Warsaw'))

options, remainder = getopt.getopt(sys.argv[1:], '', ['from=',
                                                         'to='])
date_from = ''
date_to = ''
logfile = ''
for option, argument in options:
    if option == "--from":
        date_from = argument
    elif option == '--to':
        date_to = argument
if remainder:
    logfile = remainder[0]
else:
    raise ValueError('Filename was not found!')
results = get_gunicorn_logs(date_from, date_to, logfile)
responses = ''
for key, value in results['responses'].items():
    responses += f'[{key}]: {value} '
print(f"requests: {results['count']} \n"
    f"requests/sec: {results['requests_sec']}\n"
    f"responses: {responses}\n" 
    f"average size of 2xx request: {results['2xx_avg_size']}")