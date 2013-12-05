from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch


import random
import sys
import logging
#from google.appengine.ext.db import Model

import webapp2
import json
import cgi
import tweepy
import requests
import urllib3
import urllib2

import tweet_collector
import page_components

from geopy import geocoders

def delete_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
    # Referenced from: http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order


class tweet_store(db.Model):
  text = db.TextProperty()
  latitude = db.StringProperty()
  longitude = db.StringProperty()
  tweet_info = db.StringProperty()
  timestamp =  db.StringProperty()

colors = [
                'red',
                'green',
                'blue',
                'light_blue',
                'orange',
                'purple',
                'pink',
                'yellow'
            ]

pin_colors = {   "red": 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                "green": 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                "blue": 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                "light_blue": 'http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png',
                "orange": 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
                "purple": 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
                "pink": 'http://maps.google.com/mapfiles/ms/icons/pink-dot.png', 
                "yellow": 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
                }

line_colors = {"red": "#FF0000", "green": "#00CC00", "blue": "#0066FF", "light_blue": "#33CCFF",
                "orange": "#FF6600", "purple": "#6600FF", "pink": "#FF33CC", "yellow": "#FFFF00"
                }

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

def getFirst(myList):
    return myList[0]

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.out.write(page_components.heading)
        self.response.write(page_components.initial_screen)


    def post(self):

#################################################################################################################################
        # Main page
