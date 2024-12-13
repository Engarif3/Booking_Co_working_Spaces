from rdflib import Graph, Namespace, URIRef

from bookingApp.Solid.solid_auth import solid_auth


def delete_space_by_uuid(solid_session, user_pod_url, space_uuid):
    response = solid_session.get(user_pod_url, headers={"Accept": "text/turtle"})
    graph = Graph()
    if response.status_code == 200:
        graph.parse(data=response.content, format="turtle")
    else:
        print("Failed to fetch data from the POD")
        return False
    
    EX = Namespace("http://example.org/")
    space_uri = URIRef(f"{EX}{space_uuid}")  
    
    for predicate, obj in graph.predicate_objects(subject=space_uri):
        graph.remove((space_uri, predicate, obj))

    print("After deletion:", graph.serialize(format="turtle").decode("utf-8"))

    updated_rdf_data = graph.serialize(format="turtle")
    update_response = solid_session.put(user_pod_url, data=updated_rdf_data, headers={"Content-Type": "text/turtle"})
    print("Update response status code:", update_response.status_code)
    return update_response.ok


from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

def delete_space_by_id(request, uuid):
    if request.method == 'POST':
        solid_username = request.session.get('solid_username')
        solid_password = request.session.get('solid_password')
        user_pod_url = f'https://{solid_username}.solidcommunity.net/public/user_data.ttl'
        
        session = solid_auth('https://solidcommunity.net/', solid_username, solid_password)

        
        if delete_space_by_uuid(session, user_pod_url, uuid):
            return HttpResponseRedirect(reverse('show_pod_data'))
        else:
            return HttpResponse("Failed to delete the space.", status=500)
    else:
        return HttpResponseRedirect(reverse('show_pod_data'))
