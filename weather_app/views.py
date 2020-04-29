from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
import requests
from .models import City
from .forms import CityForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import pytz

# Create your views here.
def index(request):
    units = request.session.setdefault('units', 'imperial')
    if request.is_ajax():
        units = request.POST.get('units')
        request.session['units'] = units
    else:
        units = request.session['units']
    res = requests.get('https://ipinfo.io/')
    data = res.json()
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid=b69dbe802588ff579fe043e5ab417eb3'
    location_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCI84giR9sixN9x7TkPA4Iyxt_c5e5PW8A'
    weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units={}&appid=b69dbe802588ff579fe043e5ab417eb3'
    err_msg = ''
    message = ''
    message_class = ''
    if not request.is_ajax() and request.method == 'POST':
        new_city = request.POST.get('name')
        if City.objects.all().count() == 3:
            message = 'Cannot add more than 3 cities manually!'
            message_class = 'is-danger'
        else:
            try:
                city = City.objects.get(name = new_city)
                err_msg = 'City already exists!'
            except ObjectDoesNotExist:
                form = CityForm(request.POST)
                req = requests.get(url.format(new_city, units)).json()
                if req['cod'] == 200:
                    form.save()
                else:
                    err_msg = 'City doesn\'t exist in the world!'
            if err_msg:
                message = err_msg
                message_class = 'is-danger'
            else:
                message = 'City added successfully!'
                message_class = 'is-primary'
    static_city = City()
    static_city.name = data['city']            
    form = CityForm()
    cities = list(City.objects.all())
    cities.insert(0, static_city)
    weather_data = []
    # print(units)
    for city in cities:
        city_latlng = requests.get(location_url.format(city.name)).json()['results'][0]['geometry']['location']
        lat = city_latlng['lat']
        lng = city_latlng['lng']
        city_weather = requests.get(weather_url.format(lat, lng, units)).json()
        weather = {
            'city': city.name,
            'temperature': city_weather['current']['temp'],
            'description': city_weather['current']['weather'][0]['description'],
            'icon': city_weather['current']['weather'][0]['icon'],
            'id': city_weather['current']['weather'][0]['id']
        }
        weather_data.append(weather)
    if units == "imperial":
        unit = "° F"
    else:
        unit = "° C"
    context = {'weather_data': weather_data, 'units': units, 'unit': unit, 'form': form, 'message': message, 'message_class': message_class}
    # print(context)
    if request.is_ajax():
        html = render_to_string('weather_app/index.html', context, request)
        return JsonResponse({'f': html})
    return render(request, 'weather_app/index.html', context)


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')

