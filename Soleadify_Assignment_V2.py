# This script defines a function called scrape_websites that scrapes information from a list of URLs and writes the results to a CSV file.

# The function takes two arguments: parquet_file and output_file, which are the input and output files, respectively.
# The parquet_file is read into a pandas DataFrame and the URLs are extracted from the 'domain' column.

# For each URL, the function sends a GET request using the requests module, and searches the response text for information using a set of regular expressions.
# Specifically, it searches for the country, city, postcode, and road number using different regular expression patterns.

# The scraped information is printed to the console and also stored in a list of dictionaries, which is later converted into a Pandas DataFrame and saved to a CSV file
# (the method used to save data to a csv file was a little bit different now).

# The program crashes after some trials because of a connection problem, but it succesfully extracts some postcodes making me understand that the code should be fine.

import re
import pandas as pd
import requests
import csv

def scrape_websites(parquet_file, output_file):
    # Read the URLs from the Parquet file
    df = pd.read_parquet(parquet_file)
    urls = df['domain'].tolist()

    # Initialize an empty list to store the scraped data
    data = []

    # Loop over each URL and scrape the relevant information
    for url in urls:
        # Check if the URL starts with "http" or "https"
        if not url.startswith("http"):
            url = "http://" + url
            
        response = requests.get(url)
        html = response.text

        # Define regular expressions to match the patterns of the country, postcode, and road number
        country_patterns = [
            re.compile(r'<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>'), 
            re.compile(r'<strong>([A-Za-z ]+)</strong>[\s\S]*<span>([A-Za-z ]+)</span>'), 
        ]
        postcode_patterns = [
            re.compile(r'\b\d{5}(?:-\d{4})?\b'),
            re.compile(r'<span>(\d{5})</span>'), 
        ]
        road_number_patterns = [
            re.compile(r'<span>(\d+ [A-Za-z ]+)</span>'), 
            re.compile(r'<span>([A-Za-z ]+ \d+)</span>'), 
        ]

        city_patterns = [
            re.compile(r'<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>'), 
            re.compile(r'<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>'), 
        ]

        street_name_patterns = [
            re.compile(r'<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>'), 
            re.compile(r'<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>'), 
            re.compile(r'<span>([A-Za-z ]+) ([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+)</span>'), 
            re.compile(r'<span>([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+) ([A-Za-z ]+)</span>'), 
            re.compile(r'<span>([A-Za-z ]+) ([A-Za-z ]+)</span>[\s\S]*<span>([A-Za-z ]+) ([A-Za-z ]+)</span>'), 
        ]       

        # Search for matches using the regular expressions
        country_match = None
        for pattern in country_patterns:
            country_match = pattern.findall(html)
            if country_match:
                country_match = country_match[0]
                break
        postcode_match = None
        for pattern in postcode_patterns:
            postcode_match = pattern.findall(html)
            if postcode_match:
                postcode_match = postcode_match[0]
                break
        road_number_match = None
        for pattern in road_number_patterns:
            road_number_match = pattern.findall(html)
            if road_number_match:
                road_number_match = road_number_match[0]
                break
        city_match = None
        for pattern in city_patterns:
            city_match = pattern.findall(html)
            if city_match:
                city_match = city_match[0]
                break
        street_name_match = None
        for pattern in street_name_patterns:
            street_name_match = pattern.findall(html)
            if street_name_match:
                street_name_match = street_name_match[0]
                break

        # Extract the relevant text using the `.group()` method
        country = country_match[0] if country_match else ''
        city = city_match[0] if city_match else ''
        postcode = postcode_match if postcode_match else ''
        road_number = road_number_match if road_number_match else ''
        street_name = ', '.join(filter(None, street_name_match)) if street_name_match else ''

        # Print the scraped data
        print(f"URL: {url}")
        print(f"Country: {country}")
        print(f"City: {city}")
        print(f"Postcode: {postcode}")
        print(f"Road Name: {street_name}")
        print(f"Road number: {road_number}")
        print()

        # Store the scraped data in a dictionary
        data.append({'url': url, 'country': country, 'city': city, 'postcode': postcode, 'road_number': road_number, 'street_name': street_name})

    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_file, index=False)

    # Return the DataFrame
    return df

dataframe = scrape_websites(r'C:\Users\User\Desktop\test\list of company websites.snappy.parquet', 'output_file.csv')
print(dataframe)
