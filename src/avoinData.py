import requests
import csv
import os

main_business_line = "Teiden ja moottoriteiden rakentaminen"
url = f"https://avoindata.prh.fi/opendata-ytj-api/v3/companies?mainBusinessLine={main_business_line}"

try:
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    data = response.json()

    # Debug print to inspect the response data
    print("Response data:", data)

    if "results" in data and len(data["results"]) > 0:
        print("Results found, writing to CSV...")
        with open('company_names.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Company Name'])  # Write header

            for company in data["results"]:
                company_name = company["name"]
                writer.writerow([company_name])  # Write company name to CSV
                print(f"Written to CSV: {company_name}")
        
        print("CSV file 'company_names.csv' created successfully.")
        print(f"CSV file location: {os.path.abspath('company_names.csv')}")
    else:
        print("No results found for the given main business line.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except (KeyError, IndexError) as e:
    print(f"Error processing data: {e}")