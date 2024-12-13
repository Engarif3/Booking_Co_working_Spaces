import json
from django.http import HttpResponse
from django.shortcuts import render
from rdflib import Graph, Literal, RDF, Namespace, URIRef
from bookingApp.Solid.solid_auth import solid_auth
from bookingApp.Solid.utils.json_to_rdf import convert_json_to_rdf
from bookingApp.forms import TextInputForm


# Constants and Namespaces
CENTRAL_POD_URL = "https://centralpod.solidcommunity.net/public/usernames.ttl"
CENTRAL_POD_USERNAME = "centralpod"
CENTRAL_POD_PASSWORD = "Thesis_123"
ACL = Namespace("http://www.w3.org/ns/auth/acl#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
EX = Namespace("http://example.org/")

# Constants and Namespaces
CENTRAL_POD_URL = "https://centralpod.solidcommunity.net/public/usernames.ttl"
CENTRAL_POD_USERNAME = "centralpod"
CENTRAL_POD_PASSWORD = "Thesis_123"
ACL = Namespace("http://www.w3.org/ns/auth/acl#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
EX = Namespace("http://example.org/")


def create_acl_data(user_pod_url, owner_webid, public_access=True):
    """Generate ACL data to set read and write permissions for public."""
    g = Graph()
    owner_auth = URIRef(f"{user_pod_url}#owner")
    g.add((owner_auth, RDF.type, ACL.Authorization))
    g.add((owner_auth, ACL.agent, URIRef(owner_webid)))
    g.add((owner_auth, ACL.accessTo, URIRef(user_pod_url)))
    g.add((owner_auth, ACL.mode, ACL.Read))
    g.add((owner_auth, ACL.mode, ACL.Write))
    g.add((owner_auth, ACL.mode, ACL.Control))

    if public_access:
        public_auth = URIRef(f"{user_pod_url}#public")
        g.add((public_auth, RDF.type, ACL.Authorization))
        g.add((public_auth, ACL.agentClass, FOAF.Agent))
        g.add((public_auth, ACL.accessTo, URIRef(user_pod_url)))
        g.add((public_auth, ACL.mode, ACL.Read))
        g.add((public_auth, ACL.mode, ACL.Write))

    return g.serialize(format="turtle")

def update_acl(session, acl_url, acl_data):
    """Update the ACL for the given URL."""
    headers = {"Content-Type": "text/turtle"}
    response = session.put(acl_url, data=acl_data, headers=headers)
    return response.ok


def append_data_to_user_pod(solid_session, user_pod_url, rdf_data):
    existing_response = solid_session.get(user_pod_url)
    graph = Graph()
    if existing_response.status_code == 200:
        graph.parse(data=existing_response.content, format="turtle")
    graph.parse(data=rdf_data, format="turtle")
    updated_rdf_data = graph.serialize(format="turtle")
    update_response = solid_session.put(user_pod_url, data=updated_rdf_data, headers={"Content-Type": "text/turtle"})
    return update_response.ok

def update_central_pod_with_username(solid_session, username):
    central_session = solid_auth("https://solidcommunity.net/", CENTRAL_POD_USERNAME, CENTRAL_POD_PASSWORD)
    graph = Graph()
    response = central_session.get(CENTRAL_POD_URL)
    if response.status_code == 200:
        graph.parse(data=response.content, format="turtle")
    username_uri = URIRef(f"{EX}{username}")
    if (username_uri, RDF.type, EX.User) not in graph:
        graph.add((username_uri, RDF.type, EX.User))
        graph.add((username_uri, EX.username, Literal(username)))
        data = graph.serialize(format="turtle")
        put_response = central_session.put(CENTRAL_POD_URL, data=data, headers={"Content-Type": "text/turtle"})
        return put_response.ok
    return True 


def create_file_to_solid(request):
    if request.method == 'POST':
        form = TextInputForm(request.POST)
        if form.is_valid():
      
            # Prepare the data dictionary to include all necessary fields.
            data_dict = {
                'space_id': form.cleaned_data['space_id'],
                'space_details': form.cleaned_data['space_details'],
                'capacity': form.cleaned_data['capacity'],
                'price': form.cleaned_data['price'],
                'checkbox': form.cleaned_data['checkbox'],
                'availability_start': form.cleaned_data.get('availability_start').isoformat() if form.cleaned_data.get('availability_start') else None,
                'availability_end': form.cleaned_data.get('availability_end').isoformat() if form.cleaned_data.get('availability_end') else None,
                'location_address': form.cleaned_data['location_address'],
                'location_city': form.cleaned_data['location_city'],
                'location_postal_code': form.cleaned_data['location_postal_code'],
                'size': form.cleaned_data['size'],
            }

            solid_username = request.session.get('solid_username')
            solid_password = request.session.get('solid_password')
            session = solid_auth('https://solidcommunity.net/', solid_username, solid_password)
            user_pod_url = f'https://{solid_username}.solidcommunity.net/public/user_data.ttl'

            # dictionary to RDF data.
            rdf_data = convert_json_to_rdf(json.dumps(data_dict, default=str), solid_username)

            # Append the new RDF data to the user's POD.
            if append_data_to_user_pod(session, user_pod_url, rdf_data):
                acl_data = create_acl_data(user_pod_url, f"https://{solid_username}.solidcommunity.net/profile/card#me")

                # Update ACL for the new data file.
                if update_acl(session, user_pod_url + ".acl", acl_data):
                    request.session['pod_data_exists'] = True  # Set a session flag after ACL update.
                    if update_central_pod_with_username(session, solid_username):
                        return render(request, 'app/space_creation_successful.html')
                    else:
                        return HttpResponse("Data appended, but failed to update username in central POD.", status=500)
                else:
                    return HttpResponse("Failed to set ACL.", status=500)
            else:
                return HttpResponse("Failed to update user's POD.", status=500)
        else:
            print("Form errors:", form.errors)  # Log the form errors
            return HttpResponse(f"Invalid form data: {form.errors}", status=400)
    else:
        form = TextInputForm()
        return render(request, 'app/provide_space_info.html', {'form': form})