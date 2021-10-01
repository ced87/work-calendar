import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import datefinder

# If modifying these scopes, delete the file token.pkl.
# Scopes are basically paths for different permissions.
scope = ['https://www.googleapis.com/auth/calendar']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', scope)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', scope)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

calendar_list = service.calendarList().list().execute()

# load in the duties and rota dictionary.
duties = json.load(open('duties.json', 'r'))

print("\n### This program will enter "
      "West Ruislip work duties & rest days into your Google Calendar ###")

# Check if user made calendar selections in the past.
# If not, save the current selections for future use.
if os.path.exists('./calendar_ids.json'):
    work_cal_id = json.load(open('./calendar_ids.json', 'r'))['work']
    rest_cal_id = json.load(open('./calendar_ids.json', 'r'))['rest']
else:
    x = 1
    print('\nThis is a list of your Google calendars: ')
    for item in calendar_list['items']:
        print(f"{x} - {calendar_list['items'][x - 1]['summary']}")
        x += 1

    while True:
        try:
            work_cal_id = int(
                input("\nEnter the number of the Google calendar to use"
                      " for work duties: ")
            )
        except IndexError:
            print('Enter a valid calendar number. Please enter again.')
        else:
            work_cal_id = calendar_list['items'][work_cal_id - 1]['id']
            break
    while True:
        try:
            rest_cal_id = int(
                input("Enter the number of the Google calendar to use for"
                      " rest days (can be the same as the duties calendar): ")
            )
        except Exception:
            print('Enter a valid calendar number. Please enter again.')
        else:
            rest_cal_id = calendar_list['items'][rest_cal_id - 1]['id']
            json.dump({'work': work_cal_id, 'rest': rest_cal_id},
                      open('./calendar_ids.json', 'w'))
            break

print(
    f"\nWork calendar selected: "
    f"{service.calendars().get(calendarId=work_cal_id).execute()['summary']}"
    f"\nRest day calendar selected: "
    f"{service.calendars().get(calendarId=rest_cal_id).execute()['summary']}\n"
    f"\nIf you want to change this selection, delete the file "
    f"'calendar_ids.json' and run again.\n"
)


# fixing the date and time because google calendar needs it in a specific way.
# "%Y-%m-%dT%H:%M:%S"
def adjust_datetime(user_date_input):
    date_matches = list(datefinder.find_dates(user_date_input))
    return date_matches[0], date_matches[0].strftime('%A')


# sending the event to google calendar
def create_duty_event(event_start_time, summary, minutes_time=1, hours_time=1,
                      description=None):
    timezone = 'Europe/London'
    start_time = datetime.strptime(event_start_time, "%Y-%m-%dT%H:%M:%S")
    end_time = start_time + \
        timedelta(minutes=minutes_time, hours=(hours_time + 0.5))
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
        },
    }
    return service.events().insert(calendarId=work_cal_id,
                                   body=event).execute()


# adding a rest day to the calendar
def create_restday_event(date_restday):
    date_fixed = date_restday.strftime('%d %b %Y')
    day = adjust_datetime(f"{date_fixed}")[1]
    next_day = date_restday + timedelta(days=1)
    event = {
        'summary': 'RD',
        'start': {
            'date': date_restday.strftime("%Y-%m-%d"),
        },
        'end': {
            'date': next_day.strftime("%Y-%m-%d"),
        },
    }
    service.events().insert(calendarId=rest_cal_id, body=event).execute()
    print(
        f"Rest day entered into calendar on "
        f'{day} {date_fixed}\n'
    )


# next few functions are for adding duties to the calendar. Work duties are
# different for Friday, Saturday, Sunday, and Monday to Thursday.
def create_sunday_event(duty_number, duty_date):
    duty_list = duties['Sun']
    date_fixed = duty_date.strftime('%d %b %Y')
    duty_date_time = adjust_datetime(
        f"{date_fixed} {duty_list[duty_number]['start']}")[0]
    duty_date_time = duty_date_time.strftime("%Y-%m-%dT%H:%M:%S")
    day = adjust_datetime(f"{date_fixed} {duty_list[duty_number]['start']}")[1]
    create_duty_event(duty_date_time,
                      duty_list[duty_number]['summary'],
                      duty_list[duty_number]['length_minutes'],
                      duty_list[duty_number]['length_hours'],
                      duty_list[duty_number]['description']
                      )
    print(f'Duty {duty_number} entered into calendar on {day} {date_fixed}\n')


