from app import app
from app.pictures.views import PictureAPI
from flask import redirect, request, session, render_template, url_for
from instagram import InstagramAPI
from config import INSTAGRAM_SECRET, INSTAGRAM_CLIENT_ID, INSTAGRAM_REDIRECT_URI
from decorators import access_token_required
import requests
import json
from forms import SearchForm

picture_view = PictureAPI.as_view('picture_api')
app.add_url_rule('/pictures/', view_func=picture_view, methods=['GET', ])
app.add_url_rule('/pictures/', view_func=picture_view, methods=['POST', ])


api = InstagramAPI(
    client_id=INSTAGRAM_CLIENT_ID,
    client_secret=INSTAGRAM_SECRET,
    redirect_uri=INSTAGRAM_REDIRECT_URI
)

@app.route('/', methods=('GET', 'POST'))
@access_token_required
def index():
    access_token = session['instagram_access_token']
    form = SearchForm()
    if form.validate_on_submit():
        payload = json.dumps({
            "access_token": access_token,
            "q": form.data['search']
        })
        headers = {'content-type': 'application/json'}
        url = url_for('picture_api', _external=True)
        r = requests.post(url, data=payload, headers=headers)
        data = r.json()
        return render_template('index.html', form=form, media=data[u'data'])

    return render_template('index.html', form=form)


# Redirect users to Instagram for login
@app.route('/connect')
def main():
    url = api.get_authorize_url(scope=['public_content'])
    return redirect(url)


@app.route('/oauth')
def oauth():
    code = request.args.get('code')

    if not code:
        return "No code provided"

    access_token, user = api.exchange_code_for_access_token(code)
    if not access_token:
        return 'Could not get access token'

    # Store instagram access token to the session to use in api
    session['instagram_access_token'] = access_token

    return redirect('/')


