# Arbalet Frontage backend

This is the backend of Arbalet Frontage, the [pixelated building facade of Bordeaux University](https://vimeo.com/arbalet/frontage).

## Development
Default keys and passwords are fine for a dev environment.
Build and run with docker:
```
cd arbalet/frontage
docker-compose up --build
```
Then open the frontend app and edit its environment so that it calls the IP of your dev workstation.

## Production
As mentionned in [install](install), in production mode the server is managed by SystemD:
```
sudo service arbalet start   # Main backend start
sudo service artnet start    # Art-Net publisher
sudo service arbalet stop
sudo systemctl status arbalet.service
sudo journalctl -u arbalet -f
```

[Network schematics](frontage.svg)
