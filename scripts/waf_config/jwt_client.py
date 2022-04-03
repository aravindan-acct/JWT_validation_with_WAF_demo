import requests
import json
import argparse
import os


'''
curl -k -v -H 'Content-Type: application/x-www-form-urlencoded' -X POST "https://20.225.52.22/auth/realms/master/protocol/openid-connect/token" \            
-d grant_type=password \
-d client_id=kube \
-d username=k8s_admin \
-d password=pass \
-d scope=openid \
-d response_type=id_token \
-d client_secret=1BRpe52t2wpMpXd39cpxlSq53wWlpGVG
'''
# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument('-s','--server' ,type=str, help="keycloak server ip or host")
parser.add_argument('-c', '--clientsecret', type=str, help="openid client secret")
args = parser.parse_args()
requests.packages.urllib3.disable_warnings()
keycloak_url = 'https://'+args.server+'/auth/realms/master/protocol/openid-connect/token'
data = {
    "grant_type":"password",
    "client_id": "kube",
    "username": "k8s_admin",
    "password": "pass",
    "scope":"openid",
    "response_type":"id_token",
    "client_secret":f'{args.clientsecret}'
}
keycloak_token = requests.post(keycloak_url,data=data, verify=False)
os.system("clear")
token_response = json.loads(keycloak_token.text)
print(f'\n\nJWT Token issued: \n\n\n {token_response["id_token"]} \n\n\n')

print("Sending request to API with the token ...")

#curl -X 'GET' \
  #'https://petstore.swagger.io/v2/pet/findByStatus?status=available' \
  #-H 'accept: application/json' \
  #-H 'authorization: Bearer 2f4d1ac1-5b9a-417b-a1fa-7780fd8e30c6'

#petstore request

petstore_url = 'https://petstore.swagger.io/v2/pet/findByStatus?status=sold'
headers = {"Accept": "application/json", "Host": "petstore.swagger.io" ,"Authorization": "Bearer "+f'{token_response["id_token"]}'}
petstore_response = requests.get(petstore_url, headers=headers)
print(f"Response from Server:\n{json.dumps(petstore_response.text)}\n\n")

with open("waf_config.json", "r") as f:
    content = json.loads(f.read())

print(f"WAF used for JWT Validation - {content['wafip']}")
for i in range(2):
    waf_url = f'https://{content["wafip"]}/v2/pet/findByStatus?status=sold'
    waf_response = requests.get(waf_url, headers=headers, verify=False)
    print(f"Response through WAF: \n{json.dumps(waf_response.text)}\n\n")
    if i < 1:
        print("Trying again after 60 seconds")
        os.system("sleep 61")
    






