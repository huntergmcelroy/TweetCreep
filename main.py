from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

import random
import sys
import logging
#from google.appengine.ext.db import Model

import webapp2
import json
import cgi
import tweepy

import tweet_collector
import page_components

from geopy import geocoders

class tweet_store(db.Model):
  text = db.TextProperty()
  latitude = db.StringProperty()
  longitude = db.StringProperty()
  tweet_info = db.StringProperty()
  timestamp =  db.StringProperty()

pinColors = [   'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                'http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png',
                'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
                'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
                'http://maps.google.com/mapfiles/ms/icons/pink-dot.png', 
                'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png']

def normalizeText(text):
    newText = text.replace("//","--")
    newText = newText.replace("\""," ")
    #newText = newText.replace("\'"," ")
    newText = newText.replace("\n"," ")
    newText = newText.replace("/*"," ")
    newText = newText.replace("\a"," ")
    newText = newText.replace("\b"," ")
    newText = newText.replace("\f"," ")
    newText = newText.replace("\r"," ")
    newText = newText.replace("\t"," ")
    newText = newText.replace("\v"," ")
    return newText

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.out.write(page_components.heading)
        self.response.write(page_components.initial_screen)


    def post(self):
        
        zipCode = cgi.escape(self.request.get('content'))
        g = geocoders.GoogleV3()
        place, (lat, lng) = g.geocode(zipCode)

        self.response.out.write(page_components.heading)
        self.response.out.write(page_components.initMap)
        self.response.out.write("pos = new google.maps.LatLng(" + str(lat) + ", " + str(lng) + ");")
        self.response.out.write(page_components.nogeoLocate)
        
        # get keys for Twitter API
        keys = tweet_collector.getKeys()
        # authenticate connection to Twitter API
        auth = tweepy.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])
        auth.set_access_token(keys["access_token_key"], keys["access_token_secret"])
        api = tweepy.API(auth)

        all_tweets = tweet_collector.collectTweets(api, lat, lng)
        user_tweets = tweet_collector.collectUsers(api, all_tweets)

        x = 0
        userLocations = {}
        users = []
        #for tweet in all_tweets:
        for tweet in user_tweets:
            if tweet.coordinates:

                users.append(tweet.user.screen_name)
                if tweet.user.screen_name in userLocations:
                    userLocations[tweet.user.screen_name].append(x)
                else:
                    userLocations[tweet.user.screen_name] = [x]

                pinRequest = "\
                    var pinPosition" + str(x) + " = new google.maps.LatLng(" + str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0]) + ");\
                    \
                    var marker" + str(x) + " = new google.maps.Marker({\
                        position: pinPosition" + str(x) + ",\
                        map: map,\
                        icon: \'" + pinColors[x % 7] + "\',\
                        title: \'Tweet " + str(x) + "'\
                    });\
                    \
                    var infowindow" + str(x) + "  = new google.maps.InfoWindow();\
                    var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p>" + "<p><a href=" + "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a></p><p>" + str(tweet.created_at) + "<\p></div>\";\
                    infowindow" + str(x) + ".setContent(content" + str(x) + ");\
                    \
                    google.maps.event.addListener(marker" + str(x) + ", \'click\', function() {\
                        geocoder.geocode({\'latLng\': pinPosition"+str(x)+"}, function(results, status) {\
                          if (status == google.maps.GeocoderStatus.OK) {\
                            if (results[0]) {\
                               var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p>" + "<p><a href=" +  "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a></p><p>" + str(tweet.created_at) + "<\p><p>\" + results[0].formatted_address + \"</p></div>\";\
                               infowindow.setContent(content" + str(x) + ");\
                            }\
                          } else {\
                            alert(\"Geocoder failed due to: \" + status);\
                          }\
                        });\
                        \
                        if (info_open){\
                          infowindow.close();\
                          info_open = false;\
                        }\
                        infowindow.open(map,marker" + str(x) + ");\
                        info_open = true;\
                    });"
                self.response.out.write(pinRequest)
                x += 1

        #connect all the pins with a blue line
        for user in users:
            path = "var " + user + "Path = ["
            length = len(userLocations[user])
            for y in range (0,length-1):
                path += "pinPosition" + str(userLocations[user][y]) + ","
            path += "pinPosition" + str(userLocations[user][length-1]) + "];\
                    var  "+ user + "flightPath = new google.maps.Polyline({\
                          path:" + user + "Path,\
                          strokeColor:\"#800000\",\
                          strokeOpacity:0.8,\
                          strokeWeight:2\
                        });\
                        "+ user + "flightPath.setMap(map);"
            self.response.out.write(path)

        '''
        path = "var myTrip = ["
        for y in range (0,x-1):
            path += "pinPosition" + str(y) + ","

        path += "pinPosition" + str(x-1) + "];\
                var flightPath = new google.maps.Polyline({\
                  path:myTrip,\
                  strokeColor:\"#0000FF\",\
                  strokeOpacity:0.8,\
                  strokeWeight:2\
                });\
                flightPath.setMap(map);"
        self.response.out.write(path)
        '''

        #write the end of the page
        self.response.out.write(page_components.placeMarker_noGeo)
        self.response.out.write(page_components.errHandle)
        self.response.out.write(page_components.setOptions)
        self.response.out.write(page_components.setInfo)
        self.response.out.write(page_components.setListen)
        self.response.out.write(page_components.body)


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)