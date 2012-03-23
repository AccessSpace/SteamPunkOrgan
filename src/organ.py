#!/usr/bin/python
import pygame
import random
from array import array
import socket
import datetime
import math
from firmata import * 

pygame.init()
pygame.mixer.init()
pygame.mixer.init()

bBeatBased = 1
fBPM = 120.0
oBeatLength = datetime.timedelta(0, 60.0 / fBPM)

#print 'oBeatLength', oBeatLength



oCurrentTime = datetime.datetime.now()
#print 'oCurrentTime' , oCurrentTime

oTriggerTime = oCurrentTime + oBeatLength
#print 'oTriggerTime', oTriggerTime
oBackgroundTime = oCurrentTime + oBeatLength
#print 'oBackgroundTime', oBackgroundTime


BackgroundNoises = [
                  #pygame.mixer.Sound('../noises/32304__acclivity__shipsbell.wav'),
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


Brass = [
  pygame.mixer.Sound('../instruments/brass/a.wav'),
  pygame.mixer.Sound('../instruments/brass/b.wav'),
  pygame.mixer.Sound('../instruments/brass/c.wav'),
  pygame.mixer.Sound('../instruments/brass/d.wav'),
  pygame.mixer.Sound('../instruments/brass/e.wav'),
  pygame.mixer.Sound('../instruments/brass/f.wav'),
  pygame.mixer.Sound('../instruments/brass/g.wav'),
  ]                



SteamWhistle = [
  pygame.mixer.Sound('../instruments/steam-whistle/a.wav'),
  pygame.mixer.Sound('../instruments/steam-whistle/b.wav'),
  pygame.mixer.Sound('../instruments/steam-whistle/c.wav'),
  pygame.mixer.Sound('../instruments/steam-whistle/d.wav'),
  pygame.mixer.Sound('../instruments/steam-whistle/e.wav'),
  pygame.mixer.Sound('../instruments/steam-whistle/f.wav'),
  pygame.mixer.Sound('../instruments/steam-whistle/g.wav'),
  ]                


SteamPipe = [
  pygame.mixer.Sound('../instruments/steam-pipe/a.wav'),
  pygame.mixer.Sound('../instruments/steam-pipe/b.wav'),
  pygame.mixer.Sound('../instruments/steam-pipe/c.wav'),
  pygame.mixer.Sound('../instruments/steam-pipe/d.wav'),
  pygame.mixer.Sound('../instruments/steam-pipe/e.wav'),
  pygame.mixer.Sound('../instruments/steam-pipe/f.wav'),
  pygame.mixer.Sound('../instruments/steam-pipe/g.wav'),
  ]                


#a = Arduino('/dev/ttyUSB0')
oArduino = Arduino('/dev/ttyACM0')

backgrounds = len(BackgroundNoises)

iCount = 0   
fMinHeight = 10.0
fMaxHeight = 50.0


print 'Start Playing :)'


# Pipe class organises everything to do with a pipe on the instrument
# sensing what input there is and playing the note needed.
class Pipe:
    iLastNote    = 0
    iCurrentNote = 0
    fMinHeight   = 10.0
    fMaxHeight   = 50.0
    aIrVals      = []
    iCurrentInstrument = 0
    
    def __init__(self, oArduino, iIrPin, iLightPin, iDialPin, aInstruments):
        # These values are created
        # when the class is instantiated.
        self.oArduino    = oArduino
        self.iIrPin      = iIrPin
        self.iLightPin   = iLightPin
        self.iDialPin    = iDialPin
        self.aInstruments= aInstruments
        self.fNoteLength = (self.fMaxHeight - self.fMinHeight)/ len(self.aInstruments[self.iCurrentInstrument])
        self.fOutStep    = int(255.0 / len(self.aInstruments[self.iCurrentInstrument]))
        #print 'self.fNoteLength', self.fNoteLength
        #print 'pipe OUTPUT', firmata.OUTPUT
        self.oArduino.pin_mode(self.iIrPin, firmata.INPUT)
        self.oArduino.pin_mode(self.iDialPin, firmata.OUTPUT)
        self.oArduino.pin_mode(self.iLightPin, firmata.INPUT)
        self.setNeedle(-1)
    
    def readArduino(self):
      
        self.aIrVals.append(self.oArduino.analog_read(self.iIrPin)) # Reading from analog pin #0
        self.iLight = self.oArduino.analog_read(self.iLightPin)
        
        
        
    def getIR(self):
        iListLength = len(self.aIrVals) -1
        iSampleLength = int( iListLength / 4)
        iTotal = 0
        #print 'iListLength', iListLength, 'iSampleLength', iSampleLength
        
        if iSampleLength > 0 :
            for i in range(iListLength - iSampleLength, iListLength):
                iTotal = iTotal + self.aIrVals[i]
                
            self.iIrVal = int(iTotal / iSampleLength)
            #print 'iTotal', iTotal, 'self.iIrVal', self.iIrVal
        else:
            self.iIrVal = 0
        
        #self.iIrVal = self.oArduino.analog_read(self.iIrPin) # Reading from analog pin #0
        
        self.aIrVals = []
        
        return self.iIrVal
        
    def getDist(self):
        self.getIR()
        if self.iIrVal > 0:
            self.fDist = 12343.85 * pow(self.iIrVal, -1.15)
        else:
            self.fDist = self.fMaxHeight * 2
            
        #print 'pipe', self.iIrPin, 'sDist', self.fDist
        
        return self.fDist
        
    def isActive(self):
        fDist = self.getDist()
        return fDist < self.fMaxHeight
            
    def update(self):
        iNewInstrument = 0
        if self.iLight < 700:
            iNewInstrument = 1
        if self.iCurrentInstrument != iNewInstrument:
            self.iCurrentInstrument = iNewInstrument
            self.fNoteLength = (self.fMaxHeight - self.fMinHeight)/ len(self.aInstruments[self.iCurrentInstrument])
            self.fOutStep    = int(255.0 / len(self.aInstruments[self.iCurrentInstrument]))
            
        self.aInstruments[self.iCurrentInstrument]
        bActive = self.isActive()
        if bActive:
            iNote = self.getNote()
            if(iNote != self.iLastNote):
                self.aInstruments[self.iCurrentInstrument][self.iLastNote].fadeout(200)
                self.iCurrentNote = iNote
                self.iLastNote = self.iCurrentNote
                self.aInstruments[self.iCurrentInstrument][self.iCurrentNote].play()
                #print 'pipe', self.iIrPin, 'iLastNote', self.iLastNote, 'new iNote', iNote    
                self.setNeedle(iNote)
                
        else:
            self.aInstruments[self.iCurrentInstrument][self.iLastNote].fadeout(200)
        
    def setNeedle(self, iNote):
        aNeedleSteps = [180, 165, 150 ,135, 120, 105, 90, 85]
        iNeedle =  aNeedleSteps[iNote + 1]
        
        #print 'iNote', iNote, 'iNeedle', iNeedle
        self.oArduino.analog_write(self.iDialPin, iNeedle)
        
    def getNote(self):     
        if self.fDist < self.fMinHeight:
            iNote = 0
        else:
            iNote = int(math.floor((self.fDist - self.fMinHeight) / self.fNoteLength))        
        return iNote
        
                
Pipes = [
    Pipe(oArduino, 0, 2, 3, [Brass, SteamPipe]),
    Pipe(oArduino, 1, 3, 5, [SteamWhistle, Accordian])
]

iInstrumentSet = 0
    
while 1:
    
    oArduino.parse()
    for oPipe in Pipes:
        oPipe.readArduino() #getIR()
        
    oCurrentTime = datetime.datetime.now()
        
    if oCurrentTime > oBackgroundTime:
        #print 'oCurrentTime triggered oBackgroundTime', oCurrentTime
        oBackgroundTime = oCurrentTime + ((random.randint(5, 15)) * oBeatLength)
        background = random.randint(0, backgrounds - 1)            
        BackgroundNoises[background].play()
    
    
    
    
    if bBeatBased:    
        if oCurrentTime > oTriggerTime:
            #print 'oCurrentTime triggered', oCurrentTime
            oTriggerTime = oCurrentTime + oBeatLength
            for oPipe in Pipes:
                oPipe.update()       
    else:
        for oPipe in Pipes:
            oPipe.update()
        
                
    #sleep( oBeatLength )
    iCount = iCount + 1
    

