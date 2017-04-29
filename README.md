# opentc_web
This is a demo website to show the capability of <a href="https://github.com/cahya-wirawan/opentc">OpenTC</a>.
The OpenTC server is running in the background listening to the port 3333. The website is running Django, and forward
the prediction request from the web client to the OpenTC server, and forward back again the result from the server
to the web client as json response.