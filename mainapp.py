import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import datefinder

# If modifying the 'scope', delete the file token.json.
# Scopes are basically paths for different permissions.
scope = ['https://www.googleapis.com/auth/calendar']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorisation flow completes for the first
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
    # Save the credentials for the next run.
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)
calendar_list = service.calendarList().list().execute()

# Load in the duties and rota dictionary.
duties = json.load(open('duties.json', 'r'))

print('\n### This program will enter '
      'West Ruislip work duties & rest days into your Google Calendar ###')

# Check if user made calendar selections in the past.
# If not, save the current selections for future use.
if os.path.exists('./calendar_ids.json'):
    work_cal_id = json.load(open('./calendar_ids.json', 'r'))['work']
    rest_cal_id = json.load(open('./calendar_ids.json', 'r'))['rest']
else:
    x = 1
    print('\nThis is a list of your Google calendars: ')
    for item in calendar_list['items']:
        print(f'{x} - {calendar_list["items"][x - 1]["summary"]}')
        x += 1

    while True:
        try:
            work_cal_id = int(
                input('\nEnter the number of the Google calendar to use'
                      ' for work duties: ')
            )
        except IndexError:
            print('Enter a valid calendar number. Please enter again.')
        else:
            work_cal_id = calendar_list['items'][work_cal_id - 1]['id']
            break
    while True:
        try:
            rest_cal_id = int(
                input('Enter the number of the Google calendar to use for'
                      ' rest days (can be the same as the duties calendar): ')
            )
        except Exception:
            print('Enter a valid calendar number. Please enter again.')
        else:
            rest_cal_id = calendar_list['items'][rest_cal_id - 1]['id']
            json.dump({'work': work_cal_id, 'rest': rest_cal_id},
                      open('./calendar_ids.json', 'w'))
            break

print(
    f'\nWork calendar selected: '
    f'{service.calendars().get(calendarId=work_cal_id).execute()["summary"]}'
    f'\nRest day calendar selected: '
    f'{service.calendars().get(calendarId=rest_cal_id).execute()["summary"]}\n'
    f'\nIf you want to change this selection, delete the file '
    f'"calendar_ids.json" and run again.\n'
)


# This function adjusts the dates to something that is easier to work with.
def adjust_datetime(user_date_input):
    date_matches = list(datefinder.find_dates(user_date_input))
    return date_matches[0], date_matches[0].strftime('%a')


# Sending the event to a google calendar
# in the format that google reference provides.
def create_calendar_event(event_start_time, summary, minutes_time=1,
                          hours_time=1, description=None):
    timezone = 'Europe/London'
    start_time = datetime.strptime(event_start_time, '%Y-%m-%dT%H:%M:%S')
    end_time = start_time + \
        timedelta(minutes=minutes_time, hours=(hours_time + 0.5))
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
        },
    }
    return service.events().insert(calendarId=work_cal_id,
                                   body=event).execute()


# 'duty_section' is the breakdown of the duties by 4 sections:
# Sunday, Monday to Thursday, Friday, and Saturday.
# This function takes all the variables that are needed to prepare the data
# for sending to the calendar
def setup_event(duty_section, duty_number, duty_date):
    date_fixed = duty_date.strftime('%d %b %Y')
    duty_list = duties[duty_section]
# This 'if' will enter a rest day.
    if duty_number == 'RD' or duty_number == '':
        date_fixed = duty_date.strftime('%d %b %Y')
        day = adjust_datetime(f'{date_fixed}')[1]
# The next line is a fix for a bug with rest days not showing on the phone app.
# For some reason, all day events can't end on the same day.
        next_day = duty_date + timedelta(days=1)
        event = {
            'summary': 'RD',
            'start': {
                'date': duty_date.strftime('%Y-%m-%d'),
            },
            'end': {
                'date': next_day.strftime('%Y-%m-%d'),
            },
        }
        service.events().insert(calendarId=rest_cal_id, body=event).execute()
        return print(f'Rest day entered into calendar on '
                     f'{day} {date_fixed}\n')
    else:  # This 'else' will enter a work duty.
        day = adjust_datetime(
            f'{date_fixed} {duty_list[duty_number]["start"]}'
            )[1]
        duty_date_time = adjust_datetime(
            f'{date_fixed} {duty_list[duty_number]["start"]}'
            )[0]
        duty_date_time = duty_date_time.strftime('%Y-%m-%dT%H:%M:%S')
        create_calendar_event(
            duty_date_time,
            duty_list[duty_number]['summary'],
            duty_list[duty_number]['length_minutes'],
            duty_list[duty_number]['length_hours'],
            duty_list[duty_number]['description']
            )
        return print(
            f'Duty {duty_number} entered into calendar on {day} {date_fixed}\n'
            )


