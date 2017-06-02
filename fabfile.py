from fabric.api import env
from fabric.api import local
from fabric.api import run
from fabric.api import settings

import local_fabric_settings as fs


env.hosts = [fs.HOST]
env.port = fs.PORT
env.user = fs.USER

repo = fs.DOCKER_REPO

net = 'seventweets'
vol = 'seventweets-postgres-data'

pg_docker_name = 'seventweets-postgres'
pg_user = fs.PG_USER
pg_pass = fs.PG_PASS

app_docker_name = 'seventweets-app'
app_node_name = fs.NODE_NAME
app_node_address = fs.HOST
app_api_token = fs.API_TOKEN

nginx_docker_name = 'seventweets-nginx'
nginx_conf = fs.NGINX_CONF


def test():
    local('PYTHONPATH=. pytest --cov=seventweets')


def build():
    local('docker build -t {} .'.format(repo))


def push():
    local('docker push {}'.format(repo))


def pull():
    run('docker pull {}'.format(repo))


def create_network():
    with settings(warn_only=True):
        run('docker network create {}'.format(net))


def create_volume():
    with settings(warn_only=True):
        run('docker volume create {}'.format(vol))


def run_postgres():
    run('docker run -d ' +
       '--name {} '.format(pg_docker_name) +
       '--net {} '.format(net) +
       '--restart unless-stopped ' +
       '-e POSTGRES_USER={} '.format(pg_user) +
       '-e POSTGRES_PASSWORD={} '.format(pg_pass) +
       '-v {}:/var/lib/postgresql/data '.format(vol) +
        'postgres:9.6')


def stop_postgres():
    run('docker stop {}'.format(pg_docker_name))


def start_postgres():
    run('docker start {}'.format(pg_docker_name))


def restart_postgres():
    stop_postgres()
    start_postgres()


def run_app():
    run('docker run -d ' +
       '--name {} '.format(app_docker_name) +
       '--net {} '.format(net) +
       '--restart unless-stopped ' +
       '-e ST_PG_USER={} '.format(pg_user) +
       '-e ST_PG_PASS={} '.format(pg_pass) +
       '-e ST_PG_HOST={} '.format(pg_docker_name) +
       '-e ST_NODE_NAME={} '.format(app_node_name) +
       '-e ST_NODE_ADDRESS={} '.format(app_node_address) +
       '-e ST_API_TOKEN={} '.format(app_api_token) +
       '{}'.format(repo))


def stop_app():
    run('docker stop {}'.format(app_docker_name))


def start_app():
    run('docker start {}'.format(app_docker_name))


def restart_app():
    stop_app()
    start_app()


def run_nginx():
    run('docker run -d ' +
       '--name {} '.format(nginx_docker_name) +
       '--net {} '.format(net) +
       '--restart unless-stopped ' +
       '-v {}:/etc/nginx/conf.d/default.conf '.format(nginx_conf) +
       '-p 80:80 ' +
       'nginx')


def stop_nginx():
    run('docker stop {}'.format(nginx_docker_name))


def start_nginx():
    run('docker start {}'.format(nginx_docker_name))


def restart_nginx():
    stop_nginx()
    start_nginx()


def deploy():
    build()
    push()
    pull()
    restart_app()

