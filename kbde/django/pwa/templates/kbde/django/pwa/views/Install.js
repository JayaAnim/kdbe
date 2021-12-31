"use strict"


$(function(){


window.addEventListener("appinstalled", function(){
    window.location.href = "{{ manifest.start_url }}"
})

var deferred_prompt = null

window.addEventListener('beforeinstallprompt', function(e){
    e.preventDefault()
    deferred_prompt = e
})

$(".pwa-install-button").click(function(){
    if (!deferred_prompt){
        return null
    }
    deferred_prompt.prompt()
    deferred_prompt = null
})


})
