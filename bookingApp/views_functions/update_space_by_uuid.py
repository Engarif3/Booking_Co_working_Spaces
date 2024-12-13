from rdflib import XSD, Graph, Namespace, URIRef, Literal
from bookingApp.Solid.solid_auth import solid_auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from bookingApp.forms import UpdateSpaceForm

EX = Namespace("http://example.org/")

from datetime import datetime
def update_space_by_uuid(solid_session, user_pod_url, space_uuid, updated_data):
    response = solid_session.get(user_pod_url, headers={"Accept": "text/turtle"})
    graph = Graph()
    if response.status_code == 200:
        graph.parse(data=response.content, format="turtle")
    else:
        print("Failed to fetch data from the POD")
        return False

    EX = Namespace("http://example.org/")
    SCHEMA = Namespace("http://schema.org/")
    space_uri = URIRef(f"{EX}{space_uuid}")

    for property_uri, new_value in updated_data.items():
        predicate = URIRef(property_uri)
        graph.remove((space_uri, predicate, None))

      
        if property_uri in [str(SCHEMA.startDate), str(SCHEMA.endDate)] and new_value:
            try:
                # Handle both date and time along with timezone
                formatted_datetime = datetime.strptime(new_value, "%Y-%m-%dT%H:%M:%S%z")
                literal_datetime = Literal(formatted_datetime, datatype=XSD.dateTime)
                graph.add((space_uri, predicate, literal_datetime))
            except ValueError as e:
                print(f"Error parsing datetime '{new_value}': {e}")
            
        else:
            graph.add((space_uri, predicate, Literal(new_value)))

    updated_rdf_data = graph.serialize(format="turtle")
    update_response = solid_session.put(user_pod_url, data=updated_rdf_data, headers={"Content-Type": "text/turtle"})
    return update_response.ok


SCHEMA = Namespace("http://schema.org/")



def update_space_by_id(request, uuid):
    if request.method == 'POST':
        form = UpdateSpaceForm(request.POST)
        if form.is_valid():
            solid_username = request.session.get('solid_username')
            solid_password = request.session.get('solid_password')
            user_pod_url = f'https://{solid_username}.solidcommunity.net/public/user_data.ttl'
            session = solid_auth('https://solidcommunity.net/', solid_username, solid_password)
            
            availability = 1 if 'checkbox' in request.POST and request.POST['checkbox'] == 'Yes' else 0

            updated_data = {
                str(SCHEMA.spaceId): form.cleaned_data['space_id'],
                str(SCHEMA.description): form.cleaned_data['space_details'],
                str(SCHEMA.capacity): form.cleaned_data['capacity'],
                str(SCHEMA.price): form.cleaned_data['price'],
                str(SCHEMA.address): form.cleaned_data['location_address'],
                str(SCHEMA.addressLocality): form.cleaned_data['location_city'],
                str(SCHEMA.postalCode): form.cleaned_data['location_postal_code'],
                str(SCHEMA.floorSize): form.cleaned_data['size'],
                str(EX.available): availability,
                str(SCHEMA.startDate): form.cleaned_data.get('start_date').isoformat() if form.cleaned_data.get('start_date') else None,
                str(SCHEMA.endDate): form.cleaned_data.get('end_date').isoformat() if form.cleaned_data.get('end_date') else None, 
            }
        
            if update_space_by_uuid(session, user_pod_url, uuid, updated_data):
                return HttpResponseRedirect(reverse('show_pod_data'))
            else:
                return HttpResponse("Failed to update the space.", status=500)
    else:
        form = UpdateSpaceForm()
        

    return render(request, 'app/show_pod_data.html', {'form': form})