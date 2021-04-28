var youtubeAPI = 'AIzaSyAaX34YQfqVzZOYJ_8wgaGMNfRjWy5issk'

embeds = [];
// function to return a list of videos from querying workouts
function workoutVideos() {
    // needed for node.js
    var request = new XMLHttpRequest();
    request.open('GET', 'https://youtube.googleapis.com/youtube/v3/search?q=workout&maxResults=10&key=' + youtubeAPI, true)
    request.onload = function() {
        var obj = JSON.parse(request.responseText);
        if (request.status == 200) {
            obj.items.forEach(element => {
                // console.log('https://www.youtube.com/watch?v='+element.id.videoId)
                embeds.push('https://www.youtube.com/embed/'+element.id.videoId);
                var iframe = 'ifrm'
                var ifrm = document.createElement(iframe)
                ifrm.src = 'https://www.youtube.com/embed/'+element.id.videoId;
            });
        }
        else {
            return request.status, ' :('
        }
    }
    request.send();
}

workoutVideos();

// var i = 0;
// embeds.forEach(element => {
//     var iframe = 'ifrm', i 
//     var ifrm = document.createElement(iframe)
//     ifrm.src = element;
// });

// document.getElementById('ifrm').src = 'https://www.youtube.com/embed/h6JH_ed1zus';


// window.frames['ifrm'].location = 'https://www.youtube.com/embed/h6JH_ed1zus';
// window.frames['ifrm'].location.replace('https://www.youtube.com/embed/h6JH_ed1zus');


