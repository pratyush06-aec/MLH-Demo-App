import os
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Home route
@app.route("/")
def home():
    user = session.get("user")
    return f"Hello {user['name']}" if user else "Not logged in ❌"

# Login route
@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

# Callback route
@app.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    session["user"] = token["userinfo"]
    return redirect("/")

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        f"returnTo=http://localhost:5000&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )

if __name__ == "__main__":
    app.run(debug=True)