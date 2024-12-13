from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url

from django.shortcuts import redirect, render
import requests
from bookingApp.Solid.solid_auth import solid_auth
from bookingApp.forms import SolidLoginForm
import logging

logger = logging.getLogger(__name__)

def solid_login_credentials(request):
    if request.method == 'POST':
        form = SolidLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            idp = 'https://solidcommunity.net/'
            try:
    
                session = solid_auth(idp, username, password)
                request.session['solid_username'] = username
                request.session['solid_password'] = password
                request.session['is_solid_logged_in'] = True
                request.session.save()
                check_and_set_my_created_space_data_exists(request, username)
                check_and_set_booking_data_exists(request, username)

                next_url = request.POST.get('next', request.GET.get('next', ''))
                default_url = reverse('show_all_data')
                if next_url and is_safe_url(next_url, allowed_hosts={request.get_host()}):
                    return HttpResponseRedirect(next_url)
                else:
                    return HttpResponseRedirect(default_url)
             
            except Exception as error:
                logger.error(f"Login failed for user: {username}, error: {error}")
                return HttpResponse('<h1>Login Failed</h1>')

    else:
        next_url = request.GET.get('next', '')
        form = SolidLoginForm()
        return render(request, 'app/solid_login_form.html', {'form': form, 'next': next_url})



def check_and_set_my_created_space_data_exists(request, username):
    created_space_url = f"https://{username}.solidcommunity.net/public/user_data.ttl"
    try:
        response = requests.head(created_space_url)
        request.session['pod_data_exists'] = response.status_code == 200
    except requests.RequestException:
        request.session['pod_data_exists'] = False
        
def check_and_set_booking_data_exists(request, username):
    booking_confirmation_url = f"https://{username}.solidcommunity.net/public/booking_confirmation.ttl"
    try:
        response = requests.head(booking_confirmation_url)
        print(response)
        request.session['booking_data_exists'] = response.status_code == 200
    except requests.RequestException:
        request.session['booking_data_exists'] = False
        
        
