from django.shortcuts import render, redirect, HttpResponse
import requests
from .models import City
from .forms import CityForm
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def index(request):
    res = requests.get('https://ipinfo.io/')
    data = res.json()
    print(res.text)
    print(data['loc'].split(',')[0])
    print(data['loc'].split(',')[1])
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=b69dbe802588ff579fe043e5ab417eb3'
    # city = "San Jose"
    err_msg = ''
    message = ''
    message_class = ''
    if request.method == 'POST':
        new_city = request.POST.get('name')
        # form = CityForm(request.POST)
        # if form.is_valid():
        #     new_city = form.cleaned_data['name']
        #     city = City.objects.get(name = new_city)
        try:
            city = City.objects.get(name = new_city)
            err_msg = 'City already exists!'
        except ObjectDoesNotExist:
            form = CityForm(request.POST)
            req = requests.get(url.format(new_city)).json()
            if req['cod'] == 200:
                form.save()
            else:
                err_msg = 'City doesn\'t exist in the world!'
        if err_msg:
            message = err_msg
            message_class = 'is-danger'
        else:
            message = 'City added successfully!'
            message_class = 'is-success'
    static_city = City()
    static_city.name = data['city']            
    form = CityForm()
    cities = list(City.objects.all())
    # print(cities)
    # cities = list(cities)
    # print(cities)
    cities.insert(0, static_city)
    weather_data = []
    for city in cities:
        city_weather = requests.get(url.format(city.name)).json()
        weather = {
            'city': city.name,
            'temperature': city_weather['main']['temp'],
            'description': city_weather['weather'][0]['description'],
            'icon': city_weather['weather'][0]['icon']
        }
        weather_data.append(weather)
    context = {'weather_data': weather_data, 'form': form, 'message': message, 'message_class': message_class}
    return render(request, 'weather_app/index.html', context)


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')