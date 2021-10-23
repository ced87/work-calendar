from datetime import timedelta
from utils import user_inputs, create_event


def duty_range_check(duties_rota_range_dict, day_of_week, user_date_input):
    if day_of_week == 'Sun':
        section_range = range(int(duties_rota_range_dict['Ranges']['Sun'][0]),
                              int(duties_rota_range_dict['Ranges']['Sun'][1]))
    elif day_of_week == 'Fri':
        section_range = range(int(duties_rota_range_dict['Ranges']['Fri'][0]),
                              int(duties_rota_range_dict['Ranges']['Fri'][1]))
    elif day_of_week == 'Sat':
        section_range = range(int(duties_rota_range_dict['Ranges']['Sat'][0]),
                              int(duties_rota_range_dict['Ranges']['Sat'][1]))
    else:
        section_range = range(int(duties_rota_range_dict['Ranges']['MonThur'][0]),
                              int(duties_rota_range_dict['Ranges']['MonThur'][1]))

    while True:
        user_duty_number_input = str.upper(user_inputs.day_of_week_user_input(day_of_week))
        if user_duty_number_input.lstrip("-").isdecimal():
            user_duty_input_int = user_duty_number_input

        if user_duty_number_input == 'RD' or user_duty_number_input == '':
            return {'duty_number': 'RD', 'duty_date': user_date_input}
        elif int(user_duty_input_int) in section_range:
            return {'duty_number': user_duty_input_int, 'duty_date': user_date_input}
        else:
            print('Out of duty range or incorrect format. Please enter again.\n')
            continue


def rota_setup(duties_rota_range_dict, service, calendar_ids):
    last_duties_week = max(duties_rota_range_dict['Rota'], key=int)
    print('\n**************'
          '\n  Rota Input\n'
          '**************', end='')
    while True:
        user_date_input = user_inputs.sunday_input_check()

        rota_week_number = user_inputs.rota_week_input(last_duties_week)
        number_of_weeks = user_inputs.rota_number_of_weeks()

        for week_number in range(number_of_weeks):
            if rota_week_number in [11, 25, 35, 45, 60]:
                rota_week_number += 2
                user_date_input = user_date_input + timedelta(days=14)
                week_number += 2

            elif rota_week_number in [12, 26, 36, 46, 61, 65]:
                rota_week_number += 1
                user_date_input = user_date_input + timedelta(days=7)
                week_number += 1

            elif rota_week_number == int(last_duties_week) + 1:
                rota_week_number = 1

            for day_of_week in range(7):
                duty_number = duties_rota_range_dict['Rota'][str(rota_week_number)][str(day_of_week + 1)]
                create_event.create_calendar_event(duties_rota_range_dict,
                                                   service,
                                                   calendar_ids,
                                                   duty_number,
                                                   user_date_input)
                user_date_input = user_date_input + timedelta(days=1)
                day_of_week += 1
            rota_week_number += 1
            week_number += 1

        if user_inputs.add_more_check() is not True:
            break

    return print('\nRota entry done.\n')


def week_setup(duties_rota_range_dict, service, calendar_ids):
    print('\n****************'
          '\n  Weekly Input\n'
          '****************', end='')

    while True:
        user_date_input = user_inputs.sunday_input_check()
        week_data = {}

        for day in range(7):
            day_of_week = user_date_input.strftime('%a')
            week_data[day_of_week] = duty_range_check(duties_rota_range_dict, day_of_week, user_date_input)
            user_date_input = user_date_input + timedelta(days=1)
            day += 1

        print(f'\nDuties entered for week commencing {(user_date_input - timedelta(days=7)).strftime("%A %d %b %Y")}:')

        for day_of_week, duty_and_date in week_data.items():
            print(f'{day_of_week}: {duty_and_date["duty_number"]}')

        print('\nIs this correct? ', end='')
        if user_inputs.continue_check():
            for day_of_week, duty_and_date in week_data.items():
                create_event.create_calendar_event(duties_rota_range_dict,
                                                   service,
                                                   calendar_ids,
                                                   duty_and_date['duty_number'],
                                                   duty_and_date['duty_date'])
            if user_inputs.add_more_check() is not True:
                break
        else:
            print('\nPlease start again.')
            continue

    return print('\nWeekly entry done.\n')


def day_setup(duties_rota_range_dict, service, calendar_ids):
    print('\n***************'
          '\n  Daily Input\n'
          '***************', end='')
    while True:
        duty_and_date = {}
        user_date_input = user_inputs.daily_date_duty_input()
        day_of_week = user_date_input.strftime('%a')
        duty_and_date = duty_range_check(duties_rota_range_dict, day_of_week, user_date_input)

        create_event.create_calendar_event(duties_rota_range_dict,
                                           service,
                                           calendar_ids,
                                           duty_and_date['duty_number'],
                                           duty_and_date['duty_date'])

        if user_inputs.add_more_check() is not True:
            break

    return print('\nDaily entry done.\n')
