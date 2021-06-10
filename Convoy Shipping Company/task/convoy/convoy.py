import pandas as pd


def import_to_file():
    file_name = input("Input file name\n")

    vehicle_df = pd.read_excel(file_name, sheet_name="Vehicles", dtype=str)

    csv_file_name = file_name[0:-4] + "csv"
    vehicle_df.to_csv(csv_file_name, index=None, header=True)

    df_size = vehicle_df.shape[0]

    if df_size == 1:
        print(f"1 line was added to {csv_file_name}")

    else:
        print(f"{df_size} lines were added to {csv_file_name}")


import_to_file()
