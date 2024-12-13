import logging
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rdflib import Graph, Namespace, URIRef
import requests

from bookingApp.Solid.utils.parse_date import parse_date

# Constants and Namespaces
CENTRAL_POD_URL = "https://centralpod.solidcommunity.net/public/usernames.ttl"
SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/")
logger = logging.getLogger(__name__)

def fetch_usernames_from_central_pod():
    response = requests.get(CENTRAL_POD_URL)
    if response.status_code != 200:
        logger.error(f"Failed to fetch usernames from the central pod with status code: {response.status_code}")
        return []

    g = Graph().parse(data=response.content, format="turtle")
    user_pod_urls = [f"https://{str(username)}.solidcommunity.net/public/user_data.ttl" 
                     for _, _, username in g.triples((None, EX.username, None))]
    return user_pod_urls

predicate_to_label = {
    SCHEMA.spaceId: "Space ID",
    SCHEMA.description: "Space Details",
    SCHEMA.capacity: "Capacity",
    SCHEMA.price: "Price",
    EX.available: "Available",
    SCHEMA.creator: "Created By"
}

def get_space_details(request, uuid):
    space_uris = fetch_usernames_from_central_pod()
    for space_uri in space_uris:
        response = requests.get(space_uri, headers={"Accept": "text/turtle"})
        if response.status_code == 200:
            graph = Graph().parse(data=response.content, format="turtle")
            space = URIRef(f"http://example.org/Space{uuid}")
            if (space, None, None) in graph:
                space_details = {predicate_to_label.get(predicate, str(predicate).split('/')[-1]): str(obj)
                                 for predicate, obj in graph.predicate_objects(subject=space)}
                logger.debug(f"Fetched space details: {space_details}")
                return space_details
    logger.error(f"No details found for space with UUID: {uuid}")
    return {}

def book_space(request, uuid):
    if not request.session.get('solid_username') or not request.session.get('solid_password'):
        login_url = reverse('solid_login')  
        next_url = reverse('confirm_booking', args=[uuid]) 
        return redirect(f'{login_url}?next={next_url}')
    
    space_details = get_space_details(request, uuid)

    
    if space_details:
        # Format dates for display
        space_details['startDate'] = parse_date(space_details['startDate'])
        space_details['endDate'] = parse_date(space_details['endDate'])
        adjusted_space_details = {key.replace(' ', '_'): value for key, value in space_details.items()}
        return render(request, 'app/confirm_booking.html', {'space_details': adjusted_space_details, 'uuid': uuid})
    else:
        logger.error("Failed to fetch space details for UUID: {uuid}")
        return HttpResponse("Failed to fetch space details.")
