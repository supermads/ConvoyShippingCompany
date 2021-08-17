import pandas as pd
import csv
import sqlite3
import json
from collections import OrderedDict
from dicttoxml import dicttoxml


def convert_to_csv(file_name):
    vehicle_df = pd.read_excel(file_name, sheet_name="Vehicles", dtype=str)

    csv_file_name = file_name[0:-4] + "csv"

    vehicle_df.to_csv(csv_file_name, index=None, header=True)

    df_size = vehicle_df.shape[0]

    if df_size == 1:
        print(f"1 line was added to {csv_file_name}")
    else:
        print(f"{df_size} lines were added to {csv_file_name}")

    return csv_file_name


def correct_and_write_csv(file_name):
    if file_name[-3:] != "csv":
        file_name = convert_to_csv(file_name)

    checked_file_name = file_name.replace(".csv", "[CHECKED].csv")

    with open(checked_file_name, "w") as checked_file:
        file_writer = csv.writer(checked_file, delimiter=",", lineterminator="\n")

        with open(file_name, "r") as unchecked_file:
            line_count = 0
            corrections = 0
            column_names = []

            for line in unchecked_file:
                line = line.replace("\n", "").split(",")
                corrected_row = []

                if line_count > 0:
                    for c in line:
                        correction_in_line = False
                        corrected_c = ""
                        for l in c:
                            if not l.isdigit():
                                correction_in_line = True
                            else:
                                corrected_c += l
                        corrected_row.append(corrected_c)

                        if correction_in_line:
                            corrections += 1

                    file_writer.writerow(corrected_row)

                else:
                    for c in line:
                        column_names.append(c)
                    file_writer.writerow(column_names)

                line_count += 1

        if corrections == 1:
            print(f"1 cell was corrected in {checked_file_name}")
        else:
            print(f"{corrections} cells were corrected in {checked_file_name}")

    return checked_file_name, column_names


def calc_score(row):
        score = 0

    # Fuel needed = liters of fuel_consumption per hundred km multiplied by 450 km trip length
        fuel_needed = 450 * row[3] / 100
        if fuel_needed <= row[2]:
            score += 2
        elif fuel_needed <= row[2] * 2:
            score += 1

        if fuel_needed <= 230:
            score += 2
        else:
            score += 1

        if row[4] >= 20:
            score += 2

        return score


def create_database(file_name, column_names):
    db_name = file_name[:-13] + ".s3db"

    df = pd.read_csv(file_name)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    create_command = """CREATE TABLE IF NOT EXISTS convoy ("""

    column_names.append("score")

    for name in column_names:
        if name == "vehicle_id":
            create_command += f"{name} INT PRIMARY KEY, "
        else:
            create_command += f"{name} INT NOT NULL, "

    create_command = create_command[0:-2] + ");"

    cursor.execute(create_command)

    entries_added = 0

    for row in df.itertuples():
        score = calc_score(row)
        cursor.execute("""
            INSERT INTO convoy 
            VALUES (?,?,?,?,?)
            """,
            (row[1],
            row[2],
            row[3],
            row[4],
            score)
            )

        entries_added += 1

    conn.commit()
    conn.close()

    if entries_added == 1:
        print(f"1 record was inserted into {db_name}")
    else:
        print(f"{entries_added} records were inserted into {db_name}")

    return db_name


def convert_to_json(file_name):
    json_file = file_name.replace(".s3db", ".json")
    conn = sqlite3.connect(file_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM convoy")
    rows = cursor.fetchall()

    json_vehicle_list = []
    xml_vehicle_list = []
    for row in rows:
        d = OrderedDict()
        d["vehicle_id"] = row[0]
        d["engine_capacity"] = row[1]
        d["fuel_consumption"] = row[2]
        d["maximum_load"] = row[3]
        if row[4] > 3:
            json_vehicle_list.append(d)
        else:
            xml_vehicle_list.append(d)

    json_vehicles = len(json_vehicle_list)
    if json_vehicles == 1:
        print(f"1 vehicle was saved into {json_file}")
    else:
        print(f"{json_vehicles} vehicles were saved into {json_file}")

    table_dict = {"convoy": json_vehicle_list}
    j = json.dumps(table_dict)

    with open(json_file, "w") as f:
        f.write(j)

    conn.close()

    return json_file, xml_vehicle_list


def convert_to_xml(file_name, vehicle_list):
    xml_file = file_name.replace(".json", ".xml")
    vehicles = len(vehicle_list)

    xml = dicttoxml({"convoy": vehicle_list}, attr_type=False, root=False, item_func=lambda x: "vehicle")

    with open(xml_file, "w") as f:
        f.write(xml.decode("utf-8"))

    if vehicles == 1:
        print(f"1 vehicle was saved into {xml_file}")
    else:
        print(f"{vehicles} vehicles were saved into {xml_file}")


def main():
    file_name = input("Input file name\n")

    if file_name[-13:] == "[CHECKED].csv":
        with open(file_name, "r") as f:
            column_names = f.readlines()[0].replace("\n", "").split(",")
        file_name = create_database(file_name, column_names)

    elif file_name[-4:] != 's3db':
        file_name, column_names = correct_and_write_csv(file_name)
        file_name = create_database(file_name, column_names)

    file_name, xml_vehicles = convert_to_json(file_name)
    convert_to_xml(file_name, xml_vehicles)


main()
