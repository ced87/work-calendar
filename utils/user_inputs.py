from utils import datetime_formatter


def main_menu_select():
    user_main_menu_selection = input('  Choose one of the following options:\n'
                                     '\n  1 - Rota\n'
                                     '(You choose the start week, where in the rota to start, '
                                     'and how many weeks to enter into the calendar.)'
                                     '\n\n  2 - Weekly\n'
                                     '(You Choose the start week, and enter a duty for each day of the week.)'
                                     '\n\n  3 - Daily\n'
                                     '(You choose a single day, and enter the duty for that day.)'
                                     '\n\n\n  4 - Change Calendars'
                                     '\n  5 - Exit'
                                     '\n\nSelect from 1 to 5: ')
    return user_main_menu_selection


def add_more_check():
    if str.upper(input('Add more? (y/n): ')) == 'Y':
        return True
    else:
        return False


def continue_check():
    if str.upper(input('(y/n): ')) == 'Y':
        return True
    else:
        return False


def sunday_input_check():
    day = ''
    while day != 'Sun':
        user_date_input = list(datetime_formatter.get_formatted_date(
            input('\nWeek commencing, must be a Sunday (eg. 21 Jul 19): ')))
        if not user_date_input:
            print('Date format is incorrect. Please enter again.')
            continue

        day = user_date_input[0].strftime('%a')
        if day != 'Sun':
            print(
                f'The date {user_date_input[0].strftime("%d %b %Y")} is not a Sunday.'
                ' Please enter again.')

    return user_date_input[0]


def rota_week_input(last_duties_week):
    while True:
        rota_week_number = int(input(f'Enter starting rota number: (1 to {last_duties_week}) '))
        if rota_week_number < 1 or rota_week_number > int(last_duties_week):
            print('Try again.')
        else:
            break
    return rota_week_number


def rota_number_of_weeks():
    while True:
        number_of_weeks = int(
            input('Number of weeks to enter into calendar: '))
        if number_of_weeks > 5:
            if str.upper(input(f'Number of weeks entered is {number_of_weeks}, are you sure? (y/n): ')) == 'Y':
                break
            else:
                print('\nEnter again.\n')
                continue
        else:
            break
    return number_of_weeks


def day_of_week_user_input(day_of_week):
    duty_number = input(f'{day_of_week}: ')
    return duty_number


def daily_date_duty_input():
    while True:
        user_date_input = list(
            datetime_formatter.get_formatted_date(input('\nDate of duty or rest day (eg. 21 Jul 19): ')))
        if not user_date_input:
            print('Date format is incorrect. Please enter again.')
            continue
        else:
            break
    print(f'\nEnter the duty number or RD for rest day'
          f' for {user_date_input[0].strftime("%A %d %b %Y")}.')
    return user_date_input[0]
