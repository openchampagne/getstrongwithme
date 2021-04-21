var weatherAPI = '1fd09e59f0f835ebe04dc5ab06de40f3';
var geolocationAPI = 'pk.9684621c328d7f6c2548e794b8b05772';

//Function to return activity suggestion based on weather conditions 
 function activitySuggestion(temp, conditionStatus) {

    var activity = ""; 

    if (temp >= 67 && temp <= 90 && conditionStatus == 'clear') {
        activity = "Perfect Time for a Brisk Outdoor walk or a Nice Run";
         } 
    if (temp > 95 && conditionStatus == 'clear') {
            activity = "Perhaps its too hot for Outdoor Activities. Try an Indoor activity like a Gym Workout";
        }
    if (conditionStatus == 'rain' || conditionStatus == 'light rain' || conditionStatus == 'moderate rain') {
            activity = "When it rains it pours... Don't let that affect your Activity. Do an indoor workout!";
        }
    if (conditionStatus = 'broken clouds' || conditionStatus == 'scattered clouds' || conditionStatus == 'cloudy' || conditionStatus == 'clouds') {
            activity = "Looks like it's Cloudy. Great time for a Walk, Run or Outdoor Yoga without the Sun";
        }
    else {
             activity = "No Activity Suggestions at this Time"
         }
    document.getElementById('activitySuggestion').textContent = activity;
    console.log(conditionStatus);
}

function weather(coordinates, city) {
    var lat = coordinates[0];
    var lon = coordinates[1];
    var request = new XMLHttpRequest();
    request.open('GET', 'https://api.openweathermap.org/data/2.5/weather?lat=' + lat + '&lon=' + lon + '&units=imperial&apikey=' + weatherAPI, true);
    request.onload = function() {
        var obj = JSON.parse(this.response);
        if (request.status >= 200 && request.status < 400) {
            var temp = obj.main.temp;
            var condition = obj.weather[0].main;
            var conditionStatus = obj.weather[0].description;
            document.getElementById('temp').textContent = "It's " + temp + "°F outside in " + city;
            //document.getElementById('temp-status').textContent = "Conditions are: " + conditionStatus;
        }
        else {
            console.log('Couldn\'t fetch temperature for latitude: '+ lat + ' longitude: '+ lon);
        }
    }
    request.send();
    activitySuggestion();
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
        var lon = crd.longitude.toString();
        var coordinates = [lat, lon];
        console.log(`Latitude: ${lat}, Longitude: ${lon}`);
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
    var lon = coordinates[1];
    var request = new XMLHttpRequest();

    request.open('GET', "https://us1.locationiq.com/v1/reverse.php?key="+ geolocationAPI +"&lat="+ lat +"&lon="+ lon +"&format=json", true);
    request.send();
    request.onreadystatechange = processRequest;
    request.addEventListener("readystatechange", processRequest, false);
    
    
    function processRequest(e) {
        if (request.readyState == 4 && request.status == 200) {
            var response = JSON.parse(request.responseText);
            city = response.address.city;
            console.log(city);
            weather(coordinates, city);
            return;
        }
    }
}

getCoordinates();