def create_monday_thursday_event(duty_number, duty_date):
    duty_list = duties['MonThur']
    date_fixed = duty_date.strftime('%d %b %Y')
    duty_date_time = adjust_datetime(
        f"{date_fixed} {duty_list[duty_number]['start']}")[0]
    duty_date_time = duty_date_time.strftime("%Y-%m-%dT%H:%M:%S")
    day = adjust_datetime(f"{date_fixed} {duty_list[duty_number]['start']}")[1]
    create_duty_event(duty_date_time,
                      duty_list[duty_number]['summary'],
                      duty_list[duty_number]['length_minutes'],
                      duty_list[duty_number]['length_hours'],
                      duty_list[duty_number]['description']
                      )
    print(f'Duty {duty_number} entered into calendar on {day} {date_fixed}\n')


def create_friday_event(duty_number, duty_date):
    duty_list = duties['Fri']
    date_fixed = duty_date.strftime('%d %b %Y')
    duty_date_time = adjust_datetime(
        f"{date_fixed} {duty_list[duty_number]['start']}")[0]
    duty_date_time = duty_date_time.strftime("%Y-%m-%dT%H:%M:%S")
    day = adjust_datetime(f"{date_fixed} {duty_list[duty_number]['start']}")[1]
    create_duty_event(duty_date_time,
                      duty_list[duty_number]['summary'],
                      duty_list[duty_number]['length_minutes'],
                      duty_list[duty_number]['length_hours'],
                      duty_list[duty_number]['description']
                      )
    print(f'Duty {duty_number} entered into calendar on {day} {date_fixed}\n')


def create_saturday_event(duty_number, duty_date):
    duty_list = duties['Sat']
    date_fixed = duty_date.strftime('%d %b %Y')
    duty_date_time = adjust_datetime(
        f"{date_fixed} {duty_list[duty_number]['start']}")[0]
    duty_date_time = duty_date_time.strftime("%Y-%m-%dT%H:%M:%S")
    day = adjust_datetime(f"{date_fixed} {duty_list[duty_number]['start']}")[1]
    create_duty_event(duty_date_time,
                      duty_list[duty_number]['summary'],
                      duty_list[duty_number]['length_minutes'],
                      duty_list[duty_number]['length_hours'],
                      duty_list[duty_number]['description']
                      )
    print(f'Duty {duty_number} entered into calendar on {day} {date_fixed}\n')


