import PyPDF2
import pickle

# this is the function that will add the duties into a dictionary
# and save it to a .pkl file.
def duty_entry(duty_num, day_code, hours, minutes, file):
    pickle_open = open(f'{file}.pkl', 'rb')
    duty_day = pickle.load(pickle_open)
    duty_day[duty_num] = {'summary': f'{duty_num}{day_code} - {hours}:{minutes}',
                             'start': start_time,
                             'length_minutes': int(minutes),
                             'length_hours': int(hours),
                             'description': '',
                          }
    print(f"\n***DUTY {duty_num} ADDED***\n{duty_day[duty_num]}")
    pickle_dump = open(f'{file}.pkl', 'wb')
    pickle.dump(duty_day, pickle_dump)
    pickle_dump.close()


# open my work pdf that contains all my duties
with open('work.pdf', 'rb') as pdf_file:
    for i in range(146):
        if i in range(120, 146):
            file_name = 'duty_sun'
            dic_code = 'Su'
        elif i in range(8, 48):
            file_name = 'duty_mon_thur'
            dic_code = 'MT'
        elif i in range(49, 88):
            file_name = 'duty_fri'
            dic_code = 'F'
        elif i in range(89, 119):
            file_name = 'duty_sat'
            dic_code = 'Sa'
        else:
            continue

        # extract the info on each page into a temporary .txt file then
        # run it through the duty_entry() function
        page_content = PyPDF2.PdfFileReader(pdf_file).getPage(i).extractText()
        with open('temp.txt', 'w') as temp_text_file:
            temp_text_file.write(page_content)
        with open('temp.txt', 'r') as temp_file:
            for line in temp_file:
                line = line.rstrip()
                if line.startswith('Length'):
                    data = line.strip('Length ')
                    a, b, c, d, e = data
                    length_hours = a + b
                    length_minutes = d + e

                if line.startswith('On'):
                    data = line.strip('On ')
                    a, b, c, d, e = data
                    start_time = a + b + d + e

                if line.startswith('9'):
                    duty_number = line

            duty_entry(duty_number, dic_code, length_hours, length_minutes, file_name)


# similar to above but these are the spare duties, different formatting. I had to improvise.
with open('work.txt', 'r') as spares_file:
    length_hours = '08'
    length_minutes = '00'

    for line in spares_file:
        line = line.rstrip()
        if line.startswith('mt'):
            data = line.strip('mt')
            a, b, c, d, e, f, g = data
            duty_number = a + b + c
            start_time = d + e + f + g
            dic_code = 'MT Spare'
            file_name = 'duty_mon_thur'
            duty_entry(duty_number, dic_code, length_hours, length_minutes, file_name)
        elif line.startswith('fr'):
            data = line.strip('fr')
            a, b, c, d, e, f, g = data
            duty_number = a + b + c
            start_time = d + e + f + g
            dic_code = 'F Spare'
            file_name = 'duty_fri'
            duty_entry(duty_number, dic_code, length_hours, length_minutes, file_name)
        elif line.startswith('sa'):
            data = line.strip('sa')
            a, b, c, d, e, f, g = data
            duty_number = a + b + c
            start_time = d + e + f + g
            dic_code = 'Sa Spare'
            file_name = 'duty_sat'
            duty_entry(duty_number, dic_code, length_hours, length_minutes, file_name)
        elif line.startswith('su'):
            data = line.strip('su')
            a, b, c, d, e, f, g = data
            duty_number = a + b + c
            start_time = d + e + f + g
            dic_code = 'Su Spare'
            file_name = 'duty_sun'
            duty_entry(duty_number, dic_code, length_hours, length_minutes, file_name)
        else:
            continue
