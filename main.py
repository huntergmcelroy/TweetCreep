from google.appengine.ext.webapp.util import run_wsgi_app
import random
import sys
import webapp2
import cgi
import tweepy

import tweet_collector
import page_components


#################################################################################################################################
        # Utility functions
#################################################################################################################################


def delete_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
    # Referenced from: http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order

def normalizeText(text):
    newText = text.replace("\""," ")
    newText = newText.replace("\n"," ")
    newText = newText.replace("/*"," ")
    newText = newText.replace("\\"," ")
    newText = newText.replace("*/"," ")
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

        pin_colors = {  "red": 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
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

#################################################################################################################################
        # Main page
#################################################################################################################################
        
        if cgi.escape(self.request.get('result')):
            location_input = cgi.escape(self.request.get('result'))
            failed = False
            
            try:
                location_components = location_input.split("/")
                lat = location_components[0]
                lng = location_components[1]
            except:
                lat = 30.6104
                lng = -96.3441
                failed = True
            
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

            distinct_users = delete_duplicates(users)
            
            if distinct_users != []:
                user_tweets = tweet_collector.collectUserTweets(api, distinct_users[0])

                for user in distinct_users:
                    user_tweets += tweet_collector.collectUserTweets(api, user)

                
                x = 0
                users = []
                distinct_users = []
                user_color = {}
                userLocations = {}
                #for tweet in all_tweets:
                for tweet in user_tweets:
                    if tweet.coordinates:
                        users.append(tweet.user.screen_name)
                        distinct_users = delete_duplicates(users)

                user_color = {user: random.choice(colors) for user in distinct_users}
                if failed:
                    self.response.out.write("alert(\"Failed to geocode. Click Back or Refresh to continue.\");")

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
                            var content" + str(x) + " =   \"<div sty align=center><p><b>" + normalizeText(tweet.text.encode('ascii', errors='ignore')) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" + "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p></div>\";\
                            infowindow" + str(x) + ".setContent(content" + str(x) + ");\
                            \
                            google.maps.event.addListener(marker" + str(x) + ", \'click\', function() {\
                                geocoder.geocode({\'latLng\': pinPosition"+str(x)+"}, function(results, status) {\
                                  if (status == google.maps.GeocoderStatus.OK) {\
                                    if (results[0]) {\
                                       var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text.encode('ascii', errors='ignore')) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" +  "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p><p>\" + results[0].formatted_address + \"</p></div>\";\
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
                                icon: \'http://maps.google.com/mapfiles/kml/pal4/icon47.png\',\
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
                                       var contentDensity = \"<div align=center><p><b>Recommended Location</b></p> <p> This is the center of Tweet activity. </p><p> Head on over to <b>\" + results[0].formatted_address + \"</b> to be where the action is!</p></div>\";\
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

                #connect all the pins with a line
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

                    <body>
                      <div id="main_wrap">
                        <div id="sidebar">

                            <div id="blue_form">
                                <form action="" method="post">
                                    Change Location: <input type="text" name="content"/>
                                    <input type=\"hidden\" name="result" id="result" value="0/0">
                                    <input type="button" value="Submit" onclick="codeAddress(content.value);" id="submit_location">
                                    <input type=\"submit\" name="submit" id="creep" value="Waiting for input..."/>
                                </form>
                          </div>
                          <figure>
                            <img src="/static/img/logo.png" alt="Tweet Creep">
                          </figure>
                          <div id="blue_form">
                          Search by Twitter handle:

                          <form action="" method="post">
                                  <input type="text" name="user_query"/>
                                  <input type="submit" value="Creep!" id="submit"/>
                          </form>
                          </div>
                          <div id="instr_text"><p>Results:</p></div>
                            <div STYLE=" height: 400px; width: 100%; overflow: auto; background-color: #00acee;">
                                <table align=center>
                                        """
                show_results = ""
                x = 0
                for user in distinct_users:
                    position = "pinPosition" + str(userLocations[user][len(userLocations[user])-1])
                    show_results += "<tr><td><img src=\"" + pin_colors[user_color[user]] + "\" alt = \"marker\"></td><td><button id=\"submit\" onclick=\"onGo(userPositions[" + str(x) + "])\">" + user + "</button></td></tr>"
                    x += 1
                tail = """</table>
                    </div>
                    <div id="instr_text"><p>Copyright 2013 <a href="/static/about-us.html" target="_blank">Tweet Creep</a></p></div>
                    <script>
                        function onGo(name){
                            map.setCenter(name);
                            map.setZoom(18);
                        }

                        document.getElementById("creep").style.display = "none";
                         function codeAddress(address) {
                                      var lat;
                                      var lng;
                                      var geocoder = new google.maps.Geocoder();
                                      geocoder.geocode( { 'address': address}, function(results, status) {
                                        if (status == google.maps.GeocoderStatus.OK) {
                                          res = results[0].geometry.location;
                                          lat = results[0].geometry.location.lat();
                                          lng = results[0].geometry.location.lng();
                                          //alert('Success ' + lat + ', ' +lng);
                                          document.getElementById('result').value = lat + "/" + lng
                                          document.getElementById('creep').value = "Creep!"
                                          document.getElementById("creep").style.display = "inline";
                                          document.getElementById("submit_location").style.display = "none";
                                        } else {
                                          document.getElementById('result').value = "0/0"
                                          alert('Geocode was not successful for the following reason: ' + status);
                                        }
                                      });
                        }

                        function stopRKey(evt) { 
                          var evt = (evt) ? evt : ((event) ? event : null); 
                          var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null); 
                          if ((evt.keyCode == 13) && (node.type=="text"))  {return false;} 
                        } 

                        document.onkeypress = stopRKey;
                    </script>


                            </div>
                            <div id="content">
                              <div id="map-canvas"></div>
                            </div>
                          </div>
                        </body>
                    </html>
                    """

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
                self.response.out.write("alert(\"The location you entered is invalid! Click Back or Refresh to continue.\");")

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

            user_tweets = tweet_collector.collectUserTweets(api, user)
            
            coords = False
            if user_tweets:
                for tweet in user_tweets:
                    if tweet.coordinates:
                        coords = True
                        coordinates = str(tweet.coordinates['coordinates'][1]) + ", " + str(tweet.coordinates['coordinates'][0])

                self.response.out.write(page_components.heading)
                self.response.out.write(page_components.initMap)

                #handle a user with geolocation disabled
                if coords:
                    self.response.out.write("pos = new google.maps.LatLng(" + coordinates + ");")
                else:
                    self.response.out.write("alert(\"The user you entered has geolocation disabled! Click Back or Refresh to continue.\");")
                    self.response.out.write("pos = new google.maps.LatLng(" + str(30.626127) + ", " + str(-96.34235419999999)  + ");")

                self.response.out.write(page_components.nogeoLocate)
                
                x = 0
                userLocations = {}
                users = []
                distinct_users = []
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
                            var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text.encode('ascii', errors='ignore')) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" + "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p></div>\";\
                            infowindow" + str(x) + ".setContent(content" + str(x) + ");\
                            \
                            google.maps.event.addListener(marker" + str(x) + ", \'click\', function() {\
                                geocoder.geocode({\'latLng\': pinPosition"+str(x)+"}, function(results, status) {\
                                  if (status == google.maps.GeocoderStatus.OK) {\
                                    if (results[0]) {\
                                       var content" + str(x) + " =   \"<div align=center><p><b>" + normalizeText(tweet.text.encode('ascii', errors='ignore')) + "</b></p>" + "<p><img src=" + tweet.user.profile_image_url + " alt= 'profile_pic' ></p><p>" + tweet.user.name + " (<a href=" +  "http://twitter.com/" + tweet.user.screen_name + " target=" + "_blank" + ">" + tweet.user.screen_name + "</a>)</p><p>" + str(tweet.created_at) + "<\p><p>\" + results[0].formatted_address + \"</p></div>\";\
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

                    <body>
                      <div id="main_wrap">
                        <div id="sidebar">

                            <div id="blue_form">
                                <form action="" method="post">
                                    Change Location: <input type="text" name="content"/>
                                    <input type=\"hidden\" name="result" id="result" value="0/0">
                                    <input type="button" value="Sumbit" onclick="codeAddress(content.value);" id="creep">
                                    <input type=\"submit\" name="submit" id="submit_location" value="Waiting for input..."/>
                                </form>
                              </div>
                          <figure>
                            <img src="/static/img/logo.png" alt="Tweet Creep">
                          </figure>
                          <div id="blue_form">
                          Search by Twitter handle:

                          <form action="" method="post">
                                  <input type="text" name="user_query"/>
                                  <input type="submit" value="Creep!" id="submit"/>
                          </form>
                          </div>
                          <div id="instr_text"><p>Results:</p></div>
                            <div STYLE=" height: 400px; width: 100%; overflow: auto; background-color: #00acee;">
                                <table align=center>
                                        """
                show_results = ""
                x = 0
                for user in distinct_users:
                    position = "pinPosition" + str(userLocations[user][len(userLocations[user])-1])
                    show_results += "<tr><td><img src=\"" + pin_colors[user_color[user]] + "\" alt = \"marker\"></td><td><button id=\"submit\" onclick=\"onGo(userPositions[" + str(x) + "])\">" + user + "</button></td></tr>"
                    x += 1

                tail = """</table>
                    </div>
                    <div id="instr_text"><p>Copyright 2013 <a href="/static/about-us.html" target="_blank">Tweet Creep</a></p></div>
                    <script>
                        function onGo(name){
                            map.setCenter(name);
                            map.setZoom(18);
                        }

                        document.getElementById("creep").style.display = "none";

                         function codeAddress(address) {
                                      var lat;
                                      var lng;
                                      var geocoder = new google.maps.Geocoder();
                                      geocoder.geocode( { 'address': address}, function(results, status) {
                                        if (status == google.maps.GeocoderStatus.OK) {
                                          res = results[0].geometry.location;
                                          lat = results[0].geometry.location.lat();
                                          lng = results[0].geometry.location.lng();
                                          //alert('Success ' + lat + ', ' +lng);
                                          document.getElementById('result').value = lat + "/" + lng
                                          document.getElementById('creep').value = "Creep!"
                                          document.getElementById("creep").style.display = "inline";
                                          document.getElementById("submit_location").style.display = "none";
                                        } else {
                                          document.getElementById('result').value = "0/0"
                                          alert('Geocode was not successful for the following reason: ' + status);
                                        }
                                      });
                            }

                            function stopRKey(evt) { 
                              var evt = (evt) ? evt : ((event) ? event : null); 
                              var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null); 
                              if ((evt.keyCode == 13) && (node.type=="text"))  {return false;} 
                            } 

                            document.onkeypress = stopRKey;
                    </script>


                            </div>
                            <div id="content">
                              <div id="map-canvas"></div>
                            </div>
                          </div>
                        </body>
                    </html>
                    """


                #write the end of the page
                self.response.out.write(page_components.placeMarker_noGeo)
                self.response.out.write(page_components.errHandle)
                self.response.out.write(page_components.setOptions)
                self.response.out.write(page_components.setInfo)
                self.response.out.write(page_components.setListen)
                self.response.out.write(body)
                self.response.out.write(show_results)
                self.response.out.write(tail)
            
            else: #no users were found
                self.response.out.write(page_components.heading)
                self.response.out.write(page_components.initMap)
                self.response.out.write("pos = new google.maps.LatLng(" + str(30.626127) + ", " + str(-96.34235419999999) + ");")
                self.response.out.write(page_components.nogeoLocate)
                self.response.out.write(page_components.placeMarker_noGeo)
                self.response.out.write(page_components.errHandle)
                self.response.out.write(page_components.setOptions)
                self.response.out.write(page_components.setInfo)
                self.response.out.write(page_components.setListen)

                body = """
                  </head>

                    <body>
                      <div id="main_wrap">
                        <div id="sidebar">

                            <div id="blue_form">
                                    <form action="" method="post">
                                        Change Location: <input type="text" name="content"/>
                                        <input type=\"hidden\" name="result" id="result" value="0/0">
                                        <input type="button" value="Submit" onclick="codeAddress(content.value);" id="submit_location">
                                        <input type=\"submit\" name="submit" id="creep" value="Waiting for input..."/>
                                    </form>
                              </div>
                          <figure>
                            <img src="/static/img/logo.png" alt="Tweet Creep">
                          </figure>
                          <div id="blue_form">
                          Search by Twitter handle:

                          <form action="" method="post">
                                  <input type="text" name="user_query"/>
                                  <input type="submit" value="Creep!" id="submit"/>
                          </form>
                          </div>
                          <div id="instr_text"><p>Results:</p></div>
                            <div STYLE=" height: 400px; width: 100%; overflow: auto; background-color: #00acee;">
                                <table align=center>
                                        """
                self.response.out.write(body)

                tail = """</table>
                    </div>
                    <div id="instr_text"><p>Copyright 2013 <a href="/static/about-us.html" target="_blank">Tweet Creep</a></p></div>
                    <script>
                        alert("No user with that Twitter handle exists! Click Back or Refresh to continue.");
                        function onGo(name){
                            map.setCenter(name);
                            map.setZoom(18);
                        }

                        document.getElementById("creep").style.display = "none";

                         function codeAddress(address) {
                                      var lat;
                                      var lng;
                                      var geocoder = new google.maps.Geocoder();
                                      geocoder.geocode( { 'address': address}, function(results, status) {
                                        if (status == google.maps.GeocoderStatus.OK) {
                                          res = results[0].geometry.location;
                                          lat = results[0].geometry.location.lat();
                                          lng = results[0].geometry.location.lng();
                                          //alert('Success ' + lat + ', ' +lng);
                                          document.getElementById('result').value = lat + "/" + lng
                                          document.getElementById('creep').value = "Creep!"
                                          document.getElementById("creep").style.display = "inline";
                                          document.getElementById("submit_location").style.display = "none";
                                        } else {
                                          document.getElementById('result').value = "0/0"
                                          alert('Geocode was not successful for the following reason: ' + status);
                                        }
                                      });
                            }

                            function stopRKey(evt) { 
                              var evt = (evt) ? evt : ((event) ? event : null); 
                              var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null); 
                              if ((evt.keyCode == 13) && (node.type=="text"))  {return false;} 
                            } 

                            document.onkeypress = stopRKey;
                    </script>


                            </div>
                            <div id="content">
                              <div id="map-canvas"></div>
                            </div>
                          </div>
                        </body>
                    </html>
                    """
                self.response.out.write(tail)

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)