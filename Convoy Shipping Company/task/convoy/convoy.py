import pandas as pd
import csv


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


def correct_and_write_file():
    file_name = input("Input file name\n")

    if file_name[-3:] != "csv":
        file_name = convert_to_csv(file_name)

    checked_file_name = file_name.replace(".csv", "[CHECKED].csv")

    with open(checked_file_name, "w") as checked_file:
        file_writer = csv.writer(checked_file, delimiter=",", lineterminator="\n")

        with open(file_name, "r") as unchecked_file:
            line_count = 0
            corrections = 0

            for line in unchecked_file:
                line = line.replace("\n", "").split(",")

                if line_count > 0:
                    for c in line:
                        correction_in_line = False
                        corrected_c = ""
                        for l in c:
                            if not l.isdigit():
                                correction_in_line = True
                            else:
                                corrected_c += l

                        file_writer.writerow([corrected_c])

                        if correction_in_line:
                            corrections += 1

                line_count += 1

        if corrections == 1:
            print(f"1 cell was corrected in {checked_file_name}")
        else:
            print(f"{corrections} cells were corrected in {checked_file_name}")


correct_and_write_file()