def detailed_city(request, city_name):
    # units = "imperial"
    location_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCI84giR9sixN9x7TkPA4Iyxt_c5e5PW8A'
    weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units={}&appid=b69dbe802588ff579fe043e5ab417eb3'
    city_latlng = requests.get(location_url.format(city_name)).json()['results'][0]['geometry']['location']
    lat = city_latlng['lat']
    lng = city_latlng['lng']
    if not request.is_ajax():
        units = request.session['units']
    elif request.is_ajax() and request.method == "POST":
        units = request.POST.get('units')
        request.session['units'] = units
    elif request.is_ajax() and request.method == "GET":
        units = request.session['units']
    forecast = requests.get(weather_url.format(lat, lng, units)).json()
    hourly_forecast = forecast['hourly']
    daily_forecast = forecast['daily']
    timezone= pytz.timezone(forecast['timezone'])
    hourly = []
    daily = []
    hd=[]
    lis=[]
    dd=[]
    lis1=[]
    for hour in hourly_forecast[:25]:
        date1 = utc_to_tz(hour['dt'], timezone).strftime("%H:%M")
        hourly_data = {
            'dt': date1,
            'temp': hour['temp'],
            'feels': hour['feels_like'],
            'pressure': hour['pressure'],
            'humidity': hour['humidity'],
            'dew_point': hour['dew_point'],
            'clouds': hour['clouds'],
            'wind_speed': hour['wind_speed'],
            'wind_deg': hour['wind_deg'],
            'des': hour['weather'][0]['description'],
            'icon': hour['weather'][0]['icon']
        }
        hourly.append(hourly_data)
        lis.append([date1,hour['temp'],hour['feels_like'],hour['pressure'],hour['humidity'],hour['dew_point'],hour['clouds'],hour['wind_speed'],hour['wind_deg'],hour['weather'][0]['description']])
        hd.append(lis[-1])
    day = daily_forecast[0]
    dt = utc_to_tz(day['dt'], timezone)
    time = datetime.now(timezone).strftime("%H:%M:%S")
    current = {
        'weekday': dt.strftime("%A"),
        'date': dt.strftime("%B %d, %Y"),
        'temp': day['temp']['day'],
        'feels': day['feels_like']['day'],
        'min': day['temp']['min'],
        'max': day['temp']['max'],
        'dew': day['dew_point'],
        'pressure': day['pressure'],
        'humidity': day['humidity'],
        'rain': day.get('rain', 0.0),
        'wind_speed': day['wind_speed'],
        'wind_dir': day['wind_deg'],
        'clouds': day['clouds'],
        'uvi': day['uvi'],
        'sunrise': utc_to_tz(day['sunrise'], timezone).strftime("%H:%M"),
        'sunset': utc_to_tz(day['sunset'], timezone).strftime("%H:%M"),
        'icon': day['weather'][0]['icon'],
        'description': day['weather'][0]['description']
    }


    for day in daily_forecast[1:]:
        dt = utc_to_tz(day['dt'], timezone)
        sunrise = utc_to_tz(day['sunrise'], timezone).strftime("%H:%M")
        sunset = utc_to_tz(day['sunset'], timezone).strftime("%H:%M")
        daily_data = {
            'weekday': dt.strftime("%a"),
            'date': dt.strftime("%#m/%#d"),
            'min': day['temp']['min'],
            'max': day['temp']['max'],
            'feels': day['feels_like']['day'],
            'sunrise': sunrise,
            'sunset': sunset,
            'icon': day['weather'][0]['icon'],
            'pressure': day['pressure'],
            'humidity': day['humidity'],
            'dew': day['dew_point'],
            'clouds': day['clouds'],
            'wind_speed': day['wind_speed'],
            'wind_dir': day['wind_deg'],
            'description': day['weather'][0]['description']
        }
        daily.append(daily_data)
        lis1.append([dt.strftime("%a"),dt.strftime("%#m/%#d"), sunrise, sunset, day['temp']['min'],day['temp']['max'],day['feels_like']['day'], day['pressure'], day['humidity'], day['dew_point'], day['clouds'], day['wind_speed'],day['wind_deg'],day['weather'][0]['description']])
        dd.append(lis1[-1])
    if units == "imperial":
        unit = "°F"
        speed = "mph"
    else:
        unit = "°C"
        speed = "m/s"
    context = {'city': city_name,'current': current, 'time': time, 'hourly': hourly, 'daily': daily, 'unit': unit, 'units': units, 'speed': speed, 'hd': hd, 'dd': dd, 'activities': activities(city_name), 'precautions': precautions_city(city_name)}
    if request.is_ajax():
        print(request)
        html = render_to_string('weather_app/detail.html', context, request)
        return JsonResponse({'f': html})
    return render(request, 'weather_app/detail.html', context)


def utc_to_tz(time, timezone):
    return pytz.utc.localize(datetime.utcfromtimestamp(time), is_dst=None).astimezone(timezone)












def avgtemp(tod):
    avg_temp = 0
    c_temp = 0
    for ele in tod:
        avg_temp = avg_temp+ele["temp"]
        c_temp+=1
    if c_temp == 0:
        return 0
    else:
        avg_temp_final = avg_temp/c_temp
        return avg_temp_final

