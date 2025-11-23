predefined_color_ranges = {
    "up": (np.array([170, 195, 75]), np.array([180, 255, 255])),      # dark pink - consistent
    "down": (np.array([15, 150, 80]), np.array([25, 255, 255])),     # yellow - consistent
    "left": (np.array([5, 230, 80]), np.array([12, 255, 255])),   # orange
    "right": (np.array([110, 110, 50]), np.array([120, 255, 255])),  # blue
}


{
    "use_calibrated": true,
    "roi": [400, 200, 50, 50],
    "fps": 30
}


red
{
    "lower": [170, 195, 75],
    "upper": [180, 255, 255]
}

{
    "lower": [15, 150, 80],
    "upper": [25, 255, 255]
}

predefined_color_ranges = {
    "up": (np.array([170, 195, 75]), np.array([180, 255, 255])),      # dark pink - consistent
    "down": (np.array([15, 150, 80]), np.array([25, 255, 255])),     # yellow - consistent
    "left": (np.array([5, 230, 80]), np.array([12, 255, 255])),   # orange
    "right": (np.array([110, 110, 50]), np.array([120, 255, 255])),  # blue
}


{
    "use_calibrated": true,
    "roi": [400, 200, 50, 50],
    "fps": 30
}


red
{
    "lower": [170, 195, 75],
    "upper": [180, 255, 255]
}

{
    "lower": [15, 150, 80],
    "upper": [25, 255, 255]
}

anime
"position": [3035, 1032],

sudo apt-get update
sudo apt-get install wmctrl x11-utils

bookmarklet
javascript:(function(){
    /* 1. Close Ad (Click + Enter) */
    var btn = document.getElementById('close-btn');
    if(btn) {
        btn.click();
        var e = new KeyboardEvent('keydown',{'key':'Enter','code':'Enter','keyCode':13,'bubbles':true});
        btn.dispatchEvent(e);
    }
    
    /* 2. Click Play Button (VideoJS) after delay */
    setTimeout(function(){
        var icon = document.querySelector('.vjs-icon-placeholder');
        if(icon) {
            icon.click();
            if(icon.parentElement) icon.parentElement.click();
        } else {
            /* Fallback */
            var v = document.querySelector('video');
            if(v) { v.focus(); v.play(); }
        }
    }, 800);
})();

oneline:
javascript:(function(){function tap(el){if(!el)return;el.dispatchEvent(new PointerEvent("pointerdown",{bubbles:true}));el.dispatchEvent(new PointerEvent("pointerup",{bubbles:true}));el.click();}var btn=document.getElementById("close-btn");if(btn)tap(btn);setTimeout(function(){var icon=document.querySelector(".vjs-icon-placeholder");if(icon){tap(icon);if(icon.parentElement)tap(icon.parentElement);}else{var v=document.querySelector("video");if(v){v.focus();v.play();}}},800);})();


youtube play all button
<yt-touch-feedback-shape aria-hidden="true" class="yt-spec-touch-feedback-shape yt-spec-touch-feedback-shape--overlay-touch-response-inverse"><div class="yt-spec-touch-feedback-shape__stroke"></div><div class="yt-spec-touch-feedback-shape__fill"></div></yt-touch-feedback-shape>