"use strict";
(function(){


var ServiceWorker = function(){

    addEventListener("install", function(e){
        skipWaiting()
    })


    addEventListener("fetch", function(e){
        e.respondWith((async function(){
            return await fetch(e.request)
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

}


self.kbde = self.kbde || {}
self.kbde.service_worker = new ServiceWorker()


})()