def activities_city(tod):
    s=[]
    count=0
    avg=tod[-1]#Average temperature logic
    tod.pop()
    dic1={}
    # print("Average temperature "+str(round(avg,2))+"° F")

    if(avg<=45):
        s10="-> Open a bottle of wine and keep yourself warm."
        if(tod[0]['time']!='night'):
            s11="-> Jump on a trampoline and build some heat up."
            s12="-> Get a hot chocolate and go for a stroll around your town."
            s.append(s11)
            s.append(s12)
        else:
            s13="-> Make a backyard bonfire."
            s.append(s13)
    elif((avg>45 and avg<=75)):
        if(tod[0]['time']!='night'):
            s14="-> You could get a warm wetsuit and take a lesson in surfing."
            s15="-> Feeling wild? Travel somewhere hot and swim in the ocean."
            s16="-> Perfect weather to go biking or a rent a bike and explore your city."
            s17="-> Lace up your sneakers and go for a sun."
            s18="-> Go birdwatching."
            s19="-> Find an outdoor pull up bar and practice your pullups."
            s20="-> Go apple or berry picking."
            s21="-> Go camping. Toss a frisbee."
            s22="-> Plan a last-minute road trip."
            s23="-> Collect seashells at the beach."
            s24="-> Nap in a hammock or sit in a porch swing."
            s.extend([s14,s15,s16,s17,s18,s19,s20,s21,s22,s23,s24])
        else:
            s25="-> Stargaze while lying on grass."
            s.append(s25)

    else:
        if(tod[0]['time']!='night'):
            s26="-> Host a barbecue party."
            s27="-> Make a pitcher or Sangria."
            s28="-> Pooly party, of course! Blow bubbles and play water balloon baseball."
            s29="-> Have lots of ice cream!"
            s30="-> A slice of watermelon is just as good if you're too lazy to make slushes or snowcones."
            s31="-> Grown a kitchen herb garden."
            s32="-> Bake a fruit pie from scratch and eat it all!"
            s.extend([s26,s27,s28,s29,s30,s31,s32])

    for ele in tod:
        if((ele['main']=='Rain' or ele['main']=='Drizzle') and ele['time'] !='night'):
            count=2
        elif(ele['main']=='Thunderstorm'):
            count=3
            break
        elif(ele['main']=='Snow' and ele['time'] !='night'):
            count=4
            break

    if(count==2):   ####Rain or drizzle
        s6="-> Two words, beach volleyball."
        s7="-> If you can't get to the beach, football in the rain is the next best thing."
        s8="-> Also, jump around in mud puddles."
        s9="-> You could also sit at your windown and watch the rain while sipping on hot tea."
        s.extend([s6,s7,s8,s9])

    elif(count==3):   ####Thunderstorm
        s1 = "-> You can't step out in the thunderstorm but you can always kick back and read a good book while sipping on hot cocoa."
        s2= "-> We bet it's been quite sometime that you played a board game. Beat some dust off those old favourites, get together. "+"Beat some dust off those old favourites, get together to have some fun while you're still indoors."
        s.append(s1)
        s.append(s2)
    elif(count==4): ####Snow
        s3 = "-> Put on your winter clothes and make a snownman or have a snowball fight."
        s4="-> May be you should try skiing. Try not to hurt yourself."
        s5="-> Ice fishing sounds like the coolest thing to us. We suggest you try your hand at it."
        s.extend([s3,s4,s5])


    #s="\t"+"Morning"
    if(tod[0]['time']=='morning'):
        s40="Morning (06:00-12:00 Local time)"
    elif(tod[0]['time']=='afternoon'):
        s40="Afternoon (12:00-16:00 Local time)"
    elif(tod[0]['time']=='evening'):
        s40="Evening (16:00-20:00 Local time)"
    else:
        s40="Night (20:00-06:00 Local time)"
    #print(s)
    dic1 = {
        's40': s40,
        's': s
    }
    return dic1

