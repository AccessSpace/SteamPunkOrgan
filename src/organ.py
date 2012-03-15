#!/usr/bin/python
import pygame
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.init()
bpm = 60.0


beatlength = 60.0 / bpm
print beatlength
backgroundbeats = 10000
notebeats = 1000


from time import sleep

from array import array
import socket
import time
import math
from firmata import * 


BackgroundNoises = [
                  pygame.mixer.Sound('../noises/32304__acclivity__shipsbell.wav'),
                  pygame.mixer.Sound('../noises/69299__nummer39__steam.wav'),
                  pygame.mixer.Sound('../noises/90143__pengo-au__steam-burst.wav')]

Accordian = [
  pygame.mixer.Sound('../instruments/accordian/a.wav'),
  pygame.mixer.Sound('../instruments/accordian/b.wav'),
  pygame.mixer.Sound('../instruments/accordian/c.wav'),
  pygame.mixer.Sound('../instruments/accordian/d.wav'),
  pygame.mixer.Sound('../instruments/accordian/e.wav'),
  pygame.mixer.Sound('../instruments/accordian/f.wav'),
  pygame.mixer.Sound('../instruments/accordian/g.wav'),
  ]                


#a = Arduino('/dev/ttyUSB0')
a = Arduino('/dev/ttyACM0')

print 'Connected Thanks...'

backgrounds = len(BackgroundNoises)

count = 0   
a.pin_mode(0, OUTPUT)

maxheight = 60.0
while 1:
# TODO : change this to a loop that continually updates the iIR1val
# TODO : and checks whether a new note is due?
# TODO : drop the sleep
    
    a.parse()
    iIR1val = a.analog_read(0) # Reading from analog pin #0
    
    
    if( count % backgroundbeats) == 0:
        background = random.randint(0, backgrounds - 1)            
        BackgroundNoises[background].play()
    
    if( count % notebeats) == 0:
     
        #print iIR1val
        if iIR1val > 0:
            fDist1 = 12343.85 * pow(iIR1val, -1.15)
            print fDist1
            #print count
            
            if fDist1 < maxheight:
                note = int(math.floor(fDist1 / (maxheight / len(Accordian))))
                print note
                Accordian[note].play()
    
                
    #sleep( beatlength )
    count = count + 1
    

