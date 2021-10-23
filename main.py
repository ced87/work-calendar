import json
from utils import google_login, calendar_init, event_setup, user_inputs


def main():
    service = google_login.google_login()
    calendar_list = service.calendarList().list().execute()

    print('\n  This program will enter West Ruislip work duties and rest days into your Google Calendar.')

    duties_rota_range_dict = json.load(open('./duties.json', 'r'))

    calendar_init.calendar_selector(calendar_list, service)
    calendar_ids = json.load(open('./calendar_ids.json', 'r'))

    while True:
        user_main_menu_selection = user_inputs.main_menu_select()

        if user_main_menu_selection == '1':
            event_setup.rota_setup(duties_rota_range_dict, service, calendar_ids)
        elif user_main_menu_selection == '2':
            event_setup.week_setup(duties_rota_range_dict, service, calendar_ids)
        elif user_main_menu_selection == '3':
            event_setup.day_setup(duties_rota_range_dict, service, calendar_ids)
        elif user_main_menu_selection == '4':
            calendar_init.delete_calendar_selection()
            calendar_init.calendar_selector(calendar_list, service)
        elif user_main_menu_selection == '5':
            break
        else:
            print('Please try again.')

        if str.upper(input('Do you want to see the main menu? (y/n): ')) == 'Y':
            continue
        else:
            break

    print('\nDuty entry done. Program ended.\n')


if __name__ == '__main__':
    main()
