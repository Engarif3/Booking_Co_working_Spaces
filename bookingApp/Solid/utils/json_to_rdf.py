import json
import uuid
from rdflib import XSD, Graph, Literal, Namespace, URIRef, RDF

def convert_json_to_rdf(json_data, username):
    data = json.loads(json_data)
    unique_id = str(uuid.uuid4())  

    # namespaces definition
    SCHEMA = Namespace("http://schema.org/")
    EX = Namespace("http://example.org/")

    g = Graph()
    space_uri = URIRef(f"http://example.org/Space{unique_id}")
    g.add((space_uri, RDF.type, SCHEMA.Place))
    g.add((space_uri, SCHEMA.spaceId, Literal(data['space_id'])))
    g.add((space_uri, SCHEMA.creator, Literal(username)))
    g.add((space_uri, SCHEMA.description, Literal(data['space_details'])))
    g.add((space_uri, SCHEMA.floorSize, Literal(data['size'])))
    g.add((space_uri, SCHEMA.capacity, Literal(data['capacity'])))
    g.add((space_uri, SCHEMA.price, Literal(data['price'])))
    g.add((space_uri, EX.available, Literal(1 if data['checkbox'] else 0)))
    g.add((space_uri, SCHEMA.address, Literal(data['location_address'])))
    g.add((space_uri, SCHEMA.addressLocality, Literal(data['location_city'])))
    g.add((space_uri, SCHEMA.postalCode, Literal(data['location_postal_code'])))
    
 
    # Date and time handling
    if data.get('availability_start'):
        start_datetime = Literal(data['availability_start'], datatype=XSD.dateTime)
        g.add((space_uri, SCHEMA.startDate, start_datetime))
    if data.get('availability_end'):
        end_datetime = Literal(data['availability_end'], datatype=XSD.dateTime)
        g.add((space_uri, SCHEMA.endDate, end_datetime))

    rdf_output = g.serialize(format="turtle").decode('utf-8')
    return rdf_output.strip()
