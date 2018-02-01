1. Clone the repo https://YOUR_USERNAME@bitbucket.org/aio_kombos/sentry.git
2. Go to dir:  cd sentry
3. Change SENTRY_SECRET_KEY to random 32 char string in .env
4. Run `docker-compose up -d`
5. Run `docker exec -it sentry_sentry_1 sentry upgrade` to setup database and create admin user
6. when ask, set:
 - mail: sentry@numii.io
 - password: aionet
 - is super user: y

7. Run `docker restart sentry_sentry_1`
8. Sentry is now running on public port 9000