# finding out the date and asking user to input the duties or days off.
def user_event_input(date_event):
    day = adjust_datetime(str(date_event))[1]
    while True:
        if day == 'Sunday':
            duty = str.upper(input('Sunday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 931):
                create_sunday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')

        elif day == 'Monday':
            duty = str.upper(input('Monday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 950):
                create_monday_thursday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')

        elif day == 'Tuesday':
            duty = str.upper(input('Tuesday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 950):
                create_monday_thursday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')

        elif day == 'Wednesday':
            duty = str.upper(input('Wednesday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 950):
                create_monday_thursday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')

        elif day == 'Thursday':
            duty = str.upper(input('Thursday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 950):
                create_monday_thursday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')

        elif day == 'Friday':
            duty = str.upper(input('Friday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 949):
                create_friday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')

        else:
            duty = str.upper(input('Saturday: '))
            if duty == 'RD' or duty == '':
                create_restday_event(date_event)
                break
            elif int(duty) in range(901, 937):
                create_saturday_event(duty, date_event)
                break
            else:
                print('Format incorrect. Please enter again.\n')


def rota_event_input(duty_number, date_event):
    day = adjust_datetime(str(date_event))[1]
    while True:
        if day == 'Sunday':
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_sunday_event(duty_number, date_event)
                break

        elif day == 'Monday':
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_monday_thursday_event(duty_number, date_event)
                break

        elif day == 'Tuesday':
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_monday_thursday_event(duty_number, date_event)
                break

        elif day == 'Wednesday':
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_monday_thursday_event(duty_number, date_event)
                break

        elif day == 'Thursday':
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_monday_thursday_event(duty_number, date_event)
                break

        elif day == 'Friday':
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_friday_event(duty_number, date_event)
                break

        else:
            if duty_number == 'r':
                create_restday_event(date_event)
                break
            else:
                create_saturday_event(duty_number, date_event)
                break


def rota_input():
    print('\n*************************'
          '\n\nRota Input')
    while True:
        while True:
            try:
                user_date_input = adjust_datetime(
                    input('\nWeek commencing (eg. 21 Jul 19): '))
            except IndexError:
                print('Date format is incorrect. Please enter again.')
            else:
                break

        user_date = user_date_input[0]
        if user_date_input[1] == 'Sunday':
            while True:
                rota_number = int(
                    input("Enter starting rota number: (1 to 71) "))
                if rota_number < 1 or rota_number > 71:
                    print('Try again.')
                else:
                    break

            while True:
                number_of_weeks = int(
                    input("Number of weeks to enter into calendar: "))
                if number_of_weeks > 5:
                    if str.upper(input(f'Number of weeks entered is'
                                       f' {number_of_weeks}, are you sure? '
                                       f'(y/n): ')) == 'Y':
                        break
                    else:
                        print('\nEnter again.\n')
                        continue
                else:
                    break

            for i in range(number_of_weeks):
                for ii in range(7):
                    rota_event_input(duties['Rota'][str(rota_number)]
                                     [str(ii + 1)], user_date)
                    user_date = user_date + timedelta(days=1)
                    ii += 1
                rota_number += 1
                i += 1
                if rota_number in [11, 25, 35, 45, 60]:
                    rota_number += 2
                    user_date = user_date + timedelta(days=14)
                    i += 2
                elif rota_number in [12, 26, 36, 46, 61, 65]:
                    rota_number += 1
                    user_date = user_date + timedelta(days=7)
                    i += 1
                elif rota_number == 72:
                    rota_number = 1

        else:
            print(
                f'The date {user_date.strftime("%d %b %Y")} is not a Sunday.'
                ' Please enter again.')
            continue

        user_continue = str.upper(input('Add duties to other weeks? (y/n): '))
        if user_continue == 'Y':
            continue
        else:
            break


def weekly_input():
    print('\n*************************'
          '\n\nWeekly Input')
    while True:
        while True:
            try:
                user_date_input = adjust_datetime(
                    input('\nWeek commencing (eg. 21 Jul 19): '))
            except IndexError:
                print('Date format is incorrect. Please enter again.')
            else:
                break

        user_date = user_date_input[0]
        if user_date_input[1] == 'Sunday':
            print('\n### Enter duty number or leave blank for rest day. ###\n')
            for i in range(7):
                user_event_input(user_date)
                user_date = user_date + timedelta(days=1)
                i += 1
        else:
            print(
                f'The date {user_date.strftime("%d %b %Y")} is not a Sunday.'
                ' Please enter again.')
            continue
        user_continue = str.upper(input('Add duties to another week? (y/n): '))
        if user_continue == 'Y':
            continue
        else:
            break


def daily_input():
    print('\n*************************'
          '\n\nDaily Input')
    while True:
        while True:
            try:
                user_date_input = adjust_datetime(
                    input('\nDate of duty or rest day (eg. 21 Jul 19): '))
            except IndexError:
                print('Date format is incorrect. Please enter again.')
            else:
                break

        user_date = user_date_input[0]
        print('\nEnter the duty number or RD for rest day.')
        user_event_input(user_date)
        user_continue = str.upper(
            input('Add more duties to a different date? (y/n): '))
        if user_continue == 'Y':
            continue
        else:
            break


# run the app
def main():
    while True:
        start_selection = input('*************************'
                                '\n\n1 - Weekly input'
                                '\n2 - Daily input'
                                '\n3 - Rota input'
                                '\n\n4 - Exit'
                                '\n\nSelect from 1 to 4: ')
        if start_selection == '1':
            weekly_input()
            break
        elif start_selection == '2':
            daily_input()
            break
        elif start_selection == '3':
            rota_input()
            break
        elif start_selection == '4':
            break
        else:
            print('Please try again.')


if __name__ == '__main__':
    main()

print('\nDuty entry done. Program ended.')