def activities(city_name):
    location_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCI84giR9sixN9x7TkPA4Iyxt_c5e5PW8A'
    weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=imperial&appid=25abf37eaf95927fc1dc79357ef3df0c'
    city_latlng = requests.get(location_url.format(city_name)).json()['results'][0]['geometry']['location']
    lat = city_latlng['lat']
    lng = city_latlng['lng']
    forecast = requests.get(weather_url.format(lat, lng)).json()
    hourly_forecast = forecast['hourly']
    #daily_forecast = forecast['daily']
    timezone= pytz.timezone(forecast['timezone'])
    #print(timezone)
    hourly = []
    daily = []
    dict_morning={}
    morning=[]
    dict_an={}
    an=[]
    dict_eve={}
    eve=[]
    dict_night={}
    night=[]
    c=0
    for hour in hourly_forecast[:12]:


        hourly_data = {
            'dt': utc_to_tz(hour['dt'], timezone).strftime("%H:%M"),
            'temp': hour['temp'],
            'humidity': hour['humidity'],
            'wind_speed': hour['wind_speed'],
            'main': hour['weather'][0]['main'],
            'desc': hour['weather'][0]['description']
        }
        #print(type(hourly_data["dt"]))


        x=int(hourly_data["dt"].split(":")[0])

        #print(x)
        if(x>=6 and x<=11):
            if(c==0):
                x1=1
                c+=1
            hourly_data['time']="morning"
            morning.append(hourly_data)
        elif(x>=12 and x<=15):
            if(c==0):
                x1=2
                c+=1
            hourly_data['time']="afternoon"
            an.append(hourly_data)

        elif(x>=16 and x<=19):
            if(c==0):
                x1=3
                c+=1
            hourly_data['time']="evening"
            eve.append(hourly_data)

        else:
            if(c==0):
                x1=4
                c+=1
            hourly_data['time']="night"
            night.append(hourly_data)
        #print(hourly_data["time"])
        #hourly.append(hourly_data)
    #print(morning)
    #print(an)
    #print(eve)
    #print(night)
        #print(n)
    if(len(morning)):
        m=avgtemp(morning)
        morning.append(m)
        #print(m)
    if(len(an)):
        a=avgtemp(an)
        an.append(a)
        #print(a)
    if(len(eve)):
        e=avgtemp(eve)
        eve.append(e)
        #print(e)
    if(len(night)):
        n=avgtemp(night)
        night.append(n)
        #print(n)

    s1=''
    s2=''
    s3=''
    s4=''
    activities_city_arr=[]
    if(x1==1):
        if(len(morning)):
            s1=activities_city(morning)
            s1['image']='https://i.pinimg.com/474x/0c/eb/7a/0ceb7a8ca0366388510b8b62db103d94.jpg'
            activities_city_arr.append(s1)
        if(len(an)):
            s2=activities_city(an)
            s2['image']='https://upload.wikimedia.org/wikipedia/commons/0/09/A_good_afternoon_%286933189752%29.jpg'
            activities_city_arr.append(s2)
        if(len(eve)):
            s3=activities_city(eve)
            s3['image']='https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80'
            activities_city_arr.append(s3)
        if(len(night)):
            s4=activities_city(night)
            s4['image']='https://images.unsplash.com/photo-1489549132488-d00b7eee80f1?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
            activities_city_arr.append(s4)

    elif(x1==2):

        if(len(an)):
            s1=activities_city(an)
            s1['image']='https://upload.wikimedia.org/wikipedia/commons/0/09/A_good_afternoon_%286933189752%29.jpg'
            activities_city_arr.append(s1)
        if(len(eve)):
            s2=activities_city(eve)
            s2['image']='https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80'
            activities_city_arr.append(s2)
        if(len(night)):
            s3=activities_city(night)
            s3['image']='https://images.unsplash.com/photo-1489549132488-d00b7eee80f1?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
            activities_city_arr.append(s3)
        if(len(morning)):
            s4=activities_city(morning)
            s4['image']='https://i.pinimg.com/474x/0c/eb/7a/0ceb7a8ca0366388510b8b62db103d94.jpg'
            activities_city_arr.append(s4)
    elif(x1==3):

        if(len(eve)):
            s1=activities_city(eve)
            s1['image']='https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80'
            activities_city_arr.append(s1)
        if(len(night)):
            s2=activities_city(night)
            s2['image']='https://images.unsplash.com/photo-1489549132488-d00b7eee80f1?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
            activities_city_arr.append(s2)
        if(len(morning)):
            s3=activities_city(morning)
            s3['image']='https://i.pinimg.com/474x/0c/eb/7a/0ceb7a8ca0366388510b8b62db103d94.jpg'
            activities_city_arr.append(s3)
        if(len(an)):
            s4=activities_city(an)
            s4['image']='https://upload.wikimedia.org/wikipedia/commons/0/09/A_good_afternoon_%286933189752%29.jpg'
            activities_city_arr.append(s4)
    else:
        if(len(night)):
            s1=activities_city(night)
            s1['image']='https://images.unsplash.com/photo-1489549132488-d00b7eee80f1?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
            activities_city_arr.append(s1)
        if(len(morning)):
            s2=activities_city(morning)
            s2['image']='https://i.pinimg.com/474x/0c/eb/7a/0ceb7a8ca0366388510b8b62db103d94.jpg'
            activities_city_arr.append(s2)
        if(len(an)):
            s3=activities_city(an)
            s3['image']='https://upload.wikimedia.org/wikipedia/commons/0/09/A_good_afternoon_%286933189752%29.jpg'
            activities_city_arr.append(s3)
        if(len(eve)):
            s4=activities_city(eve)
            s4['image']='https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80'
            activities_city_arr.append(s4)
    #print(activities_city_arr)
    #images=['https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80', 'https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80', 'https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80','https://images.unsplash.com/photo-1495567720989-cebdbdd97913?ixlib=rb-1.2.1&auto=format&fit=crop&w=2250&q=80']
    # context = {'city': city_name,'activities':activities_city_arr}

    # return render(request, 'weather_app/activities.html', context)
    return activities_city_arr

















