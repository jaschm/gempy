import csv
import json

def write_to_csv(data, output_file):
    with open('aineiston_kasittely/config_files/config.json', 'r') as cfg_file:
        config = json.load(cfg_file)
    column_names = config["column_names"]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)
