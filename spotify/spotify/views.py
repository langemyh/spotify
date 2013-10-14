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
    # http://open.spotify.com/track/6A7qC3kcSp2leiG5r5KZj6
    http_match = re.compile(
            r'http://open\.spotify\.com/(album|track|artist)/[a-zA-Z0-9]{22}')
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
        
        if not handler == 'spotify' and not handler == 'http:':
            return HttpResponseRedirect('/')

   
    url = u'http://ws.spotify.com/lookup/1/?uri=spotify:%s:%s' % (type, uri)
    xml_data = urlopen(url).read()
    dom = minidom.parseString(xml_data)

    # Find the titles
    data = {}
    track = []
    try:
        for title in dom.getElementsByTagName('track'):
            track.append(
                    title.getElementsByTagName('name')[0].firstChild.nodeValue)
        data['track'] = track
    except:
        pass
    
    # Find the artists
    artists = []
    try:
        for artist in dom.getElementsByTagName('artist'):
            artistSURI = artist.attributes.items()[0][1]
            artist = artist.getElementsByTagName('name')[0].firstChild.nodeValue
            if type == 'artist':
                artists.append(artist)
            else:
                artists.append({'artist': artist, 'artistSURI': artistSURI})
        data['artist'] = artists
    except:
        pass
    
    # Find the albums
    albums = []
    try:
        for album in dom.getElementsByTagName('album'):
            albumSURI = album.attributes.items()[0][1]
            album = album.getElementsByTagName('name')[0].firstChild.nodeValue
            if type == 'album':
                albums.append(album)
            else:
                albums.append({'album': album, 'albumSURI': albumSURI})
        data['album'] = albums

    except:
        pass

    context = {
        'page_title': 'Spotify',
        'type': type,
        'title': data[type],
        'uri': uri,
        'data': data,
    }
    
    return render(request, 'spotify.html', context)

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
                    search = re.sub(sanitize, '+', search)
                    search = re.sub(r'\+$', '', search)
        
                    # Search for string
                    # http://ws.spotify.com/search/1/track.json?q=search+string
                    try:
                        url = u'http://ws.spotify.com/search/1/track.json?q=%s' % (search)
                        result = json.loads(urlopen(url).read())

                        # Get artist, title and uri
                        artist = ''
                        for a in result['tracks'][0]['artists']:
                            if (not artist):
                                artist = a['name']
                            elif (not a['name'] in artist):
                                artist = '%s, %s' % (artist, a['name'])
                        title = result['tracks'][0]['name']
                        uri = result['tracks'][0]['href']
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
