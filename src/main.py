import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import rasterio

from data_processing.parse_input import parse_input
from data_processing.write_to_csv import write_to_csv
from data_processing.filter_rows import filter_rows
from data_processing.clean_nro import clean_nro
from utils.choose_input_file import choose_input_file
from utils.read_filtered_data import read_filtered_data
from utils.create_orientation_file import create_orientation_file


def main():
    input_directory = "aineiston_kasittely/input_data"
    input_file = choose_input_file(input_directory)
    if input_file:
        print(f"Selected file: {input_file}")
        output_file = "aineiston_kasittely/output_data/output_tek_to_csv.csv"
        data = parse_input(input_file)
        write_to_csv(data, output_file)
        
        # Create output_from_table.csv
        with open(output_file, mode='r', newline='', encoding='utf-8') as infile, \
             open('aineiston_kasittely/output_data/output_from_table.csv', mode='w', newline='', encoding='utf-8') as outfile:

            with open('aineiston_kasittely/input_data/config.json', 'r') as cfg_file:
                config = json.load(cfg_file)
            fieldnames = config["fieldnames"]

            reader = csv.DictReader(infile)
            new_rows = []

            for row in reader:
                if row.get("TT") == "PO - 0":
                    continue

                for col_name, cell_value in row.items():
                    if '[' in cell_value:
                        cell_list = eval(cell_value)
                        for item in cell_list:
                            new_row = {'maalaji': col_name, 'value': item}
                            for key in fieldnames[2:-1]:
                                new_row[key] = row[key]
                            try:
                                z_value = float(row['Z'])
                                item_value = float(item)
                                new_row['korko'] = z_value - item_value
                            except ValueError:
                                new_row['korko'] = ''
                            new_rows.append(new_row)

            sorted_rows = sorted(
                new_rows,
                key=lambda x: (
                    float(x['X']),
                    -float(x['korko']) if isinstance(x['korko'], (float, int))
                    else (-float(x['korko']) if isinstance(x['korko'], str) and x['korko'].replace('.', '', 1).isdigit() else float('-inf')),
                )
            )
            sorted_rows2 = sorted(
                sorted_rows,
                key=lambda x: (clean_nro(x['nro']) if 'nro' in x else '')
            )

            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_rows2)

        filename = 'aineiston_kasittely/output_data/output_from_table.csv'
        filtered_data = filter_rows(filename)

        table = PrettyTable()
        table.field_names = ['piste', 'X', 'Y', 'Z', 'formation']

        output_csv = r'aineiston_kasittely/output_data/filtered_output.csv'

        with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
            with open('aineiston_kasittely/input_data/config.json', 'r') as cfg_file:
                config = json.load(cfg_file)
            header_row = config["header_row"]
            writer = csv.writer(csvfile)
            writer.writerow(header_row)
            print(f"Filtered data: {filtered_data}")
            for row in filtered_data:
                if len(row) == 7:  # Adjusted to match the actual length of the rows
                    try:
                        korko_rounded = round(float(row[6]), 3) if row[6] else ''
                    except ValueError:
                        korko_rounded = ''
                    writer.writerow([row[5], row[3], row[2], korko_rounded, row[0]])
                    table.add_row([row[5], row[3], row[2], korko_rounded, row[0]])

        print(table)

        filtered_df = pd.read_csv('aineiston_kasittely/output_data/filtered_output.csv')
        print(filtered_df)

        # Offset per formation
        offset_map = {
            'Sa': 0,  
            'Mr': 0,
            'Sr': 0,  
            'Hk': 0,
            'Si': 0,
        }

        def get_offset(formation):
            return offset_map.get(formation, 0)

        df = pd.read_csv('aineiston_kasittely/output_data/filtered_output.csv')

        for i, row in df.iterrows():
            formation = row['formation']
            df.at[i, 'Z'] = row['Z'] + get_offset(formation)

        df.to_csv('aineiston_kasittely/output_data/offset_data.csv', index=False)
        print("\nOffset applied to formations. 'offset_data.csv' created.\n")

        offset_points = read_filtered_data('aineiston_kasittely/output_data/offset_data.csv')
        orientation_file = 'aineiston_kasittely/output_data/orientation_offset.csv'
        create_orientation_file(offset_points, orientation_file)
        print(f"Orientation file created: {orientation_file}")

        df_offset = pd.read_csv('aineiston_kasittely/output_data/offset_data.csv')
        df_offset = df_offset.dropna(subset=['Z'])
        df_offset.to_csv('aineiston_kasittely/output_data/offset_data.csv', index=False)

        x_min, x_max = df_offset['X'].min(), df_offset['X'].max()
        y_min, y_max = df_offset['Y'].min(), df_offset['Y'].max()
        z_min_points, z_max_points = df_offset['Z'].min(), df_offset['Z'].max()  # Z range from points data
        print(f"X range: {x_min} to {x_max}")
        print(f"Y range: {y_min} to {y_max}")

        # Ensure coordinates are numeric
        x_min, x_max = float(x_min), float(x_max)
        y_min, y_max = float(y_min), float(y_max)
        z_min_points, z_max_points = float(z_min_points), float(z_max_points)

        # Read Z range from TIFF file
        with rasterio.open('aineiston_kasittely/input_data/dtm_8.3.2025_2.tif') as dataset:
            band1 = dataset.read(1)
            nodata = dataset.nodata
            valid_data = band1[band1 != nodata]
            z_min_dtm = valid_data.min()
            z_max_dtm = valid_data.max()
            print(f"Z range from TIFF: {z_min_dtm} to {z_max_dtm}")

            # Ensure crop_to_extent values are within the valid range of the raster dataset
            x_min = max(x_min, dataset.bounds.left)
            x_max = min(x_max, dataset.bounds.right)
            y_min = max(y_min, dataset.bounds.bottom)
            y_max = min(y_max, dataset.bounds.top)

            # Debug print to inspect the adjusted extent values
            print(f"Adjusted crop to extent: [{x_min}, {x_max}, {y_min}, {y_max}]")

        # Determine final Z range, ensuring nodata values are not included
        z_min = min(z_min_points, z_min_dtm)
        z_max = max(z_max_points, z_max_dtm)

        print(f"X range: {x_min} to {x_max}")
        print(f"Y range: {y_min} to {y_max}")
        print(f"Z range: {z_min} to {z_max}")

        return x_min, x_max, y_min, y_max, z_min, z_max


if __name__ == "__main__":
    main()