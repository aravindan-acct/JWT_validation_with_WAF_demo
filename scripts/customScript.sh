#! /bin/bash

sudo apt update
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
