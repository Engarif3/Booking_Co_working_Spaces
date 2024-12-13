from django.shortcuts import render
from bookingApp.Solid.solid_auth import solid_auth
from bookingApp.Solid.utils.parse_date import parse_date
import rdflib
from rdflib.namespace import RDF, Namespace

from bookingApp.views_functions.show_all_data import is_trusted_address, is_trusted_capacity, is_trusted_price, validate_city_postal_code


def fetch_pod_data(solid_url, username, password, file_url):
    session = solid_auth(solid_url, username, password)
    response = session.get(file_url, headers={"Accept": "text/turtle"})
    response.encoding = 'utf-8'  
    if response.status_code != 200:
        print(f"Failed to fetch data from POD. Status code: {response.status_code}")
        return []

    g = rdflib.Graph()
    EX = Namespace("http://example.org/")
    SCHEMA = Namespace("http://schema.org/")
    g.bind("ex", EX)
    g.bind("schema", SCHEMA)

    g.parse(data=response.text, format="turtle")
    spaces_data = []

    for space in g.subjects(RDF.type, SCHEMA.Place):
        space_data = {
            "UUID": str(space).rsplit('/', 1)[-1],
            "Space_ID": str(g.value(space, SCHEMA.spaceId)),
            "Space_Details": str(g.value(space, SCHEMA.description)),
            "Capacity": str(g.value(space, SCHEMA.capacity)),
            "Size": str(g.value(space, SCHEMA.floorSize)),
            "Price": str(g.value(space, SCHEMA.price)),
            "Address": str(g.value(space, SCHEMA.address)),
            "Post": str(g.value(space, SCHEMA.postalCode)),
            "Address_Locality": str(g.value(space, SCHEMA.addressLocality)),
            "Available": "Yes" if g.value(space, EX.available) else "No",
            "Creator": str(g.value(space, SCHEMA.creator)),
            "Start_Date": parse_date(str(g.value(space, SCHEMA.startDate))),
            "End_Date": parse_date(str(g.value(space, SCHEMA.endDate))),
        }
        space_data['Trust_Percentage'] = calculate_trust_percentage(space_data) 
        spaces_data.append(space_data)

    return spaces_data


def calculate_trust_percentage(space_details):
    total_trust = 100
    city = space_details.get('Address_Locality', '') 
    if not is_trusted_capacity(space_details):
        total_trust -= 20
    if not is_trusted_price(city, space_details.get('Price', 0), space_details.get('Size', 0)):
        total_trust -= 10
    if not is_trusted_address(space_details.get('Address', '')):
        total_trust -= 20
    if not validate_city_postal_code(city, space_details.get('Post', '')):
        total_trust = 0  

    return total_trust
