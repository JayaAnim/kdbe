if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("{% url 'pwa:ServiceWorker' %}")
    .then(function(registration){
        console.log('Registration successful, scope is:', registration.scope)
    })
    .catch(function(error){
        console.log('Service worker registration failed, error:', error)
    })

}

self.addEventListener("install", function(event){
    event.waitUntil(
        caches.open("v1")
        .then(function(cache){
            return cache.addAll({{ cache_paths_json|safe }})
        })
    )
})

self.addEventListener("fetch", function(event){
    event.respondWith(
        caches.match(event.request)
    )
})