#################################################################################################################################

        
        if cgi.escape(self.request.get('content')):
            location_input = cgi.escape(self.request.get('content'))
            #http://geopy.readthedocs.org/en/release-0.96.2/#module-geopy.geocoders
            try:
                g = geocoders.GoogleV3(domain='maps.googleapis.com', protocol='http', client_id=None, secret_key=None)
                place, (lat, lng) = g.geocode(location_input)
            except:
                logging.error("Geopy failed to geocode. Setting location to Texas A&M.")
                lat = 30.6104
                lng = -96.3441
                failed = True
            '''
            location_input = location_input.replace(" ","+")
            url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + location_input + "&sensor=true"
            response = urlfetch.fetch(url, method=urlfetch.GET)
            json_decoder = json.decoder.JSONDecoder()
            data = json_decoder.decode(response.content)
            #data = json.loads(response.content)
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            '''
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
            users = []
            user_color = {}
            for tweet in all_tweets:
                if tweet.coordinates:
                    users.append(tweet.user.screen_name)
                    
            #         user_color = {user: random.choice(colors) for user in distinct_users}
            #         user_coordinates = {user: str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0]) for user in distinct_users}

            distinct_users = delete_duplicates(users)
            
            if distinct_users != []:
                #user_tweets = tweet_collector.collectUTweets(api, distinct_users[0])
                user_tweets = tweet_collector.collectUTweets(api, distinct_users[0])
                #user_tweets = all_tweets

                for user in distinct_users:
                    user_tweets += tweet_collector.collectUTweets(api, user)

                # all_tweets = tweet_collector.collectTweets(api, lat, lng)

                # user_name = all_tweets[0].user.screen_name
                # user_tweets = tweet_collector.collectUTweets(api, user_name)

                # for tweet in all_tweets:
                #     user_name = str(tweet.user.screen_name)
                #     user_tweets += tweet_collector.collectUTweets(api, user_name)

                distinct_users = []
                x = 0
                userLocations = {}
                users = []
                user_color = {}
                #for tweet in all_tweets:
                for tweet in user_tweets:
                    if tweet.coordinates:
                        users.append(tweet.user.screen_name)
                        distinct_users = delete_duplicates(users)
                        # for user in users:
                        #     if user in user_color:
                        #         user_color[user] = random.choice(colors)                       

                        
                        # user_coordinates = {user: str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0]) for user in distinct_users}

                user_color = {user: random.choice(colors) for user in distinct_users}
                if failed:
                    self.response.out.write("alert(\"Geopy failed to geocode. Setting location to Texas A&M.\");")

                lat_total = 0
                lng_total = 0
                for tweet in user_tweets:
                    if tweet.coordinates:

                        if tweet.user.screen_name in userLocations:
                            userLocations[tweet.user.screen_name].append(x)
                        else:
                            userLocations[tweet.user.screen_name] = [x]
                        lat_total += tweet.coordinates['coordinates'][1]
                        lng_total += tweet.coordinates['coordinates'][0]
                        pinRequest = "\
                            var pinPosition" + str(x) + " = new google.maps.LatLng(" + str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0]) + ");\
                            \
                            var marker" + str(x) + " = new google.maps.Marker({\
                                position: pinPosition" + str(x) + ",\
                                map: map,\
                                icon: \'" + pin_colors[user_color[tweet.user.screen_name]] + "\',\
                                title: \'Tweet " + str(x) + "'\
                            });\
                            \
                            var infowindow" + str(x) + "  = new google.maps.InfoWindow();\
                            var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" + "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p></div>\";\
                            infowindow" + str(x) + ".setContent(content" + str(x) + ");\
                            \
                            google.maps.event.addListener(marker" + str(x) + ", \'click\', function() {\
                                geocoder.geocode({\'latLng\': pinPosition"+str(x)+"}, function(results, status) {\
                                  if (status == google.maps.GeocoderStatus.OK) {\
                                    if (results[0]) {\
                                       var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" +  "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p><p>\" + results[0].formatted_address + \"</p></div>\";\
                                       infowindow.setContent(content" + str(x) + ");\
                                    }\
                                  } else {\
                                    alert(\"Geocoder failed due to: \" + status);\
                                  }\
                                });\
                                \
                                map.setCenter(pinPosition" + str(x) +");\
                                if (info_open){\
                                  infowindow.close();\
                                  info_open = false;\
                                }\
                                infowindow.open(map,marker" + str(x) + ");\
                                info_open = true;\
                            });"
                        self.response.out.write(pinRequest)
                        x += 1

                lat_total /= x
                lng_total /= x

                densityRequest = "\
                            var density = new google.maps.LatLng(" + str(lat_total) + ", " + str(lng_total) + ");\
                            \
                            var markerDensity = new google.maps.Marker({\
                                position: density,\
                                map: map,\
                                icon: \'http://maps.google.com/mapfiles/ms/icons/flag.png\',\
                                title: \'Density'\
                            });\
                            \
                            var infowindowDensity = new google.maps.InfoWindow();\
                            var contentDensity =   \"<div align=center><p><b> Here is the tweet density center</b><\p></div>\";\
                            infowindowDensity.setContent(contentDensity);\
                            \
                            google.maps.event.addListener(markerDensity, \'click\', function() {\
                                geocoder.geocode({\'latLng\': density}, function(results, status) {\
                                  if (status == google.maps.GeocoderStatus.OK) {\
                                    if (results[0]) {\
                                       var contentDensity = \"<div align=center><p><b> Here is the tweet density center</b></p><p>\" + results[0].formatted_address + \"</p></div>\";\
                                       infowindow.setContent(contentDensity);\
                                    }\
                                  } else {\
                                    alert(\"Geocoder failed due to: \" + status);\
                                  }\
                                });\
                                \
                                map.setCenter(density);\
                                if (info_open){\
                                  infowindow.close();\
                                  info_open = false;\
                                }\
                                infowindow.open(map,markerDensity);\
                                info_open = true;\
                            });"
                self.response.out.write(densityRequest)

                #connect all the pins with a blue line
                x = 0
                for user in distinct_users:
                    path = "var " + user + "Path = ["
                    length = len(userLocations[user])
                    for y in range (0,length-1):
                        path += "pinPosition" + str(userLocations[user][y]) + ","
                    path += "pinPosition" + str(userLocations[user][length-1]) + "];\
                            var  "+ user + "flightPath = new google.maps.Polyline({\
                                  path:" + user + "Path,\
                                  strokeColor:\" " + line_colors[user_color[user]] + "\",\
                                  strokeOpacity:0.8,\
                                  strokeWeight:2\
                                });\
                                "+ user + "flightPath.setMap(map);\
                                userPositions[" + str(x) + "] = pinPosition" + str(userLocations[user][length-1]) +";"
                    self.response.out.write(path)
                    x += 1

                body = """
                  </head>
                          <div id="location_form">
                                <form action="" method="post">
                                    Change Location: <input type="text" name="content"/>
                                    <input type="submit" value="Submit">
                                </form>
                          </div>
                    <body>
                      <div id="main_wrap">
                        <div id="sidebar">
                          <figure>
                            <img src="/static/img/logo.png" alt="Tweet Creep">
                          </figure>
                          <div id="instr_text">Enter a friend's twitter handle to start creeping:<br></br></div>

                          <form action="" method="post">
                                  <input type="text" name="user_query"/>
                                  <input type="submit" value="Creep!" />
                          </form>
                          <br></br>
                          <div id="heading">Results:</div>
                                <table id="results_table" align = center>
                                        """
                show_results = ""
                x = 0
                for user in distinct_users:
                    position = "pinPosition" + str(userLocations[user][len(userLocations[user])-1])
                    show_results += "<tr><td><img src=\"" + pin_colors[user_color[user]] + "\" alt = \"marker\"></td><td><button onclick=\"onGo(userPositions[" + str(x) + "])\">" + user + "</button></td></tr>"
                    x += 1
                    tail = "</table>\
                    <script>\
                        function onGo(name){\
                            map.setCenter(name);\
                            map.setZoom(19);\
                        }\
                    </script>\
                            </div>\
                            <div id=\"content\">\
                              <div id=\"map-canvas\"></div>\
                            </div>\
                          </div>\
                        </body>\
                    </html>\
                    "

                #write the end of the page
                self.response.out.write(page_components.placeMarker_noGeo)
                self.response.out.write(page_components.errHandle)
                self.response.out.write(page_components.setOptions)
                self.response.out.write(page_components.setInfo)
                self.response.out.write(page_components.setListen)
                self.response.out.write(body)
                self.response.out.write(show_results)
                self.response.out.write(tail)
            else:#no users were found
                self.response.out.write("")

