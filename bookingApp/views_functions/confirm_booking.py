from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from rdflib import XSD, Graph, Literal, RDF, Namespace, URIRef
import uuid
from bookingApp.Solid.solid_auth import solid_auth
from bookingApp.views_functions.book_space import get_space_details
import pytz
from datetime import datetime, timedelta, timezone

# namespaces
EX = Namespace("http://example.org/")
SCHEMA = Namespace("http://schema.org/")

def parse_date(date_str):
    """Parse an ISO formatted date string to a datetime object with timezone adjusted to UTC."""
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",  
        "%Y-%m-%dT%H:%M:%S",    
        "%Y-%m-%dT%H:%M",      
    ]
    last_error = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            if parsed_date.tzinfo is None:
                parsed_date = pytz.utc.localize(parsed_date)
            else:
                parsed_date = parsed_date.astimezone(pytz.utc)
            return parsed_date
        except ValueError as e:
            last_error = e
    print(f"Error parsing date '{date_str}': {last_error}")
    return None
 
def create_booking_confirmation_data(space_details):
    g = Graph()
    booking_id = uuid.uuid4()  #unique ID for each booking
    booking_uri = URIRef(f"{EX}booking/{booking_id}")

    #RDF.type for the booking entry
    g.add((booking_uri, RDF.type, EX.BookingConfirmation))

    # Updated required fields with additional city and post keys
    required_fields = ['Space ID', 'Space Details', 'Capacity', 'Price', 'Created By', 'startDate', 'endDate', 'address', 'addressLocality', 'postalCode']
    if not all(key in space_details for key in required_fields):
        missing = [key for key in required_fields if key not in space_details]
        print("Missing fields:", missing)
        raise ValueError("Essential space details are missing. Cannot proceed with booking.")

   
    field_to_predicate = {
        'Space ID': SCHEMA.identifier,
        'Space Details': SCHEMA.description,
        'Capacity': SCHEMA.capacity,
        'Price': SCHEMA.price,
        'Created By': SCHEMA.creator,
        'startDate': SCHEMA.startDate,
        'endDate': SCHEMA.endDate,
        'address': SCHEMA.address,
        'postalCode': SCHEMA.postalCode,
        'addressLocality': SCHEMA.addressLocality,
    }

    for field, predicate in field_to_predicate.items():
        field_value = space_details.get(field)  
        print(field_value)
        if 'date' in field:
            date_value = Literal(field_value, datatype=XSD.dateTime)
            g.add((booking_uri, predicate, date_value))
        else:
         g.add((booking_uri, predicate, Literal(field_value)))


    # Return the serialized graph in Turtle format, decoded from bytes to string
    return g.serialize(format='turtle').decode('utf-8')



def store_booking_confirmation(solid_session, user_pod_url, booking_data):
    booking_file_url = f"{user_pod_url}booking_confirmation.ttl"
    response = solid_session.get(booking_file_url, headers={"Accept": "text/turtle"})
    graph = Graph()
    if response.ok:
        graph.parse(data=response.content, format="turtle")

    new_graph = Graph().parse(data=booking_data, format="turtle")
    combined_graph = graph + new_graph
    update_response = solid_session.put(booking_file_url, data=combined_graph.serialize(format='turtle'), headers={"Content-Type": "text/turtle"})
    return update_response.ok


def update_space_availability(session, creator_username, space_uuid, booked_start, booked_end):
    user_data_url = f"https://{creator_username}.solidcommunity.net/public/user_data.ttl"
    response = session.get(user_data_url, headers={"Accept": "text/turtle"})
    if not response.ok:
        return False, f"Failed to fetch existing data: {response.status_code}"

    graph = Graph().parse(data=response.content, format="turtle")
    space_uri = URIRef(f"{EX}Space{space_uuid}")
    available_status_predicate = URIRef(f"{EX}available")
    start_predicate = URIRef(f"{SCHEMA}startDate")
    end_predicate = URIRef(f"{SCHEMA}endDate")

    # Fetch current availability
    existing_start = next(graph.objects(subject=space_uri, predicate=start_predicate), None)
    existing_end = next(graph.objects(subject=space_uri, predicate=end_predicate), None)

    if existing_start is None or existing_end is None:
        return False, "No existing availability data found."

    existing_start = parse_date(str(existing_start))
    existing_end = parse_date(str(existing_end))

    # if booking covers the entire available range
    if booked_start <= existing_start and booked_end >= existing_end:
        graph.set((space_uri, available_status_predicate, Literal(False)))
        graph.set((space_uri, start_predicate, Literal("0000-00-00T00:00:00", datatype=XSD.dateTime)))
        graph.set((space_uri, end_predicate, Literal("0000-00-00T00:00:00", datatype=XSD.dateTime)))
        update_response = session.put(user_data_url, data=graph.serialize(format='turtle'), headers={"Content-Type": "text/turtle"})
        return update_response.ok, "Availability fully booked and reset successfully."


    graph.remove((space_uri, start_predicate, None))
    graph.remove((space_uri, end_predicate, None))

    new_start, new_end = None, None
    if booked_start > existing_start:
        new_start = existing_start
        new_end = booked_start
    if booked_end < existing_end:
        new_start = booked_end
        new_end = existing_end

    if new_start and new_end and new_start < new_end:
        graph.add((space_uri, start_predicate, Literal(new_start.isoformat(), datatype=XSD.dateTime)))
        graph.add((space_uri, end_predicate, Literal(new_end.isoformat(), datatype=XSD.dateTime)))

    update_response = session.put(user_data_url, data=graph.serialize(format='turtle'), headers={"Content-Type": "text/turtle"})
    return update_response.ok, "Availability updated successfully." if update_response.ok else f"Failed to update the graph: {update_response.text}"




def confirm_booking(request, uuid):
    if request.method == 'POST':
        space_details = get_space_details(request, uuid)
        if not space_details:
            return HttpResponse("Space details not found.", status=404)

        # Parsing dates
        available_start = parse_date(space_details['startDate'])
        available_end = parse_date(space_details['endDate'])
        user_start = parse_date(request.POST.get('startDate'))
        user_end = parse_date(request.POST.get('endDate'))
        print(available_start)
        print(available_end)
        print(user_start)
        print(user_end)
        
        space_details['startDate'] = user_start.isoformat()
        space_details['endDate'] = user_end.isoformat()


        # Checking if user provided times are within the available range
        if not (available_start <= user_start <= available_end and available_start <= user_end <= available_end):
            return HttpResponse("Selected booking time is out of available range.", status=400)
        
        # Proceed with booking if times are valid
        booking_user = request.session.get('solid_username')
        session = solid_auth('https://solidcommunity.net/', booking_user, request.session.get('solid_password'))
        
        
        try:
            booking_data = create_booking_confirmation_data(space_details)
            user_pod_url = f"https://{booking_user}.solidcommunity.net/public/"
            if store_booking_confirmation(session, user_pod_url, booking_data):
                if update_space_availability(session, space_details['Created By'], uuid, user_start, user_end):
                    return redirect('booking_success')
                else:
                    return HttpResponse('Failed to update availability.', status=500)
            else:
                return HttpResponse('Failed to store booking confirmation.', status=500)
        except ValueError as e:
            return HttpResponse(str(e), status=500)

    return render(request, 'app/confirm_booking.html', {'space_details': space_details, 'uuid': uuid})


