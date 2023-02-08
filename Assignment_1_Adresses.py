# RESUME of the CODE:

# The code is trying to scrape addresses details from a list of company websites stored in a parquet file.
# It reads a Parquet file containing the website names into a Pandas DataFrame and then uses the extract_address_details function to extract the details.
# It will check if the website has a Google Maps integration by searching for the "iframe" tag in the HTML content with a "src" attribute containing "google.com/maps". 
# If the website has a Google Maps integration, it will extract the address details using the "class" attributes of the "span" and "div" tags.
# If the website does not have a Google Maps integration, it will use the Geocoder library to extract the location data using the URL.
# The details are then written to a CSV file with headers "Website", "Country", "City", "Postcode", and "Road Number" and they are also printed in the terminal.

import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import geocoder

def extract_address_details(url):
    # Check if the URL starts with "http" or "https"
    if not url.startswith("http"):
        # If not, add "http://" to the beginning of the URL
        url = "http://" + url

    # Make the request and extract the HTML content
    try:
        response = requests.get(url)
        html_content = response.text
    except:
        return None

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # Check if the website has a Google Maps integration
    iframe = soup.find("iframe", src=lambda x: "google.com/maps" in x)
    if iframe:
        if iframe is None:
            return None
        else:
            # Extract the address details
            address = {}
            address["Country"] = None
            address["City"] = None
            address["Postcode"] = None
            address["Road Number"] = None

        # Search for the relevant tags containing the address details
        for tag in soup.find_all(["span", "div"]):
            if tag.get("class") and "country-name" in tag["class"]:
                address["Country"] = tag.text
            if tag.get("class") and "locality" in tag["class"]:
                address["City"] = tag.text
            if tag.get("class") and "postal-code" in tag["class"]:
                address["Postcode"] = tag.text
            if tag.get("class") and "street-address" in tag["class"]:
                address["Road Number"] = tag.text
        return address
    else:
        # Use the Geocoder library to extract the location data
        try:
            g = geocoder.osm(url)
            address = {}
            address["Country"] = g.country
            address["City"] = g.city
            address["Postcode"] = g.postal
            address["Road Number"] = None
            return address
        except:
            return None

# Read the Parquet file into a Pandas DataFrame
df = pd.read_parquet(r'C:\Users\User\Downloads\list of company websites.snappy.parquet')

# Create a CSV file
with open('address_details.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["Website", "Country", "City", "Postcode", "Road Number"])
    writer.writeheader()

    # Loop over the DataFrame and extract the address details
    for i, row in df.iterrows():
        url = row["domain"]
        address = extract_address_details(url)
        if address:
            writer.writerow({"Website": url, "Country": address["Country"], "City": address["City"], "Postcode": address["Postcode"], "Road Number": address["Road Number"]})
            print(f"{url} has a Google Maps integration.")
            print(f"Country: {address['Country']}")
            print(f"City: {address['City']}")
            print(f"Postcode: {address['Postcode']}")
            print(f"Road Number: {address['Road Number']}")
        else:
            print(f"{url} has no Google Maps integration.")
            writer.writerow({"Website": url, "Country": None, "City": None, "Postcode": None})
