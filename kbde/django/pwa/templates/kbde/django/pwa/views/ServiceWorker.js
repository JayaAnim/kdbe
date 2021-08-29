if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("{% url 'pwa:ServiceWorker' %}")
    .then(function(registration){
        console.log('Registration successful, scope is:', registration.scope)
    })
    .catch(function(error){
        console.log('Service worker registration failed, error:', error)
    })

}


self.addEventListener("install", function(e){
    self.skipWaiting()
})


self.addEventListener("fetch", function(e){
    e.respondWith((async function(){
        {% comment %}
        var response = await caches.match(e.request)

        if (response){
            return response
        }
        {% endcomment %}

        var response = await fetch(e.request)

        {% comment %}
        if (e.request.method === "GET"){
            var cache = await caches.open("v1")
            cache.put(e.request, response.clone())
        }
        {% endcomment %}

        return response
    })())
})
