import requests
def add_solid_username_to_navbar(request):
    return {
        'solid_username': request.session.get('solid_username', '') if request.session.get('is_solid_logged_in') else ''
    }

def booking_data_exists(request):
    print("Checking if booking data exists")
    if request.session.get('is_solid_logged_in', False):
        solid_username = request.session.get('solid_username')
        print(f"Solid username: {solid_username}")
        booking_confirmation_url = f"https://{solid_username}.solidcommunity.net/public/booking_confirmation.ttl"
        
        try:
            response = requests.head(booking_confirmation_url)
            print(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                return {'pod_data_exists': True}
        except requests.RequestException as e:
            print(f"Request failed: {e}")
    return {'pod_data_exists': False}

