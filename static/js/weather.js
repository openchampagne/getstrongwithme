var weatherAPI = '1fd09e59f0f835ebe04dc5ab06de40f3';
var geolocationAPI = 'pk.9684621c328d7f6c2548e794b8b05772';


function weather(cityName) {
    cityName = cityName.toLowerCase();
    var request = new XMLHttpRequest();
    request.open('GET', 'https://api.openweathermap.org/data/2.5/weather?q=' + cityName + '&units=imperial&apikey=' + weatherAPI, true);
    request.onload = function() {
        var obj = JSON.parse(this.response);
        if (request.status >= 200 && request.status < 400) {
            var temp = obj.main.temp;
            console.log(temp);
            document.getElementById('temp').textContent = 'It is '+ temp +' F degrees outside in '+ cityName;
        }
        else {
            arr = cityName.split(' ');
            // If the query is one word and found nothing
            if (arr.length == 1) {
                console.log('The city doesnt exist! %s', cityName);
            }
            // If the query is more than one word and found nothing, to try the query with each word and check if --/temp isDefined()/-- 
            else if (arr.length > 1) {
                for (i=0; i<arr.length; i++) {
                    if (arr[i] == 'township') {arr.splice(i, 1); break;}
                    request.open('GET', 'https://api.openweathermap.org/data/2.5/weather?q=' + arr[i] + '&units=imperial&apikey=' + weatherAPI, true);
                    request.onload = function() {
                        var obj = JSON.parse(this.response);
                        if (request.status >= 200 && request.status < 400) {
                            var temp = obj.main.temp;
                            console.log(temp);
                            document.getElementById('temp').textContent = 'It is '+ temp +' F degrees outside in'+ arr[i];
                        }
                        else {
                            console.log('The city doesnt exist! %s', cityName);
                        }
                    }
                    request.send();
                }
            }
        }
    }
    request.send();
}

function getCoordinates() {
    var options = {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    };
  
    function success(pos) {
        var crd = pos.coords;
        var lat = crd.latitude.toString();
        var lng = crd.longitude.toString();
        var coordinates = [lat, lng];
        console.log(`Latitude: ${lat}, Longitude: ${lng}`);
        getCity(coordinates);        
        return;  
    }
  
    function error(err) {
        console.warn(`ERROR(${err.code}): ${err.message}`);
    }  
    navigator.geolocation.getCurrentPosition(success, error, options);
}
  
function getCity(coordinates) {
    var lat = coordinates[0];
    var lng = coordinates[1];
    var request = new XMLHttpRequest();

    request.open('GET', "https://us1.locationiq.com/v1/reverse.php?key="+ geolocationAPI +"&lat="+ lat +"&lon="+ lng +"&format=json", true);
    request.send();
    request.onreadystatechange = processRequest;
    request.addEventListener("readystatechange", processRequest, false);
    
    
    function processRequest(e) {
        if (request.readyState == 4 && request.status == 200) {
            var response = JSON.parse(request.responseText);
            city = response.address.city;
            // console.log(city);
            console.log(city);
            weather(city)
            return;
        }
    }
}
getCoordinates();


