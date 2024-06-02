from flask import Flask, render_template, url_for
import requests

app = Flask(__name__)

CLIENT_ID = 'vw9vulse8uzwbjtbbu9jx69lag8bvj'
CLIENT_SECRET = 'beodwtucxx13ld83wq5yt2y9tptfoa'

def get_access_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data['access_token']

def get_category_id(access_token, client_id, category_name):
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'name': category_name
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data['data'][0]['id']

def get_live_streams(access_token, client_id, game_id):
    url = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'first': 100,
        'game_id': game_id
    }
    all_streams = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        all_streams.extend(data['data'])
        if 'pagination' in data and 'cursor' in data['pagination']:
            params['after'] = data['pagination']['cursor']
        else:
            break
    return all_streams

def filter_streams_by_title(streams, keyword):
    return [stream for stream in streams if keyword.lower() in stream['title'].lower()]

@app.route('/')
def index():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    category_name = 'Red Dead Redemption 2'
    game_id = get_category_id(access_token, CLIENT_ID, category_name)
    streams = get_live_streams(access_token, CLIENT_ID, game_id)
    # 'Saloon RolePlay' or 'Saloon RP' or 'Saloon RôlePlay' or "RDR2"
    keywords = ['Saloon RolePlay', 'Saloon RP', 'Saloon RôlePlay', 'SaloonRP']
    filtered_streams = []
    for keyword in keywords:
      filtered_streams.extend(filter_streams_by_title(streams, keyword))

    return render_template('index.html', streams=filtered_streams)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