#################################################################################################################################
        # User search page
#################################################################################################################################

        else:
            user = cgi.escape(self.request.get('user_query'))

            # get keys for Twitter API
            keys = tweet_collector.getKeys()
            # authenticate connection to Twitter API
            auth = tweepy.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])
            auth.set_access_token(keys["access_token_key"], keys["access_token_secret"])
            api = tweepy.API(auth)

            user_tweets = tweet_collector.collectUTweets(api, user)
            
            for tweet in user_tweets:
                if tweet.coordinates:
                    coordinates = str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0])

            self.response.out.write(page_components.heading)
            self.response.out.write(page_components.initMap)
            self.response.out.write("pos = new google.maps.LatLng(" + coordinates + ");")
            self.response.out.write(page_components.nogeoLocate)
            
            x = 0
            userLocations = {}
            users = []
            user_color = {}
            #for tweet in all_tweets:
            for tweet in user_tweets:
                if tweet.coordinates:
                    users.append(tweet.user.screen_name)
                    distinct_users = delete_duplicates(users)
                    # for user in users:
                    #     if user in user_color:
                    #         user_color[user] = random.choice(colors)                       

                    user_color = {user: random.choice(colors) for user in distinct_users}
                    user_coordinates = {user: str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0]) for user in distinct_users}

            for tweet in user_tweets:
                if tweet.coordinates:

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
                            icon: \'" + pin_colors[user_color[tweet.user.screen_name]] + "\',\
                            title: \'Tweet " + str(x) + "'\
                        });\
                        \
                        var infowindow" + str(x) + "  = new google.maps.InfoWindow();\
                        var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" + "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p></div>\";\
                        infowindow" + str(x) + ".setContent(content" + str(x) + ");\
                        \
                        google.maps.event.addListener(marker" + str(x) + ", \'click\', function() {\
                            geocoder.geocode({\'latLng\': pinPosition"+str(x)+"}, function(results, status) {\
                              if (status == google.maps.GeocoderStatus.OK) {\
                                if (results[0]) {\
                                   var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" +  "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p><p>\" + results[0].formatted_address + \"</p></div>\";\
                                   infowindow.setContent(content" + str(x) + ");\
                                }\
                              } else {\
                                alert(\"Geocoder failed due to: \" + status);\
                              }\
                            });\
                            \
                            map.setCenter(pinPosition" + str(x) +");\
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
            x = 0
            for user in distinct_users:
                path = "var " + user + "Path = ["
                length = len(userLocations[user])
                for y in range (0,length-1):
                    path += "pinPosition" + str(userLocations[user][y]) + ","
                path += "pinPosition" + str(userLocations[user][length-1]) + "];\
                        var  "+ user + "flightPath = new google.maps.Polyline({\
                              path:" + user + "Path,\
                              strokeColor:\" " + line_colors[user_color[user]] + "\",\
                              strokeOpacity:0.8,\
                              strokeWeight:2\
                            });\
                            "+ user + "flightPath.setMap(map);\
                            userPositions[" + str(x) + "] = pinPosition" + str(userLocations[user][length-1]) +";"
                self.response.out.write(path)
                x += 1

            '''
            path = "var myTrip = ["
            for y in range (0,x-1):
                path += "pinPosition" + str(y) + ","

            path += "pinPosition" + str(x-1) + "];\
                    var flightPath = new google.maps.Polyline({\
                      path:myTrip,\
                      strokeColor:\'#000000\',\
                      strokeOpacity:0.8,\
                      strokeWeight:2\
                    });\
                    flightPath.setMap(map);"
            self.response.out.write(path)
            '''

            body = """
              </head>
                      <div id="location_form">
                            <form action="" method="post">
                                Change Location: <input type="text" name="content"/>
                                <input type="submit" value="Submit">
                            </form>
                      </div>
                <body>
                  <div id="main_wrap">
                    <div id="sidebar">
                      <figure>
                        <img src="/static/img/logo.png" alt="Tweet Creep">
                      </figure>
                      <div id="instr_text">Enter a friend's twitter handle to start creeping:<br></br></div>

                      <form action="" method="post">
                              <input type="text" name="user_query"/>
                              <input type="submit" value="Creep!" />
                      </form>
                      <br></br>
                      <div id="heading">Results:</div>
                            <table id="results_table" align = center>
                                    """
            show_results = ""
            x = 0
            for user in distinct_users:
                position = "pinPosition" + str(userLocations[user][len(userLocations[user])-1])
                show_results += "<tr><td><img src=\"" + pin_colors[user_color[user]] + "\" alt = \"marker\"></td><td><button onclick=\"onGo(userPositions[" + str(x) + "])\">" + user + "</button></td></tr>"
                x += 1

                tail = "</table>\
                <script>\
                    function onGo(name){\
                        map.setCenter(name);\
                        map.setZoom(19);\
                    }\
                </script>\
                        </div>\
                        <div id=\"content\">\
                          <div id=\"map-canvas\"></div>\
                        </div>\
                      </div>\
                    </body>\
                </html>\
                "

            #write the end of the page
            self.response.out.write(page_components.placeMarker_noGeo)
            self.response.out.write(page_components.errHandle)
            self.response.out.write(page_components.setOptions)
            self.response.out.write(page_components.setInfo)
            self.response.out.write(page_components.setListen)
            self.response.out.write(body)
            self.response.out.write(show_results)
            self.response.out.write(tail)





application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)