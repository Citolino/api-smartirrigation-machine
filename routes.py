from flask import Flask, Response, request
import joblib
import numpy as np
import requests
import json
import os
from datetime import datetime
app = Flask("API SMART IRRIGATION")

model = joblib.load('model_smart.pkl');


@app.route("/api/teste",methods=["GET"])
def teste():
    return {'teste':'teste'}

@app.route("/api/acaoAtuador",methods=["POST"])
def acaoAtuador():

    body = request.get_json()
    new_predict = carregarObjeto(body);
    predição = model.predict(new_predict)

    device_id = body["data"][0]["id"];

    if predição == 1 :
        payloadRequest = {
                "on": {
                    "type" : "command",
                    "value" : ""
                }};

        
    else:
       payloadRequest = {
                "off": {
                    "type" : "command",
                    "value" : ""
                }}
    response = chamaBroker(payloadRequest,device_id); 
    return Response("{'a':'b'}", status=response.status_code, mimetype='application/json')
   
def chamaBroker(payloadRequest,device_id):
    url = "http://18.216.218.224:1026/v2/entities/"+device_id+"/attrs"

    payload = json.dumps(payloadRequest)
    headers = {
    'Content-Type': 'application/json',
    'fiware-service': 'helixiot',
    'fiware-servicepath': '/'
    }

    response = requests.request("PATCH", url, headers=headers, data=payload)
    return response;
   

def carregarObjeto(body):
    umidadeSolo = float(body["data"][0]["humiditySoil"]["value"]);

    umidadeAmbiente = float(body["data"][0]["humidity"]["value"]);

    temperaturaAmbiente = float(body["data"][0]["temperature"]["value"]);

    horaLeitura = datetime.now().toordinal();

    umidadeIdeal = 50

    return np.array([horaLeitura,umidadeSolo, umidadeAmbiente, umidadeIdeal,temperaturaAmbiente]).reshape(1,-1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

