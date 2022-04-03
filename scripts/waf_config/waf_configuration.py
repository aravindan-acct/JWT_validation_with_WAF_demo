#! /usr/local/bin/python3
import json
import requests
from http_basic_auth import generate_header


with open("waf_config.json","r") as file:
    f=json.loads(file.read())
#{'wafip': '20.225.94.62', 'mgmtport': 8000, 'adminusername': 'admin', 'adminpwd': 'Pa$$w0rd123', 'backendip': '10.0.0.4', 'backendport': 8443}

if f["mgmtprotocol"] == "http":

    mgmturl = "http://"+f["wafip"]+":"+str(f["mgmtport"])+"/restapi/v3.2/"

else:
    mgmturl = "https://"+f["wafip"]+":"+str(f["mgmtport"])+"/restapi/v3.2/"

# waf login and token for api access
login_url = mgmturl+"login"
headers = {"Content-Type":"application/json"}
login_data= dict()
login_data["username"]=f["adminusername"]
login_data["password"]=f["adminpwd"]

token_response=requests.post(login_url, headers=headers,data=json.dumps(login_data))
token_response_string = json.loads(token_response.text)
basic_auth = generate_header('',token_response_string["token"]+':')
headers.update({"Authorization": basic_auth})

#Create self signed certificate
cert_url = mgmturl + "certificates/self-signed-certificate"
cert_name = "KubeCert"
cert_attr = { "country-code": "US",  
"key-type": "RSA",  
"state": "California",  
"key-size": "2048",  
"allow-private-key-export": "Yes",  
"name": cert_name,  
"organizational-unit": "Product Management",    
"city": "san francisco",  
"organization-name": "barracuda networks",  
"common-name": "kube.cudanet.local"}
check_cert_exists_url = mgmturl+"certificates/self-signed-certificate/"+cert_name
check_cert = requests.get(check_cert_exists_url,headers=headers)

if check_cert.status_code == 200:
    print("Certificate already exists")
    pass
else:
    cert_generate = requests.post(cert_url,headers=headers,data=json.dumps(cert_attr))
    print("certificate created")
    print(cert_generate.text)

#Get System IP
system_url = mgmturl+"system?groups=WAN Configuration"
system_params = json.loads(requests.get(system_url,headers=headers).text)
system_ip = system_params["data"]["System"]["WAN Configuration"]["ip-address"]

#Create service
svc_url = mgmturl+"services"
svc_name = "Kube_Svc"
server_name = "Kube_Server"

svc_exists_check_url = mgmturl+"services/"+svc_name

def svr_config(service_name,server_name):
    svr_config_url = mgmturl+"services/"+service_name+"/servers"
    print(svr_config_url)
    data = {
     "identifier": "Hostname",
     "name": server_name,
     "port": f["backendport"],
     "address-version": "IPv4",
     "hostname": f["backendip"],
     "comments": "Petstore server",
     "status": "In Service",
    }
    create_server = requests.post(svr_config_url,headers=headers,data=json.dumps(data))
    print(create_server.text)
    edit_server_url = svr_config_url+"/"+server_name+"/ssl-policy"
    edit_data = {
        "validate-certificate": "No",
        "enable-https": "Yes",
        }
    enable_ssl = requests.put(edit_server_url,headers=headers,data=json.dumps(edit_data))
    print(enable_ssl.text)
    return create_server.text

get_svc_status = requests.get(svc_exists_check_url,headers=headers)
get_server_status = requests.get(mgmturl+"/services/"+svc_name+"/servers/"+server_name)
if get_svc_status.status_code == 200:
    print("Service already exists")
    if get_server_status == 200:
        print("Server already exists")
        pass
    else:
        server = svr_config(svc_name,server_name)
        print("Server created")
        print(server)
    pass
else:

    svc_attr = {
    "address-version": "IPv4",
    "certificate": "KubeCert",
    "comments": "K8S Service",
    "ip-address": system_ip,
    "mask": "255.255.255.0",
    "name": svc_name,
    "port": "443",
    "status": "On",
    "type": "HTTPS"
    }
    svc_create = requests.post(svc_url,headers=headers,data=json.dumps(svc_attr))
    print("Service created")
    print(svc_create.text)
    try:
        server = svr_config(svc_name,server_name)
        print("Server created under the service")
        print(server)
    except:
        pass

# JWT validation endpoint
jwt_val_endpoint_url = mgmturl+"jwt-validator-endpoints"
with open("jwt_waf_config.json", "r") as f:
    data = json.loads(f.read())
print(data)