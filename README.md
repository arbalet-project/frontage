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



# Example with python CLI

move to frontage/test, then open a python shell

login as user:
`login = utils.call('POST', url='/b/login', json=Settings.USER).json()['token']`

login as admin:
`admin = utils.call('POST', url='/b/login', json=Settings.ADMIN).json()['token']`

Enable frontage:
`utils.call('POST', url='/b/admin/enabled',json={'enabled': True}, headers={'Authorization': 'Bearer '+admin})`

Start apps:

`utils.call('POST', url='/b/apps/running',json={'name': 'SweepAsync', 'params': {'uapp': 'swipe'}, 'expires':20},headers={'Authorization': 'Bearer '+login}).json()
utils.call('POST', url='/b/apps/running',json={'name': 'Flags', 'params': {'uapp': 'french'}, 'expires':20},headers={'Authorization': 'Bearer '+login}).json()`
