#!/usr/bin/python3

# Copyright (c) 2015, Stephen Warren.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name Stephen Warren, the name Fort Collins Creator Hub, nor the
# names of this software's contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import cherrypy
import re
import time

index_prefix="""\
<html>
<head>
<title>FCCH vote counter</title>
<style>
#disable_ui
{
    /* Do not display it on entry */
    display: none;
    /*
     * Display it on the layer with index 1000.
     * Make sure this is the highest z-index value
     * used by layers on that page
     */
    z-index: 1000;
    /* Make it cover the whole screen */
    position: fixed;
    top: 0%%;
    left: 0%%;
    width: 100%%;
    height: 100%%;
    /* Make it white and partially transparent */
    background-color: white;
    opacity: .5;
    filter: alpha(opacity=50);
}
</style>
</head>
<body>
<div id="disable_ui"></div>
<script>
var to;
function set_msg(s, col) {
    if (to) {
        clearTimeout(to);
        to = null;
    };
    if (s) {
        to = setTimeout(clear_msg, 5000);
    }
    msg = document.getElementById("messages");
    msg.style.color = col;
    msg.innerHTML = s;
}
function set_msg_err(s) {
    set_msg("ERROR: " + s, "red");
}
function set_msg_warn(s) {
    set_msg("WARNING: " + s, "orange");
}
function set_msg_ok(s) {
    set_msg(s, "green");
}
function clear_msg() {
    set_msg("", "black");
}
function enumerate_votes(func) {
    var elements = document.getElementById("frm_votes").elements;
    for (var i = 0; i < elements.length; i++) {
        func(elements.item(i));
    }
}
function submit_votes() {
    var checked = 0;
    enumerate_votes(function(elem_checkbox) {
        if (elem_checkbox.checked) {
            checked++;
        }
    })
    if (checked > %(maxvotes)d) {
        set_msg_err("max %(maxvotes)d votes!");
        return;
    }

    msg = "";
    if (checked < %(maxvotes)d) {
        msg += "Note: That's fewer than %(maxvotes)d votes.\\n";
    }
    msg += "Submit votes?";
    if (!confirm(msg)) {
        set_msg_warn("User cancelled vote; try again.");
        return;
    }

    set_msg_warn("Submitting vote...");

    disable_ui();

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        on_submit_status(xhttp);
    }
    xhttp.open("POST", "/vote", true);
    var frm = document.getElementById("frm_votes");
    var fd = new FormData(frm);
    xhttp.send(fd);
}
function on_submit_status(xhttp) {
    if (xhttp.readyState != 4) {
        return;
    }

    if (xhttp.status != 200) {
        set_msg_err("Vote request failed.");
    } else {
        set_msg_ok("Vote accepted.");
        reset_votes();
    }

    enable_ui();
}
function reset_vote(elem_checkbox) {
    elem_checkbox.checked = false;
}
function reset_votes() {
    enumerate_votes(reset_vote);
}
function reset_all() {
    reset_votes();
    clear_msg();
}
function disable_ui() {
    overlay = document.getElementById('disable_ui');
    overlay.style.display = 'block';
}
function enable_ui() {
    document.getElementById('disable_ui').style.display = 'none';
}
</script>
<h1>Choose up to %(maxvotes)d people:</h1>
<form id="frm_votes" method="POST" action="/vote">
"""

index_pername="""\
<input type="checkbox" name="%(ident)s">%(name)s</input><br/>
"""

index_suffix="""\
</form>
<button id="btn_vote" onclick="submit_votes()">Vote!</button>
<button id="btn_vote" onclick="reset_all()">Reset</button>
<h2 id="messages"/>
</body>
</html>
"""

def name_to_ident(s):
    return re.sub('[^A-Za-z0-9]+', '-', s)

class VoteCounter(object):
    def __init__(self):
        config = {}
        with open("config.py") as f:
            code = compile(f.read(), "config.py", 'exec')
            exec(code, {}, config)
        self.maxvotes = config["maxvotes"]
        self.people = {}
        id = 0
        for name in config["people"]:
            ident = name_to_ident(name)
            self.people[ident] = {
                'name': name,
                'ident': ident,
            }
            id += 1

    @cherrypy.expose
    def index(self):
        s = index_prefix % {'maxvotes': self.maxvotes}
        for person in self.people.values():
            s += index_pername % person
        s += index_suffix
        return s

    @cherrypy.expose
    def vote(self, **kwargs):
        if len(kwargs) > self.maxvotes:
            raise cherrypy.HTTPError(400, "Too many votes")
        for ident in kwargs:
            if not ident in self.people:
                raise cherrypy.HTTPError(400, "Bad person")
        tstamp = time.asctime()
        for ident in kwargs:
            fn = ident + '.votes'
            with open(fn, "at") as f:
                f.write(tstamp + "\n")
        return dict()

cherrypy.quickstart(VoteCounter())