# The next function takes the inputs by the user and loops through each day and
# then each week, adding duties and rest days.
def rota_input():
    # The next function deals with Rota entry. Rota entry is putting in the
    # duties and rest days for multiple weeks in one go.
    # This function checks which day of the week it is.
    def setup_rota_event(duty_number, date_event):
        day = adjust_datetime(str(date_event))[1]
        if duty_number == 'r':
            duty_number = 'RD'

        while True:
            if day == 'Sun' or day == 'Fri' or day == 'Sat':
                setup_event(day, duty_number, date_event)
                break

            else:
                setup_event('MonThur', duty_number, date_event)
                break

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
        if user_date_input[1] == 'Sun':
            while True:
                rota_number = int(
                    input('Enter starting rota number: (1 to 71) '))
                if rota_number < 1 or rota_number > 71:
                    print('Try again.')
                else:
                    break

            while True:
                number_of_weeks = int(
                    input('Number of weeks to enter into calendar: '))
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
# This loops through the number of weeks the user gave and then each day of
# the week.
            for i in range(number_of_weeks):
                for ii in range(7):
                    setup_rota_event(duties['Rota'][str(rota_number)]
                                     [str(ii + 1)], user_date)
                    user_date = user_date + timedelta(days=1)
                    ii += 1
                rota_number += 1
                i += 1
# There are 2 weeks of cover weeks that has no duties to enter,
# this skips them.
                if rota_number in [11, 25, 35, 45, 60]:
                    rota_number += 2
                    user_date = user_date + timedelta(days=14)
                    i += 2
# This skips 1 week if entry happens to start during the 2nd week
# of the cover weeks. Week 65 is a single cover week in the rota.
                elif rota_number in [12, 26, 36, 46, 61, 65]:
                    rota_number += 1
                    user_date = user_date + timedelta(days=7)
                    i += 1
# The final week in the duties is number 71. This loops back in the rota.
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


# This function has 2 arguments because it will also do the daily inputs.
# If it's a daily input it will get a 'True' in the first argument.
def weekly_input(daily_check=False, date_event=''):
    # This function is used for the daily and weekly inputs, to prepare
    # the data for the calendar.
    def setup_weekly_event(date_event):
        exact_day = adjust_datetime(str(date_event))[1]
        sun_range = range(int(duties['Ranges']['Sun'][0]),
                          int(duties['Ranges']['Sun'][1]))
        mon_thur_range = range(int(duties['Ranges']['MonThur'][0]),
                               int(duties['Ranges']['MonThur'][1]))
        fri_range = range(int(duties['Ranges']['Fri'][0]),
                          int(duties['Ranges']['Fri'][1]))
        sat_range = range(int(duties['Ranges']['Sat'][0]),
                          int(duties['Ranges']['Sat'][1]))

        def format_error_message():
            return print('Incorrect input. Please enter again.\n')

        # This will check if the duty range is correct.
        def section_range_check(exact_day, duty_section,
                                section_range, date_event):
            while True:
                user_input = str.upper(input(f'{exact_day}: '))
                if str.isdecimal(user_input):
                    duty_range = user_input
                if user_input == 'RD' or user_input == '':
                    setup_event(duty_section, user_input, date_event)
                    break
                elif int(duty_range) in section_range:
                    setup_event(duty_section, user_input, date_event)
                    break
                else:
                    format_error_message()
                    continue
        if exact_day == 'Sun':
            section_range_check(exact_day, exact_day, sun_range, date_event)

        elif exact_day == 'Fri':
            section_range_check(exact_day, exact_day, fri_range, date_event)

        elif exact_day == 'Sat':
            section_range_check(exact_day, exact_day, sat_range, date_event)

        else:
            section_range_check(exact_day, 'MonThur',
                                mon_thur_range, date_event)
    if daily_check:  # Checks it's a daily input and just does that one day.
        setup_weekly_event(date_event)
        return
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

        # Loops through a week to ask the user for duties or rest days for
        # each day of the week.
        user_date = user_date_input[0]
        if user_date_input[1] == 'Sun':
            print('\n### Enter duty number or leave blank for rest day. ###\n')
            for i in range(7):
                setup_weekly_event(user_date)
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


# Starts here and gives a menu that calls the appropriate functions.
def main():
    while True:
        start_selection = input('*************************'
                                '\n\n1 - Rota'
                                '\n2 - Weekly'
                                '\n3 - Daily'
                                '\n\n4 - Exit'
                                '\n\nSelect from 1 to 4: ')
        if start_selection == '1':
            rota_input()
            break
        elif start_selection == '2':
            weekly_input()
            break
        # The daily input code asks the user for info here and then calls the
        # 'weekly_input' function to add the duty to the calendar.
        elif start_selection == '3':
            print('\n*************************'
                  '\n\nDaily Input')
            while True:
                while True:
                    try:
                        user_date_input = adjust_datetime(
                            input(
                                '\nDate of duty or rest day (eg. 21 Jul 19): ')
                            )
                    except IndexError:
                        print('Date format is incorrect. Please enter again.')
                    else:
                        break

                date_fixed = user_date_input[0].strftime('%d %b %Y')
                print(f'\nEnter the duty number or RD for rest day'
                      f' for {date_fixed}.')
                weekly_input(True, user_date_input[0])
                user_continue = str.upper(
                    input('Add more duties to a different date? (y/n): '))
                if user_continue == 'Y':
                    continue
                else:
                    break
            break
        elif start_selection == '4':
            print('\nDuty entry done. Program ended.')
            quit()
        else:
            print('Please try again.')


if __name__ == '__main__':
    main()

if __name__ == '__main__':
    user_continue = str.upper(
        input('Do you want to see the main menu? (y/n): '))
    if user_continue == 'Y':
        main()
    print('\nDuty entry done. Program ended.')
