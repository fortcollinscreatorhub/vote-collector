# Introduction

For the FCCH annual elections, we need a method of counting votes. I'm too
lazy to count paper ballots and wanted something computerized. Hence, this
project.

# Usage Model

You run the (web) server application on a computer. You open a web browser
and open the server's page. The user selects who to vote for by checking
checkboxes on the web page, then clicks the vote button. This makes an AJAX
request to the server which records the vote. Once the AJAX request
completes, the javascript in the web page clears the checkboxes ready for
the next person to vote.

# Configuration

Edit config.py. This is a Python syntax file. Hopefully the syntax is
obvious.

# Data Recording

The server converts each person's name to something suitable for use as a
filename. A filename is created by appending ".vote" to each value. Each
vote is recorded as a single line in the person's own .vote file.

To clear out vote data before voting begins:
```
rm *.votes 
```

To determine the number of votes for each person after voting is complete,
simply stop the server and run:

```
wc -l *.votes
```

# Running the server

```
./server.py
```

# URL

Open http://localhost:8080/ in a browser.

# Security

I haven't put a large amount of effor into security. However, the following
security features were implemented:

- AJAX-based vote submission so the browser's back button can't be used to
look at who previous people voted for.

- The processing of vote submissions does check that the people being voted
for are actually in the config file, and rejects a vote if this isn't the
case. The number of votes per submission is also checked.

- The web server binds to localhost (cherrypy's default).

# Known issues.

- The server is likely running on the same machine as the browser, in a
console window under a graphics environment. Someone could interfere with
the server or its data while voting.

- There's nothing stopping someone from submitting the voting form multiple
times. 

However, since we're all sitting around watching the voting process (from
behind the screen so it's not visible) these issues are fairly unlikely to
happen. We could solve the second issue by playing a sound on each
submission, or something similar.

- There isn't much error handling or recovery in the server. In the unlikely
event of an I/O error while recording a vote, bad things might happen.
