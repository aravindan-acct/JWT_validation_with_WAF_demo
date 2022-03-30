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
echo "========= exiting as labuser and continuing with the rest of the script ========="
EOF

#export minikube_interface=`ifconfig | grep "br-" | awk {'print $1'} | tr -d ':'`
#export minikube_ip=`ifconfig $minikube_interface | grep "inet " | awk {'print $2'} | xargs`
export minikube_ip=`minikube ip|xargs`

# NGINX Configuration
{
cat > nginxconfig.conf << EOF
server {
    
    listen 80;
    listen 8443 default ssl;
    server_name minikube.cudanet.com;
    ssl_certificate           /etc/nginx/cert.file;
    ssl_certificate_key       /etc/nginx/cert.key;
    ssl_session_cache  builtin:1000  shared:SSL:10m;
    ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
    ssl_prefer_server_ciphers on;
    access_log            /var/log/nginx/minikube.access.log;
    location / {
      proxy_set_header        X-Real-IP \$remote_addr;
      proxy_set_header        X-Forwarded-For \$remote_addr;
      proxy_set_header        X-Forwarded-Proto \$scheme;
      # Fix the “It appears that your reverse proxy set up is broken" error.
      proxy_pass          https://kubeip:8443;
      proxy_read_timeout  90;
      proxy_redirect      https://kubeip:8443 https://minikube.cudanet.com:8443;
      
    }
  }

EOF
}
echo "========= replacing kubeip string with the minikube ip ========="
sed -i "s/kubeip/$minikube_ip/g" nginxconfig.conf

sudo cp nginxconfig.conf nginxconfig.conf.bak
sudo mv nginxconfig.conf /etc/nginx/sites-enabled/default
echo "========= starting nginx ========="
sudo systemctl enable nginx
sudo systemctl stop nginx
sudo systemctl start nginx