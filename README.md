# Arbalet Frontage backend

This is the backend of Arbalet Frontage, the [pixelated building facade software](https://vimeo.com/arbalet/frontage).
By default it drives 4 rows x 19 columns of RGB Art-Net I (DMX) fixtures.
See [Network schematics](frontage.svg).

## Development
### First startup
#### 1. Backend startup

Default keys and passwords are fine for a dev environment.
Make sure [docker-compose](https://docs.docker.com/compose/) is installed on your workstation and then build and run with docker:
```
git clone https://github.com/arbalet-project/frontage.git
cd frontage/dev
docker-compose run --rm app init # Prompt will ask you to create your admin password
docker-compose up
```
If everything goes well, your terminal shows the Arbalet Frontage scheduler state on stdout:
```
scheduler_1  |  ========== Scheduling ==========
scheduler_1  | -------- Enable State
scheduler_1  | scheduled
scheduler_1  | -------- Is Frontage Up?
scheduler_1  | False
scheduler_1  | -------- Usable?
scheduler_1  | False
scheduler_1  | -------- Current App
scheduler_1  | {}
scheduler_1  | ---------- Forced App ?
scheduler_1  | False
scheduler_1  | ---------- Waiting Queue
scheduler_1  | []
```

* Enable state can be `on` (forced on), `scheduled` (according to the daily planning based on sunset time) or `off` (forced off)
* Frontage is up in forced on or when the server's local time is within the range of the daily planning, or when in forced on mode
* Frontage is usable when a regular user is allowed to connect and take control (i.e. when frontage is up and no application is being forced)
* Current app shows the current running f-app (frontage application)
* Forced app is true is the current running f-app is being forced by and admin (will stop only when unforced)
* Waiting queue shows the list of users waiting for controlling the frontage

If you meet authorization issues on Linux, make sure your username is in the docker group: `sudo usermod -aG docker $USER` Log out and log back in so that your group membership is re-evaluated.

#### 2. Open the simulator
Then Open the facade simulator:
```
cd frontage/simulator
python3 simulator.py
```

You must see a 4x19 pixelated window. It may be black since by default the systems comes up at sunset until sunrise. The mobile app lets you change these settings.


#### 3. Take control with the mobile app 
Then compile, deploy and open [the frontend app](https://github.com/arbalet-project/frontage-frontend) and edit its environment so that it calls the IP of your dev workstation (usually `127.0.0.1:PORT` in `environment.ts` instead of default arbalet-project.org URLs)

The dev environment has the following open ports:
* 33400: Frontage landing page: users will be redirected and welcomed there if they connect through Wifi
* 33405: Main REST API for mobile frontend app (used for general control, start and close f-apps, ...)
* 33406: Websocket API for mobile frontend app (used for joystick control and events)
* 33450: Arbalet Live programming environement: Blockly-based environment for programming workshops (f-app Snap/Live)
* 33460: Matomo analytics: reports the traffic of the landing page, the mobile app and Arbalet Live environment

Refer to the doc of the frontend for more further details.

To stop the backend, press Ctl+C once, it will nicely closes all processes.

### Dev ports

* 33400: Frontage landing page (Nginx Wifi captive portal)
* 33405: REST API (Python/Gunicorn)
* 33406: Websocket (Python/Gunicorn)
* 33450: Arbalet Frontage Live (Node JS server)
* 33460: Matomo analytics (PHP/Mariadb)

## Production
Refer to the [install](install) procedure to deploy the app on a production server.

## How to...?
### Reset database and settings
`docker-compose down -v` will get rid of the database, you will then need to initialize a new one with `docker-compose run --rm app init`.
