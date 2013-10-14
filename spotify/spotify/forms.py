# encoding: utf-8
from django import forms

class spotifyForm(forms.Form):
	spotify = forms.CharField(label='Spotify',
                max_length=55,
                help_text=u'Spotify URI or URL',
                widget=forms.TextInput(
                    attrs={'placeholder': 'Spotify URI/URL'}))

class playlistForm(forms.Form):
    playlist = forms.CharField(label='Playlist',
            help_text=u'Paste artist - title',
            widget=forms.Textarea(
                attrs={'placeholder': 'Artist - Title'}))
