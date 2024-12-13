from bookingApp.views_functions.book_space import book_space
from bookingApp.views_functions.confirm_booking import confirm_booking
from bookingApp.views_functions.create_file_to_solid import create_file_to_solid
from bookingApp.views_functions.delete_space_by_uuid import delete_space_by_id
from bookingApp.views_functions.fetch_booking_data import show_bookings
from bookingApp.views_functions.show_all_data import show_all_data
from bookingApp.views_functions.show_user_pod_data import show_user_pod_data
from bookingApp.views_functions.solid_login_credentials import solid_login_credentials
from bookingApp.views_functions.solid_logout import solid_logout
from bookingApp.views_functions.update_space_by_uuid import update_space_by_id

# Create your views here.

def solid_login(request):
    return solid_login_credentials(request)

def logout(request):
    return solid_logout(request)

def write_to_pod(request):
    return create_file_to_solid(request)


def show_user_data(request):
  return show_user_pod_data(request)

def show_all_user_data(request):
    return show_all_data(request)

def delete_space(request,uuid):
    return delete_space_by_id(request, uuid)

def update_space(request,uuid):
    return update_space_by_id(request, uuid)

def space_booking(request,uuid):
    return book_space(request, uuid)

def booking_confirmation(request,uuid):
    return confirm_booking(request, uuid)

from django.shortcuts import render

def booking_success(request):
    return render(request, 'app/booking_success.html')

def show_booking_data(request):
    return show_bookings(request)

from django.http import HttpResponse
import requests

def test_acl_access_view(request):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    session = requests.Session() 
    response = session.get('https://ariftest2.solidcommunity.net/public/user_data.ttl', headers={"Accept": "text/turtle"})
    if response.status_code == 200:
        return HttpResponse("Access successful, data: " + response.text)
    else:
        return HttpResponse("Failed to access data, status code: " + str(response.status_code), status=response.status_code)
