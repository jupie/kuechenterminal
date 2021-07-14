import json
import urllib.request
import time
from datetime import datetime
from string import Template
from threading import Thread

import cherrypy
import feedparser


def form_trainstation_string(trainnumber, destination, departure, delay, isCancelled):
    if isCancelled != 0:
        delay = 'A'
    trainnumber = (trainnumber[:4]) if len(trainnumber) > 4 else trainnumber
    return '<tr><td>{trainnumber}</td><td>{destination}</td><td>{departure}</td><td>+{delay}</td></tr>'.format(
        trainnumber=trainnumber, destination=destination, departure=departure, delay=delay)


def find_extreme_temperature(day):
    temperature_min = 999.0
    temperature_max = 0.0
    for hourly in day:
        temp = round(hourly['main']['temp'] - 273.15, 2)
        if temp > temperature_max:
            temperature_max = temp
        if temp < temperature_min:
            temperature_min = temp
    return temperature_min, temperature_max


def get_tagesschau_first():
    url = "https://www.tagesschau.de/xml/rss2_https/"
    feed = feedparser.parse(url)
    return feed.entries[0].title


def trainstation_info(station):
    trainstation_string = ''
    with urllib.request.urlopen(
            'https://dbf.finalrewind.org/{station}?mode=json&limit=10'.format(station=station)) as response:
        station_json = json.loads(response.read())
        for train in station_json["departures"]:
            train_string = form_trainstation_string(trainnumber=train['train'], destination=train['destination'],
                                                    departure=train['scheduledDeparture'],
                                                    delay=train['delayDeparture'], isCancelled=train['isCancelled'])
            trainstation_string = trainstation_string + train_string
    if train_string == '':
        train_string = 'Serverfehler'
    return trainstation_string


def parse_forecast_day(data, day, day_of_week):
    days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    day_string = days[day_of_week % 7]
    tempmin, tempmax = find_extreme_temperature(data['list'][day - 3:day + 3])

    mode = data['list'][day]['weather'][0]['main']
    return ' <tr><td> {daystring}</td><td>{max}/{min}°C</td></tr><tr><td>{mode} </td></tr>'.format(daystring=day_string,
                                                                                                   max=tempmax,
                                                                                                   min=tempmin,
                                                                                                   mode=mode)


def parse_forcast(weather_json):
    actual = time.localtime(time.time()).tm_hour
    nextday = (24 - actual + 12) // 4
    next_day_weather = parse_forecast_day(weather_json, nextday, datetime.today().weekday() + 1)
    next_day_weather = next_day_weather + parse_forecast_day(weather_json, nextday + 6,
                                                             datetime.today().weekday() + 2)
    next_day_weather = next_day_weather + parse_forecast_day(weather_json, nextday + 12, datetime.today().weekday() + 3)

    return next_day_weather


def weather_info(apikey, place):
    weather_string = ''
    with urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q={place}&appid={apikey}'.format(
            apikey=apikey, place=place)) as response:
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
        weather_string = '<tr><td>{temperature}°C</td><td>{max}/{min}°C</td></tr><tr><td>Luftfeuchte</td> <td>{humidity}%</td></tr> '.format(
            temperature=temperature, min=tempmin, max=tempmax, humidity=humidity)
        weather_string = weather_string + '<tr><td>{sunrise}</td><td>{sunset}</td></tr>'.format(
            sunrise=sunrise, sunset=sunset)
        weather_string = weather_string + '<tr><td colspan=2 > {mode}</td></tr><tr><td>Luftdruck</td> <td>{pressure}</td>    </tr>'.format(
            mode=mode, pressure=pressure)
        weather_string = weather_string + '\n' + parse_forcast(weather_json)
    return weather_string


class Root(object):
    def __init__(self):
        with open('settings.json') as settingfile:
            settings = json.load(settingfile)
            self.openweatherkey = settings["openweatherkey"]
            self.place = settings["place"]

    @cherrypy.expose
    def index(self):
        content = {'trainstation': trainstation_info(self.place), 'weather': weather_info(self.openweatherkey),
                   'feed': get_tagesschau_first()}
        with open('newview.html') as template_file:
            template = Template(template_file.read())
            out = template.substitute(content)
            return out


class Server(Thread):

    def run(self) -> None:
        cherrypy.quickstart(Root(), '/')


Server().start()
