from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

# Cria a aplicação Flask
app = Flask(__name__)

load_dotenv()
CLIENT_ID = os.environ.get("WEBEX_CLIENT_ID")
CLIENT_SECRET = os.environ.get("WEBEX_CLIENT_SECRET")
WEBEX_REDIRECT_URL = "https://paulosgf.pythonanywhere.com"


@app.route('/')
def oauth_client_credentials():
    # Informações da sua aplicação
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    access_url = "https://webexapis.com/v1/authorize"
    redirect_uri = WEBEX_REDIRECT_URL
    scopes = "spark:all"
    response_type = "code"

    # Solicitar o código de acesso
    data = {
        "response_type": response_type,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scopes
    }

    # Faz a requisição ao servidor OAuth do WebEx
    response = requests.post(access_url, data=data)

    # Verifica se a resposta foi bem-sucedida
    if response.status_code == 200:
        code = response.json().get("code")
        return jsonify({"Code": code})
    else:
        return jsonify({"Error": response.status_code, "Text": response.text})

if __name__ == "__main__":
    app.run()
