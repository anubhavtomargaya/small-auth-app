from datetime import datetime, timedelta
def get_timerange(start:datetime=datetime.utcnow(),
                  n=7):
    """ get before and after values (date strings) for the gmail search query
    returns: before, after for the specified date diff -> n"""
    print("todadao",start.hour + 5)
    today = datetime.date(start.replace(hour=(start.hour + 5))) + timedelta(days=1)
    print(today)

    return today.__str__(), (today - timedelta(days=n)).__str__()


if __name__ =='__main__':
    print(get_timerange())