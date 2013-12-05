import sys


heading = """
      <!DOCTYPE html>
			<html>
 			 <head>
		    <link type="text/css" rel="stylesheet" href="static/css/main.css" />
        <title>Tweet Creep: See where your friends are tweeting!</title>
		    <meta name=\"viewport\" content=\"initial-scale=1.0, user-scalable=no\">
		    <meta charset=\"utf-8\">
		    <style>
		      html, body, #map-canvas {
		        height: 100%;
		        margin: 0px;
		        padding: 0px
		      }
		    </style>
        """

initial_screen = """
        <html>
          <body>
            <div id=\"initial\">
              <img src=\"/static/img/logo.png\" alt=\"Tweet Creep\">\
              <div id=\"instr_text\">Enter a location to start creeping from:<br></br>
              <form action="" method="post">
                <input type=\"text\" name="content"/>
                <div><input type="submit" value="Submit"></div>
              </form>
              <br></br>Example locations:<br></br>
              </div>\
               <div id=\"small_text\">
                  307 University Dr College Station, TX 77801<br></br>
                  Texas A&M University<br></br>
                  77840<br></br>
                  </div>\
            </div>
          </body>
        </html>
        """

initMap = "<script src=\"https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=true\"></script>\
          <script>\
          var map;\
          var geo_lat, geo_long;\
          var info_open = false;\
          var userPositions = new Array();\
          \
          function log(msg) {\
              setTimeout(function() {\
                  throw new Error(msg);\
              }, 0);\
          };\
          \
          function initialize() {\
            var mapOptions = {\
              zoom: 6,\
              mapTypeId: google.maps.MapTypeId.ROADMAP\
          };\
            \
          map = new google.maps.Map(document.getElementById(\'map-canvas\'), mapOptions);"

geoLocate= "if(navigator.geolocation) {\
              navigator.geolocation.getCurrentPosition(function(position) {\
                var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);\
                geo_lat = position.coords.latitude;\
                geo_long = position.coords.longitude;\
                var infowindow = new google.maps.InfoWindow();\
                \
                var marker = new google.maps.Marker({\
                    position: pos,\
                    map: map,\
                    icon : \'http://maps.google.com/mapfiles/ms/icons/flag.png\',\
                    title: \'Your Location\'\
                });\
                \
                var geocoder = new google.maps.Geocoder();\
                var addr = new String();\
                geocoder.geocode({\'latLng\': pos}, function(results, status) {\
                  if (status == google.maps.GeocoderStatus.OK) {\
                    if (results[1]) {\
                      addr = results[0].formatted_address;\
                     \
                      var contentString = \
                        \'<p>\' + addr + \'</p>\'+\
                        \'<p><b>Location found using HTML5.</b></p>\'+\
                        \'<p>Coordinates: \' + pos.toString() + \'</p>\';\
                        \
                      infowindow.setContent(contentString);\
                    }\
                  }\
                });"

nogeoLocate= "var infowindow = new google.maps.InfoWindow();\
                \
                var marker = new google.maps.Marker({\
                    position: pos,\
                    map: map,\
                    icon : \'http://maps.google.com/mapfiles/ms/icons/flag.png\',\
                    title: \'Your Location\'\
                });\
                \
                var contentString;\
                var geocoder = new google.maps.Geocoder();\
                var addr = new String();\
                geocoder.geocode({\'latLng\': pos}, function(results, status) {\
                  if (status == google.maps.GeocoderStatus.OK) {\
                    if (results[1]) {\
                      addr = results[0].formatted_address;\
                     \
                      contentString = \
                        \'<p>\' + addr + \'</p>\'+\
                        \'<p><b>Location given by user.</b></p>\'+\
                        \'<p>Coordinates: \' + pos.toString() + \'</p>\';\
                        \
                      infowindow.setContent(contentString);\
                    }\
                  }\
                });"

placeMarker= "google.maps.event.addListener(marker, \'click\', function() {\
                infowindow.open(map,marker);\
              });\
              \
              map.setCenter(pos);\
              map.setZoom(15);\
            }, function() {\
              handleNoGeolocation(true);\
            });\
          } else {\
            handleNoGeolocation(false);\
          }\
        }"

placeMarker_noGeo= "google.maps.event.addListener(marker, \'click\', function() {\
                if (info_open){\
                  infowindow.close();\
                  info_open = false;\
                }\
                infowindow.setContent(contentString);\
                infowindow.open(map,marker);\
                info_open = true;\
              });\
              \
              google.maps.event.addListener(map, \'click\', function() {\
                if (info_open){\
                    infowindow.close();\
                    info_open = false;\
                  }\
              });\
              \
              map.setCenter(pos);\
              map.setZoom(14);\
              }\
            "

errHandle =  "function handleNoGeolocation(errorFlag) {\
              if (errorFlag) {\
                var content = \'Error: The Geolocation service failed.\';\
              } else {\
                var content = \'Error: Your browser doesn\\'t support geolocation.\';\
              }"

setOptions = "var options = {\
        		    map: map,\
        		    position: new google.maps.LatLng(60, 105),\
        		    content: content\
        		  };"

setInfo = "var infowindow = new google.maps.InfoWindow(options);\
      		  map.setCenter(options.position);\
      		}"

setListen = """google.maps.event.addDomListener(window, \'load\', initialize);\
            </script>"""


