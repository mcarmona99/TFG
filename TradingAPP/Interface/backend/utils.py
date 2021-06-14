from datetime import datetime


# Transformar cada fecha de datetime-local a datetime
def transform_date(date):
    date_processing = date.replace('T', '-').replace(':', '-').split('-')
    date_processing = [int(v) for v in date_processing]
    return datetime(*date_processing)
