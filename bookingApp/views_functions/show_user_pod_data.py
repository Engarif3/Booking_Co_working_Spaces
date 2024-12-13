from django.shortcuts import render
from bookingApp.Solid.fetch_pod_data import fetch_pod_data

def show_user_pod_data(request):
    solid_username = request.session.get('solid_username')
    solid_password = request.session.get('solid_password')
    solid_url = 'https://solidcommunity.net/'
    file_url = f"https://{solid_username}.solidcommunity.net/public/user_data.ttl"
     
    spaces_data = fetch_pod_data(solid_url, solid_username, solid_password, file_url)
    pod_data_exists = bool(spaces_data)
    return render(request, 'app/show_pod_data.html', {'spaces_data': spaces_data, 'pod_data_exists': pod_data_exists})
