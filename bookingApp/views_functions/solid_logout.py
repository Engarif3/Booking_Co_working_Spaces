from django.http import HttpResponse
from django.shortcuts import  render

def solid_logout(request):
    request.session.pop('is_solid_logged_in', None) 
    request.session.flush()  
    return render(request, 'app/logout_success.html')