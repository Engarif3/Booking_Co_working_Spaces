from django.shortcuts import render
from rdflib import RDF, Graph, Namespace
from bookingApp.Solid.solid_auth import solid_auth
from bookingApp.Solid.utils.parse_date import parse_date

EX = Namespace("http://example.org/")
SCHEMA = Namespace("http://schema.org/")


from datetime import datetime
from rdflib import RDF, Graph, Namespace
from bookingApp.Solid.solid_auth import solid_auth

#namespaces
EX = Namespace("http://example.org/")
SCHEMA = Namespace("http://schema.org/")

def fetch_booking_data(solid_session, user_pod_url):
    booking_file_url = f"{user_pod_url}booking_confirmation.ttl"
    response = solid_session.get(booking_file_url, headers={"Accept": "text/turtle"})
    bookings = []

    if response.status_code == 200:
        g = Graph().parse(data=response.content, format="turtle")
        for booking in g.subjects(RDF.type, EX.BookingConfirmation):
            booking_details = {
                "ID": str(booking).split('/')[-1],
                "Artist": str(g.value(booking, SCHEMA.creator)),
                "Identifier": str(g.value(booking, SCHEMA.spaceDetails)),
                "Description": str(g.value(booking, SCHEMA.description)),
                "Capacity": str(g.value(booking, SCHEMA.capacity)),
                "Price": str(g.value(booking, SCHEMA.price)),
                "Address": str(g.value(booking, SCHEMA.address)),
                "City": str(g.value(booking, SCHEMA.addressLocality)),
                "Post": str(g.value(booking, SCHEMA.postalCode)),
                "Available": str(g.value(booking, EX.available)),
                "Start_Date": parse_date(str(g.value(booking, SCHEMA.startDate))),
                "End_Date": parse_date(str(g.value(booking, SCHEMA.endDate)))
            }
            bookings.append(booking_details)
    else:
        print(f"Failed to fetch booking data. Status code: {response.status_code}")

    return bookings

def show_bookings(request):
    solid_username = request.session.get('solid_username')
    solid_password = request.session.get('solid_password')
    user_pod_url = f"https://{solid_username}.solidcommunity.net/public/"

    session = solid_auth('https://solidcommunity.net/', solid_username, solid_password)
    bookings = fetch_booking_data(session, user_pod_url)
    booking_data_exists = bool(bookings)
    return render(request, 'app/show_bookings.html', {'bookings': bookings, 'booking_data_exists': booking_data_exists})
