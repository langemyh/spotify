# set encoding=utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from spotify.forms import spotifyForm, playlistForm

from urllib2 import urlopen
from xml.dom import minidom

import json
import re

def front(request):
    context = {
            'page_title': 'Spotify',
            'form': spotifyForm(),
            'playlist': playlistForm(),
            }
    return render(request, 'front.html', context)

@csrf_exempt
def spotify(request, handler=None, type=None, uri=None):
    # If the data comes from the form
    # https://open.spotify.com/track/6A7qC3kcSp2leiG5r5KZj6
    # spotify:track:063KUC8KY6hyfJqA1z17aN
    http_match = re.compile(
            r'http[s]?://open\.spotify\.com/(album|track|artist)/[a-zA-Z0-9]{22}')
    spotify_match = re.compile(
            r'spotify:(album|track|artist):[a-zA-Z0-9]{22}')

    if request.method == 'POST':
        form = spotifyForm(request.POST)
        if form.is_valid():
            spotify = form.cleaned_data['spotify']
            if re.match(spotify_match, spotify):
                handler, type, uri = spotify.split(':')
            elif re.match(http_match, spotify):
                handler, temp, url, type, uri = spotify.split('/')
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
        
        if not handler == 'spotify' and not handler == 'http:' and not handler == 'https:':
            return HttpResponseRedirect('/')

        try:
            if type == 'track':
                data = track(uri=uri)
            elif type == 'album':
                data = album(uri=uri)
            elif type == 'artist':
                data = artist(uri=uri)
            else:
                return HttpResponseRedirect('/')
    
            context = {
                 'page_title': 'Spotify',
                 'type': type,
                 'title': data[type],
                 'uri': uri,
                 'data': data,
             }
            
            return render(request, 'spotify.html', context)
        except:
            return HttpResponseRedirect('/')
            
    return HttpResponseRedirect('/')

def track(type='tracks',uri=None):
    # https://api.spotify.com/v1/tracks/6eUKZXaKkcviH0Ku9w2n3V
    url = u'https://api.spotify.com/v1/%s/%s' % (type, uri)
    result = json.loads(urlopen(url).read())

    track = {
        'name': result['name'],
        'uri': result['uri'],
        'url': result['external_urls']['spotify'],
        }
    
    album = {
        'name': result['album']['name'],
        'uri': result['album']['uri'],
        'url': result['album']['external_urls']['spotify'],
        }
    
    artists = []
    for artist in result['artists']:
        artists.append({
            'name': artist['name'],
            'uri': artist['uri'],
            'url': artist['external_urls']['spotify'],
        })

    data = {
        'track': track,
        'album': album,
        'artists': artists,
    }

    return data

def album(type='albums',uri=None):
    # https://api.spotify.com/v1/albums/6eUKZXaKkcviH0Ku9w2n3V
    url = u'https://api.spotify.com/v1/%s/%s' % (type, uri)
    result = json.loads(urlopen(url).read())

    tracks = []
    for track in result['tracks']['items']:
        if ("NO" in track['available_markets']):
            track = {
                'name': track['name'],
                'uri': track['uri'],
                'url': track['external_urls']['spotify'],
                }
            tracks.append(track)

    album = {
        'name': result['name'],
        'uri': result['uri'],
        'url': result['external_urls']['spotify'],
        }

    artists = []
    for artist in result['artists']:
        artists.append({
            'name': artist['name'],
            'uri': artist['uri'],
            'url': artist['external_urls']['spotify'],
        })
    data = {
        'tracks': tracks,
        'album': album,
        'artists': artists,
    }

    return data

def artist(type='artists',uri=None):
    # https://api.spotify.com/v1/artists/6eUKZXaKkcviH0Ku9w2n3V
    url = u'https://api.spotify.com/v1/%s/%s' % (type, uri)
    result = json.loads(urlopen(url).read())

    artist = {
        'name': result['name'],
        'uri': result['uri'],
        'url': result['external_urls']['spotify'],
        }

    data = {
        'tracks': '',
        'album': '',
        'artist': artist,
    }
    
    return data

def playlist(request):
    context = {
        'page_title': 'Playlist'
    }

    if request.method == 'POST':
        form = playlistForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['playlist']
            
            # Let's declare some dicts
            #playlist = dict()
            playlist = list()
            missed = list()
            length = 0

            # Something to match on
            #sanitize = re.compile(r'\W')
            sanitize = re.compile(u'[^A-Za-z0-9_ÆØÅæøå.-]+')
            wordseparator = re.compile(r'[\']')

            for i in data.split('\n'):
                if (not re.match('\w', i)):
                    pass
                else:
                    length += 1
                    search = re.sub(wordseparator, '', i)
                    search = re.sub(sanitize, '%20', search)
                    search = re.sub(r'\%20$', '', search)
        
                    # Search for string
                    # https://api.spotify.com/v1/search?q=tania%20bowra&type=track&limit=1
                    try:
                        url = u'https://api.spotify.com/v1/search?q=%s&type=track&limit=1' % (search)
                        result = json.loads(urlopen(url).read())

                        # Get artist, title and uri
                        artist = ''
                        for a in result['tracks']['items'][0]['artists']:
                            if (not artist):
                                artist = a['name']
                            elif (not a['name'] in artist):
                                artist = '%s, %s' % (artist, a['name'])
                        title = result['tracks']['items'][0]['name']
                        uri = result['tracks']['items'][0]['uri']
                        url = uri.replace(
                                ':', '/').replace(
                                'spotify', 'http://open.spotify.com')
                        innslag = {'uri': uri, 'artist': artist, 'title': title, 'url': url}
                        playlist.append(innslag)
                        #playlist[uri] = {'artist': artist, 'title': title, 'url': url}

                    except:
                        artist, title = i.split(' - ')
                        missed.append(i)

        context['playlist'] = playlist
        context['missed'] = missed
        context['length'] = length
        
    else:
        form = playlistForm()
    context['form'] = form

    return render(request, 'playlist.html', context)
