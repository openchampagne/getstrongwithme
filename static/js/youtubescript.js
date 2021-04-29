$(document).ready(function(){
    var API_KEY = "AIzaSyAEb-k--seGJtYZXim0bJPbaMuSzUob7Wg"
    var video = ''
    workoutVideoSearch(API_KEY)

    function workoutVideoSearch(key) {
        $("#videos").empty()
        $.get("https://www.googleapis.com/youtube/v3/search?key=" + key + "&type=video&part=snippet&maxResults=" + 10 + "&q=workout",function(data){
            console.log(data)
            data.items.forEach(item => {
                video = `<iframe width="420" height="315" src="http://www.youtube.com/embed/${item.id.videoId}" frameborder="0" allowfullscreen></iframe>`
                $("#videos").append(video)
            });

        })
    }
}) 