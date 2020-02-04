import datetime


def get_rpg_date(time_stamp):
    epoch = datetime.datetime(2001, 1, 1).timestamp()
    time_stamp += epoch
    return datetime.datetime.utcfromtimestamp(time_stamp).strftime('%Y %m %d').split()
