import datetime
from django import forms
from .models import User 


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class SolidCredentialsForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")
    idp = forms.URLField(label="Identity Provider URL")
    pod_endpoint = forms.URLField(label="POD Endpoint URL",  help_text="Enter the URL of your Solid POD.")


class SolidLoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")
    
# ==================================================================================================================
class TextInputForm(forms.Form):
    space_id = forms.IntegerField(label='Enter id', label_suffix=' ')
    space_details = forms.CharField(initial='')
    capacity = forms.IntegerField(initial='')
    price = forms.IntegerField()
    checkbox = forms.BooleanField(initial=True, disabled=True, label="Available")
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    location_address = forms.CharField(label='Address')
    location_city = forms.CharField(label='City')
    location_postal_code = forms.CharField(label='Postal Code', max_length=5)
 
    size = forms.IntegerField(label='Size (sq meters)')
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    availability_start = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'], 
        label='Available from'
    )
    availability_end = forms.DateTimeField(
        required=False,
        initial=datetime.datetime(2025, 12, 31, 23, 59),  
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],  
        label='Available to'
    )
    
    
    
    
    def clean_location_city(self):
        city = self.cleaned_data.get('location_city', '')
        return ' '.join(word.capitalize() for word in city.split())

# =================================================================================================================================
class UpdateSpaceForm(forms.Form):
    space_id = forms.IntegerField(label='Enter id', label_suffix=' ')
    space_details = forms.CharField(label='Space Details', max_length=100)
    capacity = forms.IntegerField(initial='')
    price = forms.DecimalField(label='Price')
    checkbox = forms.BooleanField(label='Available', required=False)
    location_address = forms.CharField(label='Address')
    location_city = forms.CharField(label='City')
    location_postal_code = forms.CharField(label='Postal Code', max_length=5)
    size = forms.IntegerField(label='Size (sq meters)')
    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'], 
        label='Availability Start'
    )
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'], 
        label='Availability End'
    )
    def clean_location_city(self):
        city = self.cleaned_data.get('location_city', '')
        return ' '.join(word.capitalize() for word in city.split())
    