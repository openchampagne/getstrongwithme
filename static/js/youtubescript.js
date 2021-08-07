$(document).ready(function(){
    // Heroku API Key fetch
    const aws = require('aws-sdk');

    let YOUTUBE_API = new aws.S3({ key: process.env.YOUTUBE_API });

    var video = ''
    workoutVideoSearch(YOUTUBE_API.key)

    function workoutVideoSearch(key) {
        $("#videos").empty()
        $.get("https://www.googleapis.com/youtube/v3/search?key=" + key + "&type=video&part=snippet&maxResults=" + 10 + "&q=workout",function(data){
            console.log(data)
            data.items.forEach(item => {
                video = `<div="videocontain"><iframe width="420" height="315" src="https://www.youtube.com/embed/${item.id.videoId}" frameborder="0" allowfullscreen></iframe></div>`
                $("#videos").append(video)
            });

        })
    }
}) 