#PRECAUTIONS


def avgwindspeed(tod):
    #print(tod)
    avg_temp = 0
    c_temp = 0
    for ele in tod:
        #print(ele["wind_speed"])
        #print(type(ele["wind_speed"]))
        avg_temp = avg_temp+ele["wind_speed"]
        c_temp+=1
    if c_temp == 0:
        return 0
    else:
        avg_temp_final = avg_temp/c_temp
        return avg_temp_final

def precautions(tod):
    s=[]

    avg=tod[-1]#Average temperature logic
    tod.pop()
    avgwindspeed=tod[-1]
    tod.pop()
    dic1={}
    s1="-> Average temperature "+str(round(avg,2))+"° F"


    if(avg<=45):
        s2="-> Based on the average temperature estimate, a very cold weather is expected. Please wear a jacket to keep yourself warm when stepping out."
    elif(avg>45 and avg<=60):
        s2="-> Based on the average temperature estimate, a slightly cool weather is expected."
    elif(avg>60 and avg<=75):
        s2="-> Based on the average temperature estimate, a warm weather is expected. Take a bottle of water or juice to keep yourself hydrated when stepping out."
    else:
        s2="-> Based on the average temperature estimate, a very hot weather is expected. Take a bottle of water or juice to keep yourself hydrated when stepping out."

    #s=s1+s2
    s6="-> Average wind speed "+str(round(avgwindspeed,2))+" miles per hour."
    s.extend([s1,s6,s2])

    count=0
    #s3=''
    if(tod[0]['time']=='morning' or tod[0]['time']=='afternoon'):

        for ele in tod:
            if((ele['main']=='Clear') or (ele['main']=='Clouds' and (ele['desc']=='scattered clouds' or ele['desc']=='few clouds' ))):
                count=1
                break
        #print(count)
        if(count==1 and avg>68):
            s30="-> The skies are relatively clear."
            s31="-> Slip on some sun-protective clothing that covers as much skin as possible."
            s32="-> Slop on broad-spectrum, water-resistant sunscreen it will protect you against different forms of UV rays (UVA, UVB and UVC)."
            s33="-> Slap on a hat which is broad-brimmed or legionnaire-style to protect your face, head, neck and ears."
            s34="-> Seek some shade."
            s35="-> Slide on some sunglasses."
            s36="-> Don't forget to water your plants."
            s.extend([s30,s31,s32,s33,s34,s35,s36])



    if(avgwindspeed>=1 and avgwindspeed<=3):
        s4 = "-> Light air is expected."
    elif(avgwindspeed>3 and avgwindspeed<=7):
        s4 = "-> Light breeze is expected."
    elif(avgwindspeed>7 and avgwindspeed<=12):
        s4 = "-> Gentle breeze is expected."
    elif(avgwindspeed>12 and avgwindspeed<=24):
        s4 = "-> Moderate breeze is expected."
    elif(avgwindspeed>24 and avgwindspeed<=31):
        s4 = "-> Strong breeze is expected. Large branches sway and umbrellas are difficult to carry."
    elif(avgwindspeed>31 and avgwindspeed<=38):
        s4 = "-> Strong winds are expected. Whole trees sway and it can be difficult to walk against wind. Stay indoors to avoid the harsh winds."
    else:
        s4 = "-> Strong winds are expected. Be safe and stay indoors to protect yourself from the harsh winds."

    s.append(s4)

    for ele in tod:
        if((ele['main']=='Rain' or ele['main']=='Drizzle')):
            count=2
        elif(ele['main']=='Thunderstorm'):
            count=3
            break
        elif(ele['main']=='Snow'):
            count=4
            break

    #s5=''
    if(count==2):
        s5 = "-> Rain is expected. Make sure to take an umbrella or a wear a raincoat when you're stepping out."
        s.append(s5)
    elif(count==3):
        s5 = "-> Thunderstorm is expected. Stay indoors to avoid the thunderstorm. If you have plant pots outside, bring them inside."
        s19="-> Take care of your pets and keep them at home."
        s.extend([s5,s19])
    elif(count==4):
        s5 = "-> Snow is expected. Avoid driving in snow if possible."
        s20="-> Wear gloves, boots and a jacket when stepping out."
        s.extend([s5,s20])

    #s="\t"+"Morning"
    if(tod[0]['time']=='morning'):
        s10="Morning (06:00-12:00 Local time)"
    elif(tod[0]['time']=='afternoon'):
        s10="Afternoon (12:00-16:00 Local time)"
    elif(tod[0]['time']=='evening'):
        s10="Evening (16:00-20:00 Local time)"
    else:
        s10="Night (20:00-06:00 Local time)"
    #print(s)
    dic1 = {
        's10': s10,
        's': s

    }
    '''
    if(len(s3)==0):
        del dic1[s3]
    if(len(s5)==0):
        del dic1[s5]
    '''
    return dic1




