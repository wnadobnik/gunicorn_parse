import pytest
from datetime import datetime
from gunicorn_parser import get_gunicorn_logs, get_date
import pytz
# tests for the get date method
LOGFILE = 'gunicorn.log2'
def test_date_formats():
    dates = [
        {'year': 1990, 'month': 12, 'day': 11, 'hour': 0, 'minute': 0, 'second': 0, 'input': '11-12-1990'},
        {'year': 1990, 'month': 12, 'day': 11, 'hour': 12, 'minute': 0, 'second': 0, 'input': '11-12-1990_12'},
        {'year': 1990, 'month': 12, 'day': 11, 'hour': 12, 'minute': 12, 'second': 0, 'input': '11-12-1990_12-12'},
        {'year': 1990, 'month': 12, 'day': 11, 'hour': 12, 'minute': 12, 'second': 12, 'input': '11-12-1990_12-12-12'},
    ]
    for date in dates:
        test_date = datetime(year=date['year'], month=date['month'], day=date['day'],
                             hour=date['hour'], minute=date['minute'], second=date['second'],
                             tzinfo=pytz.timezone('Europe/Warsaw'))
        assert get_date(date['input'], 'from') == test_date

def test_date_from_blank():
    test_date = datetime(year=1900, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.timezone('Europe/Warsaw'))
    assert get_date('', 'from') == test_date

def test_date_to_blank():
    start = datetime.now().replace(tzinfo=pytz.timezone('Europe/Warsaw'))
    blank_from = get_date('', 'to')
    stop = datetime.now().replace(tzinfo=pytz.timezone('Europe/Warsaw'))
    assert start <= blank_from <= stop

def test_to_from_confusion():
    with pytest.raises(ValueError):
        get_gunicorn_logs('11-12-1990','01-12-1990', LOGFILE)

def test_empty_logs():
    results = get_gunicorn_logs('11-12-1990','12-12-1990', LOGFILE)
    assert results['avg_size'] == 0
    assert results['total_size'] == 0
    assert results['count'] == 0
    assert results['requests_sec'] == 0

def test_no_timespan():
    results = get_gunicorn_logs('', '', LOGFILE)
    assert results['count'] == 99999
    assert '404' and '200' in results['responses'].keys()
    assert results['avg_size'] != 0
    assert results['total_size'] != 0
    assert results['count'] != 0
    assert results['requests_sec'] != 0

def test_comprehensive_timespan():
    results = get_gunicorn_logs('06-09-2019_09-07-17', '08-01-2020_14-04-44', LOGFILE)
    assert results['count'] == 99999
    assert '404' and '200' in results['responses'].keys()
    assert results['avg_size'] != 0
    assert results['total_size'] != 0
    assert results['count'] != 0
    assert results['requests_sec'] != 0

def test_slicing_timespan():
    results = get_gunicorn_logs('06-09-2019_09-07-17', '01-12-2019', LOGFILE)
    assert results['count'] < 99999
    assert '404' and '200' in results['responses'].keys()
    assert results['avg_size'] != 0
    assert results['total_size'] != 0
    assert results['count'] != 0
    assert results['requests_sec'] != 0


def test_file_exists_error():
    test_values = ['gunicor.log2', 'gunicorn', '']
    for value in test_values:
        with pytest.raises(FileExistsError):
            get_gunicorn_logs('', '', value)

