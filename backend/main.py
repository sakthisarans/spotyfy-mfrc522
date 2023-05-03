

secret={
    'id':'***************************',
    'secretkey':'************************'
}
pwd='****************'


import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random,time

access_token=''
val=[]
sp=''

def auth():
    global sp,val,access_token
    val=[]
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=secret['id'], client_secret=secret['secretkey'], redirect_uri='https://localhost:8080/', scope=["user-library-read", "user-read-playback-state", "user-modify-playback-state"]))
    token_info=(sp.auth_manager.get_cached_token())
    global access_token
    access_token = token_info['access_token']
    devices = sp.devices()
    temp=sp.current_playback()
    if not temp==None:
        seconds=(temp['progress_ms']/1000)%60
        minutes=(temp['progress_ms']/(1000*60))%60
        print(temp['item']['name']+'=='+str(int(minutes))+':'+str(int(seconds)))
    #print(access_token)
    devices=(devices['devices'])
    for i in devices:
        val.append(i['name'])
        val.append(i['id'])

def play(id,playlist):
    time.sleep(1)
    sp.transfer_playback(device_id=id,force_play=False)
    tracks = []
    results = sp.playlist_tracks(playlist)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_uris = [track['track']['uri'] for track in tracks]
    random.shuffle(track_uris)
    print(track_uris)
    time.sleep(5)
    sp.start_playback(uris=track_uris[:50])
    return track_uris[:50]

def socketcom(playlist):
    id=''
    auth()
    print(val)
    try:
        if 'SM-G550FY' in val:
            id=val[val.index('SM-G550FY')+1]
            return play(id,playlist=playlist)

        elif 'SAKTHISARAN_S' in val:
            id=val[val.index('SAKTHISARAN_S')+1]
            return play(id=id,playlist=playlist)

        else:
            if val.__len__()==0:
                return ('no device online')
            else:
                play(id=val[1],playlist=playlist)

    except Exception as ex:
        print("error")
        return (ex)

def playback_ctl(status):
    auth()
    try:
        if status=='previous':
            sp.previous_track()
            return 'previous track'
            
        elif status=='next':
            sp.next_track()
            return 'next track'

        elif status=='True':
            sp.start_playback()
            return 'pllaying'
        elif status=='False':
            sp.pause_playback()
            return 'paused'
    except Exception as ex:
        return ex

def volume_ctl(perc):
    auth()
    try:
        sp.volume(int(perc))
        return f'volume set to {perc}'
    except Exception as ex:
        return ex

from flask import Flask,request

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def hello_world():
    out=str(request.args.get('input'))
    password=str(request.args.get('pwd'))
    out=(out.split(':'))
    print(out)
    if password==pwd:
        if out[0].strip()=='url':
            print(out[1])
            return ( str(socketcom(out[1]))  )
        elif out[0]=='playback':
            return playback_ctl(out[1])
        elif out[0]=='track':
            return playback_ctl(out[1])
        elif out[0]=='volume':
            return volume_ctl(out[1])
        else :
            return 'none'
app.run()
