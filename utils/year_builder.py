import os
import csv
from datetime import datetime, timedelta
import calendar

DATA_PATH = "./repository/data"

#get year data file
def get_year_file(year: int):
    return os.path.join(DATA_PATH, f"{year}.csv")


def ensure_year_file(year: int):
    #gets the file in ./repository/data
    filepath = get_year_file(year)

    #if it exists, the return it.
    if os.path.exists(filepath):
        return filepath
    
    #if it doesn't, then make it.
    os.makedirs(DATA_PATH, exist_ok=True)

    #open the newly made .csv file with the year
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        #2025-01-01,Monday,January,1,1
        writer.writerow(["date", "day", "month", "week", "working_day"])

        #start at January 1, end at January 1 next year (not included)
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)

        #week counter / index
        current = start
        week_index = 1

        #while it's not January 1st of the next year:
        while current < end:

            #2d representation of the month. 1 row = 1 week.
            #if there's extra days from previous months, then they will be represented as 0s
            #so if a month starts on a monday the week array'll be [0,0,0,1,2,3,4] (starting Sunday)
            month_calendar = calendar.monthcalendar(year, current.month)
            week_of_month = None

            #find the "extra" days in the month (see line 44 with the example). i don't know if they have a name.
            #i kinda took this from geeksforgeeks
            for idx, w in enumerate(month_calendar):
                if current.day in w:
                    week_of_month = idx + 1
                    break

            #assumes the day is valid until checked
            weekday_index = current.weekday()
            belongs_to_month = True

            #checks if the date is a "spillover" day. They do have a name!
            cal_row = month_calendar[week_of_month - 1]
            if cal_row[weekday_index] == 0:
                belongs_to_month = False

            #bool to 1 and 0 to write it down.
            working = 1 if belongs_to_month else 0

            #write on the file
            writer.writerow([
                current.strftime("%Y-%m-%d"),
                current.strftime("%A"),
                current.strftime("%B"),
                week_index,
                working
            ])

            #restart the week and add a +1 to the index
            if weekday_index == 6:
                week_index += 1

            #move to the next calendar day
            current += timedelta(days=1)

    #return the filepath
    return filepath


#read just the current date + 2 weeks from now
def read_filtered(year: int, full_view: bool = False):
    filepath = ensure_year_file(year)

    today = datetime.now().date()
    two_weeks_from_now = today + timedelta(days=14)

    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row_date = datetime.strptime(row["date"], "%Y-%m-%d").date()

            if full_view:
                rows.append(row)
            else:
                if today <= row_date <= two_weeks_from_now:
                    rows.append(row)

    return rows

#read entire month
def read_month(year: int, month: int):
    filepath = ensure_year_file(year)

    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row_date = datetime.strptime(row["date"], "%Y-%m-%d").date()

            if row_date.month == month:
                if row["working_day"] == "1":
                    rows.append(row)

    return rows