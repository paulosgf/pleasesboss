# -*- coding:utf-8 -*-
from webbrowser import get
import requests
import json
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

clientID = os.environ.get("WEBEX_CLIENT_ID")
secretID = os.environ.get("WEBEX_CLIENT_SECRET")
redirectURI = "https://6b452916-b836-4123-b50b-518d368ec608-00-3l3sguw8yrcx6.riker.replit.dev/oauth"


@app.route("/")
def index():
    """
    Function Name : main_page
    Description : when using the browser to access server at
              http://127/0.0.1:10060 this function will
              render the html file index.html. That file
              contains the button that kicks off step 1
              of the Oauth process with the click of the
              grant button
    """
    return render_template("index.html")


def get_tokens(code):
    """
    Function Name : get_tokens
    Description : This is a utility function that takes in the
              Authorization Code as a parameter. The code
              is used to make a call to the access_token end
              point on the webex api to obtain a access token
              and a refresh token that is then stored as in the
              Session for use in other parts of the app.
              NOTE: in production, auth tokens would not be stored
              in a Session. This app will request a new token each time
              it runs which will not be able to check against expired tokens.
    """
    print("function : get_tokens()")
    print("code:", code)
    url = "https://webexapis.com/v1/access_token"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }
    payload = {
        "grant_type": "authorization_code",
        "client_id": clientID,
        "client_secret": secretID,
        "code": code,
        "redirect_uri": redirectURI,
    }
    # Faz a requisição POST
    req = requests.post(url=url, data=payload, headers=headers)

    # Imprime o status e a resposta para debugar
    print("Response Status Code:", req.status_code)
    print("Response Text:", req.text)

    # Verifica se o status code é 200 (OK)
    if req.status_code == 200:
        results = req.json()

        # Certifica de que o 'access_token' está na resposta
        if "access_token" in results:
            access_token = results["access_token"]
            refresh_token = results["refresh_token"]

            session["oauth_token"] = access_token
            session["refresh_token"] = refresh_token

            print("Token stored in session : ", session["oauth_token"])
            print("Refresh Token stored in session : ", session["refresh_token"])
        else:
            print("Error: 'access_token' not found in the response")
            print("Full response:", results)
    else:
        print(f"Failed to get tokens: {req.text}")


@app.route("/oauth")
def oauth():
    """
    Function Name : oauth
    Description : After the grant button is click from index.html
              and the user logs into thier Webex account, the
              are redirected here as this is the html file that
              this function renders upon successful authentication
              is granted.html. else, the user is sent back to index.html
              to try again. This function retrieves the authorization
              code and calls get_tokens() for further API calls against
              the Webex API endpoints.
    """
    print("function : oauth()")
    state = request.args.get("state")
    code = request.args.get("code")

    if code is None:
        print("Authorization code not found in request")
        return "Error: Authorization code missing. Please try again."

    print("OAuth code:", code)
    print("OAuth state:", state)
    get_tokens(code)
    return render_template("granted.html")


@app.route("/webex_login")
def webex_login():
    """
    Function Name: webex_login()
    Description: After get Oauth's Authorization Code, it's redirected to
    Webex Login Page.
    """
    webex_authorize_url = (
        f"https://webexapis.com/v1/authorize?client_id={clientID}&response_type=code"
        f"&redirect_uri={redirectURI}&scope=spark:all&state=12345"
    )
    print("Redirecting to:", webex_authorize_url)  # Log da URL de redirecionamento
    return redirect(webex_authorize_url)


def get_tokens_refresh():
    """
    Function Name : get_tokens_refresh()
    Description : This is a utility function that leverages the refresh token
              in exchange for a fresh access_token and refresh_token
              when a 401 is received when using an invalid access_token
              while making an api_call().
              NOTE: in production, auth tokens would not be stored
              in a Session. This app will request a new token each time
              it runs which will not be able to check against expired tokens.
    """
    print("function : get_token_refresh()")

    url = "https://webexapis.com/v1/access_token"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }
    payload = (
        "grant_type=refresh_token&client_id={0}&client_secret={1}&" "refresh_token={2}"
    ).format(clientID, secretID, session["refresh_token"])
    req = requests.post(url=url, data=payload, headers=headers)
    results = json.loads(req.text)

    access_token = results["access_token"]
    refresh_token = results["refresh_token"]

    session["oauth_token"] = access_token
    session["refresh_token"] = refresh_token

    print("Token stored in session : ", session["oauth_token"])
    print("Refresh Token stored in session : ", session["refresh_token"])
    return


@app.route("/spaces", methods=["GET"])
def spaces():
    """
    Funcion Name : spaces
    Description : Now that we have our authentication code the spaces button
              on the granted page can leverage this function to get list
              of spaces that the user behind the token is listed in. The
              Authentication Token is accessed via Session Key 'oauth_token'
              and used to construct the api call in authenticated mode.
    """
    print("function : spaces()")
    print("accessing token ...")
    response = api_call()

    print("status code : ", response.status_code)
    # Do a check on the response. If the access_token is invalid then use refresh
    # tokent to ontain a new set of access token and refresh token.
    if response.status_code == 401:
        get_tokens_refresh()
        response = api_call()

    r = response.json()["items"]
    print("response status code : ", response.status_code)
    spaces = []
    for i in range(len(r)):
        spaces.append(r[i]["title"])

    return render_template("spaces.html", spaces=spaces)


def api_call():
    accessToken = session["oauth_token"]
    url = "https://webexapis.com/v1/rooms"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + accessToken,
    }
    response = requests.get(url=url, headers=headers)
    return response


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
