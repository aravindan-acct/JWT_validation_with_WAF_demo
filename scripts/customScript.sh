#! /bin/bash

sudo apt update -y
sudo apt install -y curl wget apt-transport-https
sudo apt install jq -y
wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo cp minikube-linux-amd64 /usr/local/bin/minikube
sudo chmod +x /usr/local/bin/minikube
curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
echo "========= permissions set for kubectl ========="
chmod +x kubectl
echo "========= moving kubectl to /usr/local/bin ========="
sudo mv kubectl /usr/local/bin/
echo "========= installing docker ========="
sudo apt install -y docker.io
echo "========= adding labuser to docker group ========="
sudo usermod -aG docker labuser && newgrp docker
echo "========= starting minikube ========="
sudo -i -u labuser << EOF
echo "========= starting minikube as labuser ========="
minikube start --driver=docker
sudo apt-get -y install nginx
sudo cp /home/labuser/.minikube/ca.key /etc/nginx/cert.key
sudo cp /home/labuser/.minikube/ca.crt /etc/nginx/cert.file
minikube ip|xargs > /var/lib/waagent/custom-script/download/0/minikube_ip.txt
wget https://raw.githubusercontent.com/aravindan-acct/JWT_validation_with_WAF_demo/main/scripts/minikube.conf
echo "========= exiting as labuser and continuing with the rest of the script ========="
echo "========= replacing kubeip string with the minikube ip ========="
EOF
#export minikube_interface=`ifconfig | grep "br-" | awk {'print $1'} | tr -d ':'`
#export minikube_ip=`ifconfig $minikube_interface | grep "inet " | awk {'print $2'} | xargs`
export minikube_ip=`cat minikube.txt|xargs`
sed -i "s/kubeip/$minikube_ip/g" minikube.conf
sudo cp /home/labuser/minikube.conf nginxconfig.conf.bak
sudo mv /home/labuser/minikube.conf /etc/nginx/sites-enabled/default
echo "========= starting nginx ========="
sudo systemctl enable nginx
sudo systemctl stop nginx
sudo systemctl start nginx