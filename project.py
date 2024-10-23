import os
import base64
from argparse import ArgumentParser
from requests import post, get
import sys
import json
import time
import spotipy
import lyricsgenius as lg
import io
if sys.version_info < (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius as lg
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
import colorthief as ct
from PIL import ImageTk, Image
from colorthief import ColorThief
import math
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
"""
    Project code of the Spotify Karaoke
    Jason Candila, Kumail Jafari, June Lee, Shalom Akpakla
"""

"""
    Jason: Song info class
"""
class info:
    """
        info class is only meant to hold the user's song choice information
    """
    def __init__(self, artist, title, lyrics, image, duration):
        self.artist = artist
        self.title = title
        self.lyrics = lyrics
        self.image = image
        self.duration = duration
    
    
def gui_info(lyrics, image, duration):
    #raw_lyrics = open("/Users/shalomakpakla/Documents/INST326_exercises/heartless.txt", "r")
    song = lyrics.split("\n")
    total_lines = len(song)
    fd = urlopen(image)
    file_path = io.BytesIO(fd.read())
    color_thief = ColorThief(file_path)
    # get the dominant color
    dominant_color = color_thief.get_color(quality=1)
    #convert rgb to hex
    def rgb_to_hex(r, g, b):
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    background_fill =(rgb_to_hex(dominant_color[0],dominant_color[1],dominant_color[2]))
    refresh_rate = int(math.floor(duration/(len(song)/2))) 
    return song, total_lines, background_fill, refresh_rate, file_path
"""
Shalom GUI and other utilities
"""    
class Karaoke(tk.Tk):
    """
    Creates a Karaoke window with 350x350 pixel version of album cover, 
    background color will be that of the dominant color on the cover, and lyrics will be printed out 2 lines at a
    time at constant interval.
    """
    line = 0
    def __init__(self, song, duration, total_lines, background_fill, refresh_rate, file_path):
        super().__init__()
        self.song = song
        self.refresh_rate = refresh_rate
        self.total_lines = total_lines
        
        # configure the Karaoke window
        self.title('Karoake')
        self.resizable(True, True)
        self.geometry('1500x750')
        # change the background color to dominant color of album cover
        self['bg'] = f'{background_fill}'

        #album art
        img = Image.open(file_path) 
        img = img.resize((350,350)) 
        img = ImageTk.PhotoImage(img)
        picture = tk.Label(self, image = img)
        picture.place(x=30,y=375)
        picture.image = img
        picture.pack()
        
        #progress bar
        bar = Progressbar(self, orient = HORIZONTAL, length = 700, maximum = duration)
        bar.place(x=400, y=700)
        bar.pack(pady = 10)
        bar.step(1)
        bar.start(1000)
       
        #style of lyrics(words)
        self.style = ttk.Style(self)
        self.style.configure(
            'TLabel',
            background='black',
            foreground='white')

        # Lyrics text
        self.label = ttk.Label(
            self,
            background = "black",
            text = self.song_line(),
            font=('futura', 40))
        self.label.pack(expand=True)

        # schedule an update for text every x seconds (x= refresh rate)
        self.label.after(refresh_rate, self.update)
    
    def song_line(self):
        """
        Displays Lyrics on GUI, two lines at a time
        Returns: Two lines of lyrics, unless there is only one line left
        """
        if self.line < self.total_lines or self.line %2 == 0 and self.line == self.total_lines:
            self.line += 2
            two_bar = ""
            #return song[self.line - 2 : self.line]
            for bar in self.song[self.line - 2 : self.line]:
                two_bar += bar + '\n'
            return two_bar
        if self.line != "\n" and self.line == self.total_lines:
                return self.song[self.line-2]
    
    def update(self):
        """ Updates the lyrics at a predetermined interval based on song duration """

        self.label.configure(text=self.song_line())

        # schedule another timer
        self.label.after(self.refresh_rate, self.update)
        
"""
    Jason: Spotify and GENIUS API Function
"""
def spot_api(artist_name, song_title):
    """
        This function utilizes the Spotify and GENIUS api to return 
        the url image of the inputted song's album cover as well as
        the song's duration in milliseconds.
        
        Several terminal values are created, these variables are important
        for accessing the user's spotify library to obtain information from.
        For the project, we are using Jason's client id and client secret for
        the project since it is associated with access to the API website.
        Jason's GENIUS access token is also unique to the account associated
        with the API website
    """
    os.environ['SPOTIPY_CLIENT_ID'] = "59b86ae6790f4754949194665425d882"
    os.environ['SPOTIPY_CLIENT_SECRET'] = "8b25728b46ed4756b75698e8b71b4e88"
    os.environ['SPOTIPY_REDIRECT_URI'] = "https://google.com"
    os.environ['GENIUS_ACCESS_TOKEN'] = "Lpt-Wapnelbf2wGB7pGd_WEitsimXTYCtkNFE5NTB-dl451svFCQax4zmR1TV8qL"

    spotify_client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    spotify_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    spotify_redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
    genius_access_token = os.environ.get('GENIUS_ACCESS_TOKEN')

    scopes = 'user-read-currently-playing'

    #Creation of oauth_object allows us in the future to obtain a spotify access token
    oauth_object = spotipy.SpotifyOAuth(client_id=spotify_client_id,
                                        client_secret=spotify_secret,
                                        redirect_uri=spotify_redirect_uri,
                                        scope=scopes)

    #Starting in the form of a dictionary, we obtain the token for authorized user access
    token_dict = oauth_object.get_access_token()
    token = token_dict['access_token']

    #The genius API object has been created for searching future information
    genius = lg.Genius(genius_access_token)

    #An authentication header is made, needs token obtained earlier from oauth_object
    auth_header = {"Authorization": "Bearer " + token}
    
    """
        url: The API's Search url to be used to search certain types of objects the API uses
        query: Using the information inputted, we make a search query that uses the artist name
            and track name. 'limit=1' allows for only the most popular search to appear for the user
    """
    url = "https://api.spotify.com/v1/search"
    query = f"?q={artist_name, song_title}&type=artist,track&limit=1"
    
    """
        query_url: Combined url and query variables into one url string
        result: Object that represents the API's information on the searched query, 
            utilizes the auth_header for access
        json_result: API's information converted into a usable dictionary, to be used later
            for obtaining information the Spotify API provides 
    """
    query_url = url + query
    result = get(query_url, headers=auth_header)  
    json_result = json.loads(result.content)

    #Raised ValueError case for incorrectly inputted information
    if len(json_result) == 0:
        raise ValueError("There are no artists or songs with the inputted names")
        
    """
        image: The URL of the album cover image, obtained with the Spotify's API
            dictionary key pathing
        duration: The duration of a song in milliseconds, obtained with the Spotify's API
            dictionary key pathing
    """
    image = json_result["tracks"]["items"][0]["album"]["images"][1]["url"]
    duration = json_result["tracks"]["items"][0]["duration_ms"]
    """
        song: A class object created by the GENIUS API's search_song function.
            The arguments used are the information inputted into the spot_api
            function.
        lyrics: The lyrics from the song class created beforehand
        
        A ValueError case has been created for cases where there is no GENIUS
        information on the inputted song.
    """
    song = genius.search_song(title=song_title, artist=artist_name)
    if song == None:
        raise ValueError("The song inputted as no GENIUS lyrics")
    lyrics = song.lyrics
    
    
    return lyrics, image, duration

"""
    June: Function for user input
"""
def get_spotify_song():
    """
    This function prompts the user for to input an artist name and song title.
    The inputed name and title is then stored in variables to later be accessed.
    """
    # Get user input for artist and song
    print("INSTRUCTIONS:")
    user_input = input("Enter artist name and song title separated by a comma (e.g., Artist Name, Song Title): ")

    # Split the user input into artist and song
    artist_name, song_title = map(str.strip, user_input.split(','))

    return artist_name, song_title

"""
    Kumail: main function structure
"""
def main():
    """
    This main function serves the purpose of bringing the entire program together. It starts by welcoming the user, then retrieves all of the
    information for the spotify song, and lastly lets the user know that there is a new tab opened for the Karaoke visual.
    """
    print("Welcome to Spotify Karaoke!")
    an, st = get_spotify_song()
    lyrics, image, duration = spot_api(an, st)
    songInfo = info(an, st, lyrics, image, duration)
    song, total_lines, background_fill, refresh_rate, file_path = gui_info(songInfo.lyrics, songInfo.image, songInfo.duration)
    print("A new Karaoke tab has opened")
    GUI = Karaoke(song, songInfo.duration, total_lines, background_fill, refresh_rate, file_path)
    GUI.mainloop()


if __name__ == "__main__":
    main()
    
