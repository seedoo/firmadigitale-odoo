
months = {
    'Jan': '0',
    'Feb': '1',
    'Mar': '2',
    'Apr': '3',
    'May': '4',
    'Jun': '5',
    'Jul': '6',
    'Aug': '7',
    'Sep': '8',
    'Oct': '9',
    'Nov': '10',
    'Dec': '11'
}


def get_format_date(date_str):
    month = date_str[:3]
    return date_str.replace(month, months[month])


print get_format_date('Jul 31 00:00:00 2013 GMT')
