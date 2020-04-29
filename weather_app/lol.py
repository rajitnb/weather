# from django.shortcuts import render, redirect, HttpResponse
import requests
from datetime import datetime
import pytz
# from .models import City
# from .forms import CityForm
# from django.core.exceptions import ObjectDoesNotExist

city = 'Raleigh'
location_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyAm9HEKfrEBvPcLiscvKUKyjMNaBa0Haeg'
weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=imperial&appid=b69dbe802588ff579fe043e5ab417eb3'
# url = "https://maps.googleapis.com/maps/api/geocode/json?"
# res = requests.get(url + 'address=' + city + '&key=' + 'AIzaSyAm9HEKfrEBvPcLiscvKUKyjMNaBa0Haeg')
# print(res.json()['results'][0]['geometry']['location']['lng'])
city_latlng = requests.get(location_url.format(city)).json()['results'][0]['geometry']['location']
lat = city_latlng['lat']
lng = city_latlng['lng']
print(lat, lng)

x = 2
weather = requests.get(weather_url.format(lat, lng)).json()
print(weather['timezone'])
# print(weather['hourly'])
print(weather['daily'])
# print(weather['daily'])
# forecast = {}
# print(len(weather['hourly']))
# for hour in weather['hourly'][:24]:
    # print(hour)
    # print("\n\n")
    # forecast[hour['dt']] = {}
    # forecast[hour['dt']]['temp'] = hour['temp']
    # forecast[hour['dt']]['icon'] = hour['weather'][0]['icon']

# print(len(forecast))
# def lol():
#     forecast = {}
#     print(len(weather['daily']))
#     # print(weather['daily'][0])
#     print("\n\n\n")
#     # print(weather['current'])
#     daily = {}
#     for day in weather['daily'][1:]:
#     # print(day)
#     # print("\n\n\n")
#         print(x)
#         daily[day['dt']] = {}
#         daily[day['dt']]['min'] = day['temp']['min']
#         daily[day['dt']]['max'] = day['temp']['max']
#         daily[day['dt']]['icon'] = day['weather'][0]['icon']
#         daily[day['dt']]['sunrise'] = day['sunrise']
#         daily[day['dt']]['sunset'] = day['sunset']
#     print(daily)


# lol()
# print(daily)
# def utc_to_local(utc_dt):
#     local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
#     return local_tz.normalize(local_dt)

# print(pytz.timezone(weather['timezone']))
timezone = pytz.timezone(weather['timezone'])
# hourly_forecast = weather['hourly']
# print(len(hourly[:24]))
hourly = {}
# print(hourly_forecast[:24])
# for hour in hourly_forecast[:1]:
    # dt = hour['dt']
    # print(dt)
    # print(datetime.utcfromtimestamp(dt))
    # print(utc_to_local(str(dt)))
    # utc_dt = pytz.utc.localize(datetime.utcfromtimestamp(hour['dt']))
    # print(utc_dt)
    # print(hour['dt'])
    # print(datetime.fromtimestamp(hour['dt']))
    # print(datetime.utcfromtimestamp(hour['dt']))
    # timestamp = datetime.utcfromtimestamp(hour['dt'])
    # print(timezone.normalize(utc_dt.astimezone(timezone)))
    # print(pytz.utc.localize(datetime.utcfromtimestamp(hour['dt']), is_dst=None).astimezone(timezone))
    # hey = pytz.utc.localize(datetime.utcfromtimestamp(hour['dt']), is_dst=None).astimezone(timezone)
    # print(hey.strftime("%H:%M"))
    # print(hour)
    # time = str(hour['dt'])
    # hourly[time] = {}
    # hourly[time]['temp'] = hour['temp']
    # hourly[time]['feels'] = hour['feels_like']
    # hourly[time]['icon'] = hour['weather'][0]['icon']

# print(hourly)



# for day in weather['daily']:
#     print(datetime.utcfromtimestamp(day['dt']).strftime("%a"))
#     print(datetime.utcfromtimestamp(day['dt']).strftime("%#m/%#d"))

print(datetime.utcnow())
print(datetime.now(timezone))





# <!-- <div class="section"> -->
#         <!-- <nav class="level is-marginless">
#             <div class="level-left">
#                 <div class="level-item">
#                     <div class="icon is-large has-text-warning home has-background-dark is-pulled-left">
#                         <i class="fas fa-home fa-2x"></i>
#                     </div>
#                 </div>
#             </div>
#             <div class="level-right">
#                 {% if units == 'imperial' %}
#                 <input id="toggle-on" class="toggle toggle-left" name="toggle" value="imperial" type = "radio" checked>
#                 <label for="toggle-on" class="btn is-size-5">° F</label>
#                 <input id="toggle-off" class="toggle toggle-right" name="toggle" value="metric" type="radio">
#                 <label for="toggle-off" class="btn is-size-5">° C</label>
#                 {% else %}
#                 <input id="toggle-on" class="toggle toggle-left" name="toggle" value="imperial" type = "radio">
#                 <label for="toggle-on" class="btn is-size-5">° F</label>
#                 <input id="toggle-off" class="toggle toggle-right" name="toggle" value="metric" type="radio" checked>
#                 <label for="toggle-off" class="btn is-size-5">° C</label>
#                 {% endif %}
#             </div>
#         </nav> -->
#     <!-- </div> -->
#     <!-- <div class="container is-fluid">
#         <div class="icon is-large has-text-warning home has-background-dark is-pulled-left">
#             <i class="fas fa-home fa-2x"></i>
#         </div>
#         <div class="columns is-pulled-right units">
#             <div class="column is-narrow">
#                 {% if units == 'imperial' %}
#                 <input id="toggle-on" class="toggle toggle-left" name="toggle" value="imperial" type = "radio" checked>
#                 <label for="toggle-on" class="btn is-size-5">° F</label>
#                 <input id="toggle-off" class="toggle toggle-right" name="toggle" value="metric" type="radio">
#                 <label for="toggle-off" class="btn is-size-5">° C</label>
#                 {% else %}
#                 <input id="toggle-on" class="toggle toggle-left" name="toggle" value="imperial" type = "radio">
#                 <label for="toggle-on" class="btn is-size-5">° F</label>
#                 <input id="toggle-off" class="toggle toggle-right" name="toggle" value="metric" type="radio" checked>
#                 <label for="toggle-off" class="btn is-size-5">° C</label>
#                 {% endif %}
#             </div>
#         </div>
#     </div> -->

print(ord('°'))