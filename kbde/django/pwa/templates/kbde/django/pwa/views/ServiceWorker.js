"use strict"


self.addEventListener("install", function(e){
    self.skipWaiting()
})


self.addEventListener("fetch", function(e){
    e.respondWith((async function(){

        var response = await fetch(e.request)

        return response
    })())
})


if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("{% url 'pwa:ServiceWorker' %}")
    .then(function(registration){
        console.log('Registration successful, scope is:', registration.scope)
    })
    .catch(function(error){
        console.log('Service worker registration failed, error:', error)
    })

}
