import json
import re

def parse_input(input_file):
    data = []
    with open('aineiston_kasittely/config_files/config.json', 'r') as cfg_file:
        config = json.load(cfg_file)
    entry = config["entry"]
    start_keys = tuple(config["start_keys"])
    line_keys = config["line_keys"]
    alias_map = config.get("alias_map", {})

    numeric_pattern = re.compile(r"\b\d+\.\d{2}\b")

    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            if line and ' ' in line:
                if line.startswith(start_keys):
                    key, value = line.split(maxsplit=1)
                    entry[key] = value

                elif line.startswith("XY"):
                    parts = line.split()
                    entry['X'], entry['Y'], entry['Z'], entry['pvm'], entry['nro'] = parts[1:]

                elif line.startswith('-1'):
                    if entry['Paattymissyvyys'] == '':
                        numeric_value = re.findall(numeric_pattern, last_line)
                        if numeric_value:
                            entry['Paattymissyvyys'] = numeric_value[0]

                    data.append(entry.copy())
                    with open('aineiston_kasittely/config_files/config.json', 'r') as cfg_file2:
                        config = json.load(cfg_file2)
                        entry = config["entry"]

                elif any(col in line for col in line_keys):
                    parts = line.split()
                    if len(parts) >= 2:
                        raw_name = parts[-1].strip().capitalize()

                        if raw_name in alias_map:
                            raw_name = alias_map[raw_name]

                        column_name = raw_name.capitalize()
                        if column_name in entry:
                            if isinstance(entry[column_name], list):
                                entry[column_name].append(parts[0])
                            else:
                                entry[column_name] = [entry[column_name], parts[0]]
                        elif column_name == 'Paattymissyvyys':
                            numeric_value = re.findall(numeric_pattern, line)
                            if numeric_value:
                                entry[column_name] = numeric_value[0]

            last_line = line

    return data
