# Arbalet Frontage


Well, I'm using Docker

So, to build for DEV mode:

- In foreground:
	sudo docker-compose up
- In background:
	sudo docker-compose up
- Froce rebuild contenaire:
	sudo docker-compose up --build

In prod mode (@todo)
	sudo docker-compose -f docker-compose.prod.yml up


Then, to start ther Scheduler (it's kinda important you know), just call go there http://localhost:8123/b/start on a web browser or

curl http://localhost:8123/b/start


To check state, go there:

http://localhost:8123/frontage/status

