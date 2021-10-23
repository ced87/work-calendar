import os
import json


def calendar_selector(calendar_list, service):
    if os.path.exists('./calendar_ids.json'):
        duties_cal_selection = json.load(
            open('./calendar_ids.json', 'r'))['duties_calendar_id']
        restday_cal_selection = json.load(
            open('./calendar_ids.json', 'r'))['restday_calendar_id']
    else:
        x = 1
        print(
            '\nPlease select which calendars to add duties and rest days to: ')
        for calendars in calendar_list['items']:
            print(f'{x} - {calendars["summary"]}')
            x += 1

        while True:
            try:
                duties_cal_selection = int(
                    input('\nEnter the number of the Google calendar to use'
                          ' for work duties: '))
            except IndexError:
                print('Enter a valid calendar number. Please enter again.')
            else:
                duties_cal_selection = calendar_list['items'][duties_cal_selection - 1]['id']
                break
        while True:
            try:
                restday_cal_selection = int(
                    input('Enter the number of the Google calendar to use for \
rest days (can be the same as the duties calendar): '))
            except Exception:
                print('Enter a valid calendar number. Please enter again.')
            else:
                restday_cal_selection = calendar_list['items'][restday_cal_selection - 1]['id']
                json.dump(
                    {'duties_calendar_id': duties_cal_selection,
                     'restday_calendar_id': restday_cal_selection},
                    open('./calendar_ids.json', 'w'))
                break

    print(
        f'\nWork calendar selected: ------- \
{service.calendars().get(calendarId=duties_cal_selection).execute()["summary"]}'
        f'\nRest day calendar selected: --- \
{service.calendars().get(calendarId=restday_cal_selection).execute()["summary"]}\n')

    return {'duties_calendar_id': duties_cal_selection, 'restday_calendar_id': restday_cal_selection}


def delete_calendar_selection():
    while True:
        try:
            if str.upper(input('Are you sure you want to change calendar selection? (y/n): ')) == 'Y':
                os.remove('./calendar_ids.json')
                break
            else:
                break
        except FileNotFoundError:
            print('File not found, please continue.')
            break
