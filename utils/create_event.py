from datetime import timedelta
from utils import datetime_formatter


def create_calendar_event(duties_rota_range_dict, service, calendar_ids, duty_number, start_time):
    day = start_time.strftime('%a')

    if duty_number == 'r' or duty_number == 'RD':
        event = {
            'summary': 'RD',
            'start': {
                'date': start_time.strftime('%Y-%m-%d'),
            },
            'end': {
                'date': (start_time + timedelta(days=1)).strftime('%Y-%m-%d'),
            },
        }
        service.events().insert(calendarId=calendar_ids['restday_calendar_id'], body=event).execute()
        return print(f'Rest day entered into calendar on {start_time.strftime("%a %d %b %Y")}.')

    else:

        if day == 'Sun' or day == 'Fri' or day == 'Sat':
            start_time = datetime_formatter.get_formatted_date(
                f'{start_time.strftime("%d %b %Y")} {duties_rota_range_dict[day][duty_number]["start"]}')[0]
            event_data = {
                'summary': duties_rota_range_dict[day][duty_number]['summary'],
                'length_minutes': duties_rota_range_dict[day][duty_number]['length_minutes'],
                'length_hours': duties_rota_range_dict[day][duty_number]['length_hours'],
                'description': duties_rota_range_dict[day][duty_number]['description'],
                'start_time': start_time
            }
        else:
            start_time = datetime_formatter.get_formatted_date(
                f'{start_time.strftime("%d %b %Y")} {duties_rota_range_dict["MonThur"][duty_number]["start"]}')[0]
            event_data = {
                'summary': duties_rota_range_dict['MonThur'][duty_number]['summary'],
                'length_minutes': duties_rota_range_dict['MonThur'][duty_number]['length_minutes'],
                'length_hours': duties_rota_range_dict['MonThur'][duty_number]['length_hours'],
                'description': duties_rota_range_dict['MonThur'][duty_number]['description'],
                'start_time': start_time
            }

        timezone = 'Europe/London'
        start_time = event_data['start_time']
        end_time = start_time + timedelta(minutes=event_data['length_minutes'],
                                          hours=(event_data['length_hours'] + 0.5))
        event = {
            'summary': event_data['summary'],
            'description': event_data['description'],
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

        service.events().insert(calendarId=calendar_ids['duties_calendar_id'], body=event).execute()
        return print(f'Duty {duty_number} entered into calendar on {start_time.strftime("%a %d %b %Y")}.')
