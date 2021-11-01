"use strict"


$(function(){

var $manifest = $("<link>")
$manifest.attr("rel", "manifest")
$manifest.attr("href", "{% url 'pwa:Manifest' %}")

var $service_worker = $("<script>")
$service_worker.attr("src", "{% url 'pwa:ServiceWorker' %}")

var $apple_touch_icon = $("<link>")
$apple_touch_icon.attr("rel", "apple-touch-icon")
$apple_touch_icon.attr("href", "{{ manifest.icons.0.src }}")

var $head = $("head")
/*
$head.append($manifest)
$head.append($service_worker)
$head.append($apple_touch_icon)
*/


if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("{% url 'pwa:ServiceWorker' %}")
    .then(function(registration){
        console.log('Registration successful, scope is:', registration.scope)
    })
    .catch(function(error){
        console.log('Service worker registration failed, error:', error)
    })

}

window.addEventListener("appinstalled", function(){
    window.location.href = "{{ manifest.start_url }}"
})

var deferred_prompt = null

window.addEventListener('beforeinstallprompt', function(e){
    e.preventDefault()
    deferred_prompt = e
    console.log("saved prompt")
})

$(".pwa-install-button").click(function(){
    if (!deferred_prompt){
        return null
    }
    deferred_prompt.prompt()
    deferred_prompt = null
})

})
