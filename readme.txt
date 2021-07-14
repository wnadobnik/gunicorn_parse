The script requires pytz library
To run script, enter following command in your shell:
py gunicorn_parser.py <name_of file to parse>
The script takes two optional arguments:
--from <date>
--to <date>
The dates take format: dd-mm-yyyyy_hh-mm-ss. Hours, minutes and seconds can be ommited

To run tests of the program, enter "pytest" command in your shell (pytest library required)