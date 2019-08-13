#!/usr/bin/bash
# coding: utf-8


#---

sudo apt-get update\nsudo apt-get install -y apt-transport-https ca-certificates wget software-properties-common

#  Get the cryptographic (GPG) key for associated with Docker
wget https://download.docker.com/linux/debian/gpg\nsudo apt-key add gpg

echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee -a /etc/apt/sources.list.d/docker.list\n\nsudo apt-get update\n\nsudo apt-cache policy docker-ce


sudo apt-get -y install docker-ce

#---


sudo systemctl start docker

sudo systemctl stop docker

sudo systemctl restart docker


sudo systemctl status docker


sudo systemctl enable docker


sudo docker run hello-world
docker --version


docker info

docker image ls

docker container ls --all

sudo docker images

sudo groupadd docker\n\nsudo useradd ra\n\nsudo usermod -aG docker ra


mkdir -p docker_test\ncd docker_test/

cat code/docker_test/Dockerfile


# Edit your  `requirements.txt` in the same directory. 
# 
# Here, we'll just make use of NumPy, so it has one single line:
# 
# > Numpy
# 
# 
# Pure poetry.

docker build --tag=roll20 .


docker image ls


docker run roll20

docker build --tag=roll20 .


docker inspect roll20

docker swarm init


docker stack deploy -c docker-compose.yml attack_the_grue


docker service ls


docker container ls -q
docker stack ps attack_the_grue 


docker stack deploy -c docker-compose.yml attack_the_grue


docker stack rm attack_the_grue

docker swarm leave --force

