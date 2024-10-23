import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
import colorthief as ct
from PIL import ImageTk, Image
from colorthief import ColorThief
import time
import math

#raw_lyrics = open("/Users/shalomakpakla/Documents/INST326_exercises/heartless.txt", "r")
raw_lyrics = open("/Users/shalomakpakla/Documents/INST326_exercises/champions.txt", "r")
song_file = raw_lyrics.read()
song = song_file.split("\n")
total_lines = len(song)
duration = 167
color_thief = ColorThief('/Users/shalomakpakla/Documents/INST326_exercises/graduation_cover.jpeg')
# get the dominant color
dominant_color = color_thief.get_color(quality=1)
#convert rgb to hex
def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)
background_fill =(rgb_to_hex(dominant_color[0],dominant_color[1],dominant_color[2]))
print(background_fill)
refresh_rate = int(math.floor(duration*1000/(len(song)/2)))


class Karaoke(tk.Tk):
    line = 0
    def __init__(self):
        super().__init__()

        # configure the root window
        self.title('Karoake')
        self.resizable(True, True)
        self.geometry('1500x750')
        self['bg'] = f'{background_fill}'

        #album art
        img = Image.open("/Users/shalomakpakla/Documents/INST326_exercises/graduation_cover.jpeg") 
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
        
        #updates progress bar 
        def start(self):
            play_time = 0
            while(play_time < duration):
                time.sleep(1)
                bar["value"] += 1
                play_time += 1 
                bar.update_idletasks()
       
        # change the background color to black
        self.style = ttk.Style(self)
        self.style.configure(
            'TLabel',
            background='red',
            foreground='white')

        # Lyrics text
        self.label = ttk.Label(
            self,
            text = self.song_line(),
            font=('futura', 40))
        self.label.pack(expand=True)

        # schedule an update for text every 6 second
        self.label.after(refresh_rate, self.update)
    
    def song_line(self):
        if self.line < total_lines or self.line %2 == 0 and self.line == total_lines:
            self.line += 2
            two_bar = ""
            #return song[self.line - 2 : self.line]
            for bar in song[self.line - 2 : self.line]:
                two_bar += bar + '\n'
            return two_bar
        if self.line != "\n" and self.line == total_lines:
                return song[self.line-2]
    
    def update(self):
        """ update the label every 6 seconds """

        self.label.configure(text=self.song_line())

        # schedule another timer
        self.label.after(refresh_rate, self.update)


if __name__ == "__main__":
    newKaroake = Karaoke()
    #newKaroake.start()
    newKaroake.mainloop()