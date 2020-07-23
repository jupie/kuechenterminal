import json
import urllib.request
import time


def form_trainstation_string(trainnumber,destination, departure, delay,isCancelled):
    if isCancelled != 0:
        destination = destination +'- Ausfall der Fahrt'
    return '<tr><td>{trainnumber}</td><td>{destination}</td><td>{departure}</td><td>{delay}</td></tr>'.format(trainnumber=trainnumber,destination=destination,departure=departure,delay=delay)

def trainstation_info():
    trainstation_string = ''
    with urllib.request.urlopen('https://dbf.finalrewind.org/FRA?mode=json&limit=10') as response:
        station_json = json.loads(response.read())
        for train in station_json["departures"]:
            train_string  = form_trainstation_string(trainnumber=train['train'], destination=train['destination'], departure=train['scheduledDeparture'],delay=train['delayDeparture'], isCancelled=train['isCancelled'] )
            trainstation_string = trainstation_string + train_string
    if train_string == '':
        train_string = 'Serverfehler'
    return trainstation_string

def parse_forecast_day(day)

def parse_forcast(weather_json):
    actual = time.localtime(time.time()).tm_hour
    day1 = parse_forcast(weather_json['list'][])


def weather_info(apikey):
    weather_string = ''
    with urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q=Raunheim&appid={apikey}'.format(apikey=apikey)) as response:
        weather_json = json.loads(response.read())
        sunrise = time.strftime(" %H:%M", time.localtime(weather_json['city']['sunrise']))
        sunset =  time.strftime(" %H:%M", time.localtime(weather_json['city']['sunset']))
        temperature = round(weather_json['list'][0]['main']['temp']-273.15,2)
        tempmin =  round(weather_json['list'][0]['main']['temp_min']-273.15,2)
        tempmax =  round(weather_json['list'][0]['main']['temp_max']-273.15,2)
        humidity = weather_json['list'][0]['main']['humidity']
        pressure =  weather_json['list'][0]['main']['pressure']
        clouds = weather_json['list'][0]['clouds']['all']
        mode = weather_json['list'][0]['weather'][0]['main']
        weather_string= '<tr><td>{temperature}°C</td><td>{min}/{max}°C</td> <td>{humidity}%</td></tr>'.format(temperature=temperature,min=tempmin,max=tempmax,humidity=humidity)
        weather_string= weather_string+'<tr><td>{sunrise}</td><td>{sunset}</td><td>{clouds}%</td>     </tr>'.format(sunrise=sunrise,sunset=sunset,clouds=clouds)
        weather_string= weather_string+'<tr><td colspan=2 > {mode}</td> <td>{pressure}</td>    </tr>'.format(mode=mode, pressure=pressure)
        parse_forcast(weather_json)
    return weather_string




print(weather_info(api))