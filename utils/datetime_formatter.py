import datefinder


def get_formatted_date(date):
    date = list(datefinder.find_dates(date))
    if not date:
        return []
    else:
        return date
