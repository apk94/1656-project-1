import argparse
import collections
import csv
import json
import glob
import math
import os
import pandas
import re
import requests
import string
import sys
import time
import xml
import ssl

class Bike():
    def __init__(self, baseURL, station_info, station_status):
        self.baseURL = baseURL 
        self.station_info = station_info
        self.station_status = station_status
        # initialize the instance
        pass

    def total_bikes(self):
        response = requests.get(self.baseURL + '/' + self.station_status)
        data = response.json()
        total = 0 
        for station in data['data']['stations']:
            total += station['num_bikes_available'] 
        
        return total 
        
    def total_docks(self):
        response = requests.get(self.baseURL + '/' + self.station_status)
        data = response.json()
        total = 0 
        for station in data['data']['stations']:
            total += station['num_docks_available'] 
        
        return total 
        # return the total number of docks available

    def percent_avail(self, station_id):
        response = requests.get(self.baseURL + '/' + self.station_status)
        data = response.json()
        total = 0 
        for station in data['data']['stations']:
            if str(station['station_id']) == str(station_id): 
                bikes = station['num_bikes_available']
                docks = station['num_docks_available']
                total = bikes + docks 
                if total == 0: 
                    return "0%"
                percentage = math.floor((docks/total)*100)
                return f"{percentage}%"

        return ""

    def closest_stations(self, latitude, longitude):
        response = requests.get(self.baseURL + '/' + self.station_info)
        data = response.json()

        stations_distance = []
        for station in data['data']['stations']:
            distance = self.distance(latitude, longitude, station['lat'], station['lon'])
            stations_distance.append({
                'station_id' : str(station['station_id']), 
                'name' : station['name'],
                'distance' : distance
            })

        n = len(stations_distance)
        for i in range(n) : 
            for j in range(0, n-i-1):
                if stations_distance[j]['distance'] > stations_distance[j+1]['distance']:
                    stations_distance[j], stations_distance[j+1] = stations_distance[j+1], stations_distance[j]
       
        closest_stations = {}
        count = 0
        for station in stations_distance: 
            if count < 3: 
                closest_stations[station['station_id']] = station['name']
                count += 1
        return closest_stations
       

    def closest_bike(self, latitude, longitude):
        info_response = requests.get(self.baseURL + '/' + self.station_info)
        info_data = info_response.json()
        status_response = requests.get(self.baseURL + '/' + self.station_status)
        status_data = status_response.json()
        
        bikes_map = {}
        for station in status_data['data']['stations']:
            bikes_map[str(station['station_id'])] = station['num_bikes_available']

        stations_bikes = []
        for station in info_data['data']['stations']:
            station_id = str(station['station_id'])
            if station_id in bikes_map and bikes_map[station_id] > 0 :
                 distance = self.distance(latitude, longitude, station['lat'], station['lon'])
                 stations_bikes.append({
                     'station_id' : str(station['station_id']), 
                     'name' : station['name'],
                     'distance' : distance
                }) 
        n = len(stations_bikes)
        for i in range(n): 
            for j in range(0, n-i-1):
                if stations_bikes[j]['distance'] > stations_bikes[j+1]['distance']:
                    stations_bikes[j], stations_bikes[j+1] = stations_bikes[j+1], stations_bikes[j]
        if len(stations_bikes) > 0: 
            closest = stations_bikes[0]
            return {closest['station_id']: closest['name']}
        else: 
            return {}
    
        
    def station_bike_avail(self, latitude, longitude):
        info_response = requests.get(self.baseURL + '/' + self.station_info)
        info_data = info_response.json()
        status_response = requests.get(self.baseURL + '/' + self.station_status)
        status_data = status_response.json()
        
        station_id = None
        for station in info_data['data']['stations']:
            if station['lat'] == latitude and station['lon'] == longitude: 
                station_id = str(station['station_id'])
                break
        if station_id !=None:
            for station in status_data['data']['stations']: 
                if str(station['station_id']) == station_id: 
                    bikes_available = station['num_bikes_available']
                    return {station_id : bikes_available}
        return {}
        
        

    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))


# testing and debugging the Bike class

if __name__ == '__main__':
    instance = Bike('http://labrinidis.cs.pitt.edu/cs1656/data', 'station_information.json', 'station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342885) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(40.445834, -79.954707) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)

