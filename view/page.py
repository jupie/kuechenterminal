import json
import urllib.request
import time
from datetime import datetime
from string import Template
from threading import Thread

import cherrypy


def form_trainstation_string(trainnumber, destination, departure, delay, isCancelled):
    if isCancelled != 0:
        destination = destination + '- Ausfall der Fahrt'
    return '<tr><td>{trainnumber}</td><td>{destination}</td><td>{departure}</td><td>+{delay}</td></tr>'.format(
        trainnumber=trainnumber, destination=destination, departure=departure, delay=delay)


def trainstation_info():
    trainstation_string = ''
    with urllib.request.urlopen('https://dbf.finalrewind.org/FRA?mode=json&limit=10') as response:
        station_json = json.loads(response.read())
        for train in station_json["departures"]:
            train_string = form_trainstation_string(trainnumber=train['train'], destination=train['destination'],
                                                    departure=train['scheduledDeparture'],
                                                    delay=train['delayDeparture'], isCancelled=train['isCancelled'])
            trainstation_string = trainstation_string + train_string
    if train_string == '':
        train_string = 'Serverfehler'
    return trainstation_string


def parse_forecast_day(day, day_of_week):
    days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    day_string = days[day_of_week % 6]
    tempmin = round(day['main']['temp_min'] - 273.15, 2)
    tempmax = round(day['main']['temp_max'] - 273.15, 2)
    mode = day['weather'][0]['main']
    return ' <tr><td> {daystring}</td><td>{max}/{min}°C</td><td>{mode} </td></tr>'.format(daystring=day_string,
                                                                                          max=tempmax, min=tempmin,
                                                                                          mode=mode)


def parse_forcast(weather_json):
    actual = time.localtime(time.time()).tm_hour
    nextday = (24 - actual + 12) // 4
    table = '<table width220> {content}</table>'
    next_day_weather = parse_forecast_day(weather_json['list'][nextday], datetime.today().weekday() + 1)
    next_day_weather = next_day_weather + parse_forecast_day(weather_json['list'][nextday + 6],
                                                             datetime.today().weekday() + 1)
    next_day_weather = next_day_weather + parse_forecast_day(weather_json['list'][nextday + 6],
                                                             datetime.today().weekday() + 2)

    return next_day_weather


def weather_info(apikey):
    weather_string = ''
    with urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q=Raunheim&appid={apikey}'.format(
            apikey=apikey)) as response:
        weather_json = json.loads(response.read())
        sunrise = time.strftime(" %H:%M", time.localtime(weather_json['city']['sunrise']))
        sunset = time.strftime(" %H:%M", time.localtime(weather_json['city']['sunset']))
        temperature = round(weather_json['list'][0]['main']['temp'] - 273.15, 2)
        tempmin = round(weather_json['list'][0]['main']['temp_min'] - 273.15, 2)
        tempmax = round(weather_json['list'][0]['main']['temp_max'] - 273.15, 2)
        humidity = weather_json['list'][0]['main']['humidity']
        pressure = weather_json['list'][0]['main']['pressure']
        clouds = weather_json['list'][0]['clouds']['all']
        mode = weather_json['list'][0]['weather'][0]['main']
        weather_string = '<tr><td>{temperature}°C</td><td>{max}/{min}°C</td> <td>{humidity}%</td></tr>'.format(
            temperature=temperature, min=tempmin, max=tempmax, humidity=humidity)
        weather_string = weather_string + '<tr><td>{sunrise}</td><td>{sunset}</td><td>{clouds}%</td>     </tr>'.format(
            sunrise=sunrise, sunset=sunset, clouds=clouds)
        weather_string = weather_string + '<tr><td colspan=2 > {mode}</td> <td>{pressure}</td>    </tr>'.format(
            mode=mode, pressure=pressure)
        weather_string = weather_string + '\n' + parse_forcast(weather_json)
    return weather_string


class Root(object):
    @cherrypy.expose
    def index(self):
        content = {'trainstation': trainstation_info(), 'weather': weather_info('')}
        with open('newview.html') as template_file:
            template = Template(template_file.read())
            out = template.substitute(content)
            return out


class Server(Thread):

    def run(self) -> None:
        cherrypy.quickstart(Root(), '/')