def precautions_city(city_name):
    location_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCI84giR9sixN9x7TkPA4Iyxt_c5e5PW8A'
    weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=imperial&appid=25abf37eaf95927fc1dc79357ef3df0c'
    city_latlng = requests.get(location_url.format(city_name)).json()['results'][0]['geometry']['location']
    lat = city_latlng['lat']
    lng = city_latlng['lng']
    forecast = requests.get(weather_url.format(lat, lng)).json()
    hourly_forecast = forecast['hourly']
    #daily_forecast = forecast['daily']
    timezone= pytz.timezone(forecast['timezone'])
    #print(timezone)
    hourly = []
    daily = []
    dict_morning={}
    morning=[]
    dict_an={}
    an=[]
    dict_eve={}
    eve=[]
    dict_night={}
    night=[]
    c=0
    for hour in hourly_forecast[:12]:


        hourly_data = {
            'dt': utc_to_tz(hour['dt'], timezone).strftime("%H:%M"),
            'temp': hour['temp'],
            'humidity': hour['humidity'],
            'wind_speed': hour['wind_speed'],
            'main': hour['weather'][0]['main'],
            'desc': hour['weather'][0]['description']
        }
        #print(type(hourly_data["dt"]))


        x=int(hourly_data["dt"].split(":")[0])

        #print(x)
        if(x>=6 and x<=11):
            if(c==0):
                x1=1
                c+=1
            hourly_data['time']="morning"
            morning.append(hourly_data)
        elif(x>=12 and x<=15):
            if(c==0):
                x1=2
                c+=1
            hourly_data['time']="afternoon"
            an.append(hourly_data)

        elif(x>=16 and x<=19):
            if(c==0):
                x1=3
                c+=1
            hourly_data['time']="evening"
            eve.append(hourly_data)

        else:
            if(c==0):
                x1=4
                c+=1
            hourly_data['time']="night"
            night.append(hourly_data)
        #print(hourly_data["time"])
        #hourly.append(hourly_data)
    #print(morning)
    #print(an)
    #print(eve)
    #print(night)

    if(len(morning)):
        w=avgwindspeed(morning)
        m=avgtemp(morning)
        morning.append(w)
        morning.append(m)
        #print(m)
    if(len(an)):
        w=avgwindspeed(an)
        a=avgtemp(an)
        an.append(w)
        an.append(a)
        #print(a)
    if(len(eve)):
        w=avgwindspeed(eve)
        e=avgtemp(eve)
        eve.append(w)
        eve.append(e)
        #print(e)
    if(len(night)):
        w=avgwindspeed(night)
        n=avgtemp(night)
        night.append(w)
        night.append(n)
        #print(n)

    s1=''
    s2=''
    s3=''
    s4=''
    precautions_arr=[]
    if(x1==1):
        if(len(morning)):
            s1=precautions(morning)
            precautions_arr.append(s1)
        if(len(an)):
            s2=precautions(an)
            precautions_arr.append(s2)
        if(len(eve)):
            s3=precautions(eve)
            precautions_arr.append(s3)
        if(len(night)):
            s4=precautions(night)
            precautions_arr.append(s4)

    elif(x1==2):

        if(len(an)):
            s1=precautions(an)
            precautions_arr.append(s1)
        if(len(eve)):
            s2=precautions(eve)
            precautions_arr.append(s2)
        if(len(night)):
            s3=precautions(night)
            precautions_arr.append(s3)
        if(len(morning)):
            s4=precautions(morning)
            precautions_arr.append(s4)
    elif(x1==3):

        if(len(eve)):
            s1=precautions(eve)
            precautions_arr.append(s1)
        if(len(night)):
            s2=precautions(night)
            precautions_arr.append(s2)
        if(len(morning)):
            s3=precautions(morning)
            precautions_arr.append(s3)
        if(len(an)):
            s4=precautions(an)
            precautions_arr.append(s4)
    else:
        if(len(night)):
            s1=precautions(night)
            precautions_arr.append(s1)
        if(len(morning)):
            s2=precautions(morning)
            precautions_arr.append(s2)
        if(len(an)):
            s3=precautions(an)
            precautions_arr.append(s3)
        if(len(eve)):
            s4=precautions(eve)
            precautions_arr.append(s4)
    # print(precautions_arr)

    # context = {'city': city_name,'precautions':precautions_arr}

    # return render(request, 'weather_app/precautions.html', context)
    return precautions_arr


    '''
    for day in daily_forecast[1:]:
        time = utc_to_tz(day['dt'], timezone)
        daily_data = {
            'weekday': time.strftime("%a"),
            'date': time.strftime("%#m/%#d"),
            'min': day['temp']['min'],
            'max': day['temp']['max'],
            'feels': day['feels_like']['day'],
            'sunrise': utc_to_tz(day['sunrise'], timezone).strftime("%H:%M"),
            'sunset': utc_to_tz(day['sunset'], timezone).strftime("%H:%M"),
            'icon': day['weather'][0]['icon']
        }
        daily.append(daily_data)
    '''

    #print(daily)

    '''
    context = {'city': city_name,'hourly': hourly, 'daily': daily}
    return render(request, 'weather_app/detail.html', context)
    '''

#detailed_city("Raleigh")