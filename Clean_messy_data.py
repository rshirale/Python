import pandas as pd
import re
import csv
import sqlite3
import json
import dicttoxml
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET

regex_csv = r'.+\.csv'
regex_xlsx = r'.+\.xlsx'
regex_checked_csv = r'.+\[CHECKED].csv'
regex_s3db = r'.+\.s3db'
original_input = ""


def to_json(sql_file):
    new_filename = sql_file.replace(".s3db", ".json")
    xml_filename = new_filename.replace(".json", ".xml")
    mydict = {}
    _list = []

    conn = sqlite3.connect(sql_file)

    cur = conn.cursor()
    cur.execute('SELECT * FROM convoy')
    field_names = [i[0] for i in cur.description]
    rows = cur.fetchall()
    conn.commit()

    for i in range(len(rows)):
        temp = rows[i]
        for value, key in enumerate(field_names):
            mydict[key] = temp[value]
            if value == len(field_names) - 1:
                _list.append(mydict.copy())

    # print(_list)
    s3db_dict = {"convoy": _list}
    # print(s3db_dict)

    with open(new_filename, "w") as json_file:
        json.dump(s3db_dict, json_file, indent=4)

    with open(new_filename, "r") as json_file:
        py_dict = json.load(json_file)
        my_item_func = lambda x: 'vehicle'
        xml = dicttoxml.dicttoxml(py_dict, attr_type=False, root=False, item_func=my_item_func)
        dom = parseString(xml)
    
    for p_id, p_info in py_dict.items():
        count = 0
        for key in p_info:
            count += 1

    with open(xml_filename, "w") as outfile:
        outfile.write(dom.toprettyxml(indent=' ' * 4))

    if count <= 1:
        print(f'{count} vehicle was saved into {new_filename}')
        print(f'{count} vehicle was saved into {xml_filename}')
    else:
        print(f'{count} vehicles were saved into {new_filename}')
        print(f'{count} vehicles were saved into {xml_filename}')


def read_and_convert():
    global original_input

    while True:
        try:
            print("Input file name: ")
            filename = input()
            original_input = filename
            if re.match(regex_xlsx, filename):

                '''   XLSX to CSV   '''
                df = pd.read_excel(filename, sheet_name="Vehicles", dtype=str)
                filename = filename.replace(".xlsx", ".csv")
                df.to_csv(filename, index=None, header=True)
                if df.shape[0] == 1:
                    print(f'{df.shape[0]} line was added to {filename}')
                else:
                    print(f'{df.shape[0]} lines were added to {filename}')
                return filename

            elif re.match(regex_csv, filename):
                return filename

            elif re.match(regex_checked_csv, filename):
                return filename

            elif re.match(regex_s3db, filename):
                # print(filename)
                to_json(filename)
                exit()

        except ValueError:
            print("Oops!  That was no valid number.  Try again...")


def read_csv(file):
    new_file = []
    with open(file, newline='') as csv_file:
        file_reader = csv.reader(csv_file, delimiter=",")  # Create a reader object

        counter = 0
        for count, line in enumerate(file_reader):  # Read each line
            if count == 0:
                new_file.append(line)
            else:
                for item in line:  # Read each item in the line

                    if not item.isnumeric():
                        counter += 1
                        index = line.index(item)
                        replace = ''.join(filter(str.isdigit, item))
                        line[index] = replace
                new_file.append(line)
    return new_file, counter


def write_new_csv(_list, filename, cells):
    if re.match(regex_checked_csv, filename):
        new_filename = filename
        return new_filename
    else:
        new_filename = filename.replace(".csv", "[CHECKED].csv")
        with open(new_filename, "w") as w_file:
            file_writer = csv.writer(w_file, delimiter=",", lineterminator="\n")
            for line in _list:
                file_writer.writerow(line)
        if cells == 1:
            print(f'{cells} cell was corrected in {new_filename}')
        else:
            print(f'{cells} cells were corrected in {new_filename}')
        return new_filename


def create_sql_table(csv_filename):
    global original_input
    # print("Original Input:", original_input)

    if re.match(regex_checked_csv, original_input):
        new_filename = original_input.replace("[CHECKED].csv", ".s3db")
    else:
        new_filename = csv_filename.replace(".csv", ".s3db")

    conn = sqlite3.connect(new_filename)  # Open a database file
    # create a Cursor object and call its execute() method to perform SQL queries:
    cur = conn.cursor()
    # Executes some SQL query
    cur.execute('''CREATE TABLE IF NOT EXISTS convoy (
                vehicle_id INTEGER PRIMARY KEY,
                engine_capacity INTEGER NOT NULL,
                fuel_consumption INTEGER NOT NULL,
                maximum_load INTEGER NOT NULL);
                ''')

    # After doing some changes in DB don't forget to commit them!
    conn.commit()
    return new_filename


def insert_data_in_sql(checked_csv_file, sql_file):
    conn = sqlite3.connect(sql_file)
    cur = conn.cursor()
    with open(checked_csv_file, newline='') as csv_file:
        file_reader = csv.reader(csv_file, delimiter=",")  # Create a reader object

        for count, line in enumerate(file_reader):
            if count != 0:
                # print(line)
                sqlite_insert_with_param = """INSERT INTO convoy
                                           (vehicle_id, engine_capacity, fuel_consumption,
                                           maximum_load) 
                                           VALUES (?, ?, ?, ?);"""
                data_tuple = (line[0], line[1], line[2], line[3])
                cur.execute(sqlite_insert_with_param, data_tuple)

    conn.commit()
    cur.execute('SELECT * FROM convoy')
    results = cur.fetchall()
    if len(results) <= 1:
        print(f'{len(results)} record was inserted into {sql_file}')
    else:
        print(f'{len(results)} records were inserted into {sql_file}')


csv_file = read_and_convert()
mistakes_corrected_list, cells = read_csv(csv_file)
checked_csv_filename = write_new_csv(mistakes_corrected_list, csv_file, cells)
sql_filename = create_sql_table(csv_file)
insert_data_in_sql(checked_csv_filename, sql_filename)
to_json(sql_filename)