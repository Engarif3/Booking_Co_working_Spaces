from django.shortcuts import render
import requests
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF
import pgeocode
import re

from datetime import datetime
import pytz

from bookingApp.Solid.utils.parse_date import parse_date

nomi = pgeocode.Nominatim('de') 

city_name_mapping = {
    "Munich": "München",
    "Nuremberg": "Nürnberg",
    "Cologne": "Köln",
    "Hanover": "Hannover",
}

# ===================================== Trusted functions =======================================
def validate_city_postal_code(city, postal_code):
    nomi = pgeocode.Nominatim('de')
    result = nomi.query_postal_code(postal_code)
    if result is not None and result.place_name is not None:
        place_name = result.place_name
        if isinstance(place_name, float) and not place_name == place_name:  # NaN check
            return False
        place_name = str(place_name)

        city_names = [name.strip().lower() for name in place_name.split(',')]
        normalized_city = city_name_mapping.get(city, city).lower()
        if normalized_city in city_names:
            return True
    return False

def is_trusted_capacity(space_details):
    trusted_ratio = 3  
    try:
        floor_size = float(space_details['Size'])
        capacity = float(space_details['Capacity'])
        if floor_size / capacity > trusted_ratio:
            return True
    except (ValueError, KeyError):
        return False
    return False


def is_trusted_price(city, price, size):

    city_name_mapping = {
        "Munich": "München",
        "Nuremberg": "Nürnberg",
        "Cologne": "Köln",
        "Hanover": "Hannover",
    }

    city_price_map = {
        "Berlin": 21,
        "München": 20,   
        "Frankfurt am Main": 19,
        "Stuttgart": 18,
        "Hamburg": 16,
        "Köln": 15,
        "Düsseldorf": 14,

    }

    normal_price_per_m2 = 12
    variance = 2  

    try:
        normalized_city = city_name_mapping.get(city, city)

        price = float(price)
        size = float(size)

        if size <= 0: 
            return False


        average_price_per_m2 = city_price_map.get(normalized_city, normal_price_per_m2)
        price_per_m2 = price / size
        
        lower_bound = average_price_per_m2 - variance
        upper_bound = average_price_per_m2 + variance
        return lower_bound <= price_per_m2 <= upper_bound
    except (ValueError, TypeError):
        return False





def is_trusted_address(address):
    return bool(re.search(r'\d', address))

# ===================================================================================

SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/")

CENTRAL_POD_URL = 'https://centralpod.solidcommunity.net/public/usernames.ttl'

def fetch_usernames_from_central_pod():
    response = requests.get(CENTRAL_POD_URL)
    if response.status_code != 200:
        return []

    g = Graph().parse(data=response.content, format="turtle")
    usernames = []

    for _, _, username in g.triples((None, EX.username, None)):
        usernames.append(str(username))
    
    return usernames



def fetch_user_data(username, exclude_username=None):
    user_pod_url = f'https://{username}.solidcommunity.net/public/user_data.ttl'
    response = requests.get(user_pod_url)
    if response.status_code != 200:
        print("Failed to fetch user data for username:", username)
        return []

    g = Graph().parse(data=response.content, format="turtle")
    spaces = g.subjects(RDF.type, SCHEMA.Place)
    user_data_sets = []

    for space in spaces:
        space_details = {}
        uuid = str(space).rsplit('/', 1)[-1]
        
        start_date_str = space_details.get('Start_Date', '')
        end_date_str = space_details.get('End_Date', '')
        # Parse the datetime strings to datetime objects
        if start_date_str:
            space_details['Start_Date'] = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            space_details['End_Date'] = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

        for p, o in g.predicate_objects(subject=space):
            label_map = {
                SCHEMA.spaceId: "Space_ID",
                SCHEMA.description: "Space_Details",
                SCHEMA.floorSize: "Size",
                SCHEMA.capacity: "Capacity",
                SCHEMA.address: "Address",
                SCHEMA.postalCode: "Post",
                SCHEMA.addressLocality: "City",
                SCHEMA.price: "Price",
                EX.available: "Available",
                SCHEMA.creator: "Created_By",
                SCHEMA.startDate: "Start_Date",
                SCHEMA.endDate: "End_Date"
            }
            label = label_map.get(p)
            if label:
                space_details[label] = str(o)
            if label == "Available":
                            space_details[label] = "Yes" if str(o).lower() in ["1", "true"] else "No"

        space_details['Trust_Percentage'] = calculate_trust_percentage(space_details)
        print(f"UUID: {uuid}, Trust Percentage: {space_details['Trust_Percentage']}%")

        if space_details['Trust_Percentage'] >= 51:
            print(f"Adding space with UUID: {uuid} to display list.")
            space_details['UUID'] = uuid
            user_data_sets.append(space_details)

    return user_data_sets

def calculate_trust_percentage(space_details):
    total_trust = 100
    if not is_trusted_capacity(space_details):
        total_trust -= 20
    if not is_trusted_price(space_details['City'], space_details['Price'], space_details['Size']):
        total_trust -= 10
    if not is_trusted_address(space_details['Address']):
        total_trust -= 20
    if not validate_city_postal_code(space_details['City'], space_details['Post']):
        total_trust = 0  

    return total_trust



def show_all_data(request):
    usernames = fetch_usernames_from_central_pod()
    all_spaces_data = []

    for username in usernames:
        user_spaces_data = fetch_user_data(username)
        for space in user_spaces_data:
            # ISO format string to datetime objects
            if 'Start_Date' in space and isinstance(space['Start_Date'], str):
                space['Start_Date'] = parse_date(space['Start_Date'])
            if 'End_Date' in space and isinstance(space['End_Date'], str):
                space['End_Date'] = parse_date(space['End_Date'])
        
        filtered_spaces = [
            space for space in user_spaces_data
            if space['Available'] in ["Yes", "1"] and space['Trust_Percentage'] >= 51
            ]
        all_spaces_data.extend(filtered_spaces)
        

    solid_username = request.session.get('solid_username', None)
    return render(request, 'app/show_all_data.html', {
        'spaces_data': all_spaces_data,
        'logged_in_username': solid_username 
    })

