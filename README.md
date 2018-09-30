# Arbalet Frontage backend

This is the backend of Arbalet Frontage, the [pixelated building facade of Bordeaux University](https://vimeo.com/arbalet/frontage). It drives 4 rows x 19 columns of RGB Art-Net/DMX fixtures. See [Network schematics](frontage.svg).


## Development
Default keys and passwords are fine for a dev environment.
Maker you [docker-compose](https://docs.docker.com/compose/) is installed on your desktop and then build and run with docker:
```
git clone https://github.com/arbalet-project/frontage.git
cd frontage
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

If you're meeting authorizations issues on Linux, make sure your username is in the docker group: `sudo usermod -aG docker $USER` Log out and log back in so that your group membership is re-evaluated.

Then compile, deploy and open [the frontend app](https://github.com/arbalet-project/frontage-frontend) and edit its environment so that it calls the IP of your dev workstation (usually `127.0.0.1` in `environment.ts`)

## Production
Refer to the [install](install) procedure to deploy the app on a production server.
