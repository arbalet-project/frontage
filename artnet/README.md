# Art-Net I transmitter
This is the process broadcasting pixel colours to all Art-Net I nodes with IP 2.xxx.xxx.xxx
Art-Net I is UDP broadcasting, which doesn't work with NAT and thus require to bind the container to the host network

## Generate new mapping
Mapping `Pixel row, col -> Art-Net DMX addresses` is provided by a static `mapping.json`.
To generate a new one:
```
cd notebooks
jupyter notebook
```
Then follow the notebook cells.

## TODOs 
### Newer ARt-Net implmentation
1. Switch to newer Art-Net version with UDP unicast
2. Switch back to non-host network mode in docker-compose.yml (prod)
3. Uncomment the wait-for-it script in docker-entrypoint.sh so that RabbitMQ is ready before starting the transmitter
