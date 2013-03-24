window.onload = function () {
    fix_glossaries();
}

window.onpopstate = function(event) {
    if (event.state != null) {
        document.getElementById('right').innerHTML = event.state;
        fix_glossaries();
    }
}

function getOffset(el) {
    if (el.getBoundingClientRect)
        return el.getBoundingClientRect();
    else {
        var x = 0, y = 0;
        do {
            x += el.offsetLeft - el.scrollLeft;
            y += el.offsetTop - el.scrollTop;
        } 
        while (el = el.offsetParent);

        return { "left": x, "top": y }
    }      
}

function fix_glossaries() {
    glosses = document.getElementsByClassName('glossary');
    last_top = 0;
    for (var i = 0; i < glosses.length; i++){
        glossed = document.getElementsByClassName(glosses[i].id.slice(1))[0];
        cur_top = glossed.getBoundingClientRect().top + window.scrollY;
        if (cur_top <= last_top){
            cur_top = last_top;
        }
        glosses[i].style.top = cur_top;
        last_top = cur_top + glosses[i].getBoundingClientRect().height + 20;
    }
}

function test_handle(req) {
    var elem = document.getElementById('right');
    elem.innerHTML = req.responseText;
    //fix glosssaries
    fix_glossaries();
    history.pushState(req.responseText, "", "s=" + req.search_term); 
}


function xml_http_post(url, data, callback) {
    var req = false;
    req = new XMLHttpRequest();
    req.open("POST", url, true);
    req.search_term = data;
    req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callback(this);
        }
    }
    req.send(data);
}

function maybeSubmit(e) {
    if (e.keyCode == 13){
        //remove all glossaries
        var data = document.getElementById('search').value;
        xml_http_post("/", data, test_handle);
        return false;
    }
}
