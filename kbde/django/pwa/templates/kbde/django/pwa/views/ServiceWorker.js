self.addEventListener("install", function(e){
    self.skipWaiting()
})


self.addEventListener("fetch", function(e){
    e.respondWith((async function(){

        var response = await fetch(e.request)

        return response
    })())
})
