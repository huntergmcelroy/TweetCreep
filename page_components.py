import sys


heading = """
      <!DOCTYPE html>
			<html>
 			 <head>
		    <link type="text/css" rel="stylesheet" href="static/css/main.css" />
        <title>Tweet Creep: See who is tweeting around you!</title>
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
            <div id=\"instr_text\">
              <img src=\"/static/img/logo.png\" alt=\"Tweet Creep\">\
              <div id=\"instr_text\">Enter a location to start creeping from:<br></br>

              <form action="" method="post" onsubmit="">
                <input type="text"   name="content"/>
                <input type="hidden" name="result" id="result" value="0.0/0.0">
                <div>
                <input type="submit" name="submit" id="creep"   value="Waiting for input..."/>
                <input type="button" name="submit" id="submit_location" value="Sumbit"                onclick="codeAddress(content.value);"></div>
              </form>

              </div>\
              <br></br><div id=\"instr_text\">Example locations:<br></br></div>
               <div id=\"small_text\">
                  307 University Dr College Station, TX 77801<br></br>
                  Texas A&M University<br></br>
                  77840<br></br>
                  </div>\
            </div>

            <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false"></script>
            <script>
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
              //setTimeout(function() { alert("Waiting for something to happen? Try pressing Go!"); }, 3000 );
            }

            function stopRKey(evt) { 
              var evt = (evt) ? evt : ((event) ? event : null); 
              var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null); 
              if ((evt.keyCode == 13) && (node.type=="text"))  {return false;} 
            } 

            document.onkeypress = stopRKey;
            </script>

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
              mapTypeId: google.maps.MapTypeId.HYBRID\
          };\
            \
          map = new google.maps.Map(document.getElementById(\'map-canvas\'), mapOptions);"


nogeoLocate= """
                var infowindow = new google.maps.InfoWindow();
                
                var marker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    icon : \'http://maps.google.com/mapfiles/ms/icons/flag.png\',
                    title: \'Your Location\'
                });
                
                var contentString;
                var geocoder = new google.maps.Geocoder();
                var addr = new String();
                geocoder.geocode({\'latLng\': pos}, function(results, status) {
                  if (status == google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                      addr = results[0].formatted_address;
                     
                      contentString = 
                        \'<p>\' + addr + \'</p>\'+
                        \'<p><b>Location given by user.</b></p>\'+
                        \'<p>Coordinates: \' + pos.toString() + \'</p>\';
                        
                      infowindow.setContent(contentString);
                    }
                  }
                });
              """

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


