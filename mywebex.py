from flask import Flask, jsonify
import requests

# Cria a aplicação Flask
app = Flask(__name__)

@app.route('/')
def oauth_client_credentials():
    # Informações da sua aplicação
    client_id = "C94798424f9b59222d253d17d199b060e06c69406157cd8c284afc71e099316f4"
    client_secret = "d51319d89c2e28318e43d03485c4582b6d658bbbac90a8ef4e94f9033d903e2f"
    access_url = "https://webexapis.com/v1/authorize"
    redirect_uri = "https://paulosgf.pythonanywhere.com"
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
