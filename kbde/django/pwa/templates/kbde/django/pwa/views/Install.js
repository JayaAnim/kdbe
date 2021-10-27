"use strict"


$(function(){

var $manifest = $("<link>")
$manifest.attr("rel", "manifest")
$manifest.attr("href", "{% url 'pwa:Manifest' %}")

var $service_worker = $("<script>")
$service_worker.attr("src", "{% url 'pwa:ServiceWorker' %}")

var $head = $("head")
$head.append($manifest)
$head.append($service_worker)


if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("{% url 'pwa:ServiceWorker' %}")
    .then(function(registration){
        console.log('Registration successful, scope is:', registration.scope)
    })
    .catch(function(error){
        console.log('Service worker registration failed, error:', error)
    })

}

self.addEventListener("appinstalled", function(){
    window.location.href = "{{ manifest.start_url }}"
})

})
