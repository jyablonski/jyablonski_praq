# Given a date, return the corresponding day of the week for that date.

# The input is given as three integers representing the day, month and year respectively.

# Return the answer as one of the following values:
# {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}.

from datetime import datetime


def solution(day: int, month: int, year: int) -> str:
    date_formatted = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
    weekday = date_formatted.strftime("%A")
    return weekday


day1 = 31
month1 = 8
year1 = 2019

solution(day=day1, month=month1, year=year1)

d = datetime.now().date()
