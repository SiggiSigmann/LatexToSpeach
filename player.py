#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygame import mixer
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os
from gtts import gTTS
import time
import threading
from mutagen.mp3 import MP3
from pathlib import Path

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title("TexToSpeach")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.createWidgets()
        self.pack(fill="both", expand=1)
        
        #pause function
        self.pauseMarker = 1

        #display time        
        self.playTime = None
        self.timePause = None

        #songlength
        self.mp3Length = 0

        #slider
        self.updateSlider = True

        #thread for displaying time
        self.updatePlayTime = threading.Thread(target=self.thread_function, args=("PrintTime",))
        self.updatePlayTime.start()

        mixer.init()
    
    #text to speach########################################################################
    def processtextString(self, text):
        #remove everything bevor section
        if b"\\section{" in text:
            index1 = text.index(b"\\section{")
            index2 = text.index(b"}", index1 )+1
            text = b"Kapitel " + text[index1+9:index2-1] + text[index2:]

        #remove commands
        while b"%" in text:
            index1 = text.index(b"%")
            try:
                index2 = text.index(b"\n",index1 )
                text = text[:index1] + text[index2:]
            except:
                text = text[:index1]

        #remove label
        while b"\\label" in text:
            index1 = text.index(b"\\label")
            index2 = text.index(b"}", index1 )+1
            text = text[:index1] + text[index2:]

        #remove bf
        while b"\\textbf{" in text:
            index1 = text.index(b"\\textbf{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1] + text[index1+8:index2-1] + text[index2:]

        #remove it
        while b"\\textit{" in text:
            index1 = text.index(b"\\textit{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1]+ text[index1+8:index2-1]  + text[index2:]

        #remove it
        while b"\\ac{" in text:
            index1 = text.index(b"\\ac{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1]+ text[index1+4:index2-1]  + text[index2:]

        #cite
        while b"\\cite{" in text:
            index1 = text.index(b"\\cite{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1] + text[index2:]

        #ref
        while b"\\ref{" in text:
            index1 = text.index(b"\\ref{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1] + text[index2:]

        #subsubsection
        while b"\\subsubsection{" in text:
            index1 = text.index(b"\\subsubsection{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1] + b"UnterUnterKapitel " + text[index1+15:index2-1] + text[index2:]

        #subsection
        while b"\\subsection{" in text:
            index1 = text.index(b"\\subsection{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1] + b" UnterKapitel " + text[index1+9:index2-1] + text[index2:]
        
        #remove everything bevor section
        while b"\\section{" in text:
            index1 = text.index(b"\\section{")
            index2 = text.index(b"}", index1 )+1
            text = text[:index1] +  b"Kapitel " + text[index1+9:index2-1] + text[index2:]

        #remove paragraph
        while b"\\pparagraph{" in text:
            index1 = text.index(b"\\pparagraph{")
            index2 = text.index(b"}", index1 )+1
            text = text[:index1] +  b"PParagraph " + text[index1+12:index2-1] + text[index2:]

        #remove fparagraph
        while b"\\fparagraph{" in text:
            index1 = text.index(b"\\fparagraph{")
            index2 = text.index(b"}", index1 )+1
            text = text[:index1] +  b"fParagraph " + text[index1+12:index2-1] + text[index2:]

        #table
        while b"\\begin{table}" in text:
            index1 = text.index(b"\\begin{table}")
            index2 = text.index(b"\\end{table}", index1)+12
            text = text[:index1] + text[index2:]

        #longtable
        while b"\\begin{longtable}" in text:
            index1 = text.index(b"\\begin{longtable}")
            index2 = text.index(b"\\end{longtable}", index1)+15
            text = text[:index1] + text[index2:]

        #figure
        while b"\\begin{figure}" in text:
            index1 = text.index(b"\\begin{figure}")
            index2 = text.index(b"\\end{figure}", index1)+12
            text = text[:index1] + text[index2:]

        #enquote
        while b"\\enquote{" in text:
            index1 = text.index(b"\\enquote{")
            index2 = text.index(b"}", index1)+1
            text = text[:index1] + text[index1+9:index2-1] + text[index2:]

        #itemize
        while b"\\begin{itemize}" in text:
            index1 = text.index(b"\\begin{itemize}")
            index2 = text.index(b"\\end{itemize}", index1)+13
            text = text[:index1] + text[index2:]

        #multicolumn
        while b"\\begin{multicols}" in text:
            index1 = text.index(b"\\begin{multicols}")
            index2 = text.index(b"}", index1+18)+1
            text = text[:index1] + text[index2:]

        while b"\\end{multicols}" in text:
            index1 = text.index(b"\\end{multicols}")
            text = text[:index1] + text[index1+15:]

        #remove ´
        while b"\\grqq{}" in text:
            index1 = text.index(b"\\grqq{}")
            text = text[:index1] + text[index1+7:]

                    #remove ´
        while b"\\grqq{ }" in text:
            index1 = text.index(b"\\grqq{ }")
            text = text[:index1] + text[index1+8:]

        #remove ``
        while b"\\glqq" in text:
            index1 = text.index(b"\\glqq")
            text = text[:index1] + text[index1+5:]

        return text

    def createTempMP3(self, text):
        path = os.path.join(os.getcwd(),"dummy.mp3")

        #stop control for mp3 creation
        self.bPlay["state"] = "disabled"
        self.bStop["state"] = "disabled"
        self.bPause["state"] = "disabled"
        self.bp10["state"] = "disabled"
        self.bm10["state"] = "disabled"
        self.bp5["state"] = "disabled"
        self.bm5["state"] = "disabled"
        self.bTex["state"] = "disabled"
        self.bMP3["state"] = "disabled"
        self.update_idletasks()

        #create sound
        self.updateLabel("creating MP3")
        language = 'de'
        myobj = gTTS(text=text.decode(), lang=language, slow=False)
        
        #save model
        #load dummy file to close temp.mp3
        self.updateLabel("saving MP3")
        myobj.save(path)
        mixer.music.load(path)

        #restart control for mp3 creation
        self.bPlay["state"] = "normal"
        self.bStop["state"] = "normal"
        self.bPause["state"] = "normal"
        self.bp10["state"] = "normal"
        self.bm10["state"] = "normal"
        self.bp5["state"] = "normal"
        self.bm5["state"] = "normal"
        self.bTex["state"] = "normal"
        self.bMP3["state"] = "normal"
        self.update_idletasks()

    #player commands########################################################################
    def play(self):
        filename = "dummy.mp3"
        if Path(os.path.join(os.getcwd(),"temp.mp3")).exists():
            filename = "temp.mp3"

        #get length
        audio = MP3(os.path.join(os.getcwd(),filename))
        self.mp3Length = audio.info.length
        
        #open file and play
        mixer.music.load(os.path.join(os.getcwd(),filename))
        mixer.music.play()

        #store time
        self.playTime = time.time()

        #store not paused
        self.pauseMarker = 1

        self.updateLabel("playing")

    def stop(self):
        mixer.music.stop()

        #store not paused
        self.pauseMarker = 1

        self.updateLabel("stop")

    def pause(self):
        if(self.pauseMarker== 1):
            self.pauseMarker = 0

            mixer.music.pause()

            #store pause time
            self.timePause = time.time()

            self.updateLabel("pause")
        else:
            self.pauseMarker = 1

            mixer.music.unpause()

            #calc new time
            self.playTime =  self.playTime+(time.time()- self.timePause)

            self.updateLabel("playing")

    def p10(self):
        elapsed = time.time() - self.playTime
        self.setpos(elapsed+10)

    def m10(self):
        elapsed = time.time() - self.playTime
        delta = min(elapsed, 10)
        self.setpos(elapsed-delta)

    def p5(self):
        elapsed = time.time() - self.playTime
        self.setpos(elapsed+5)

    def m5(self):
        elapsed = time.time() - self.playTime
        delta = min(elapsed, 5)
        self.setpos(elapsed-delta)

    def openFile(self):
        self.stop()

        #show file open dialog
        filename = askopenfilename(filetypes =[('Tex File', '*.tex'),('All files', '*.*')])
        if filename:
            #open file
            with open(filename, 'r', encoding='utf8') as f:
                #read file and set text in text widget
                content = f.read()
                self.T.delete(1.0,"end")
                self.T.insert(1.0, content)
                self.updateLabel("loaded")
        else:
            #handle cancel
            self.updateLabel("no file selected")

    def openText(self):
        self.stop()

        #get text from text widget
        content = self.T.get("1.0",END).encode('utf-8')

        #process text
        content = self.processtextString(content)

        #set processed text
        self.T.delete(1.0,"end")
        self.T.insert(1.0, content)

        #create MP3
        self.updateLabel("creat MP3")
        self.createTempMP3(content)
        self.updateLabel("MP3 ready")

        #play MP3
        self.play()

    def setPositionFromSilder(self, event):
        #stop auto posision update
        self.updateSlider = True

        #update play position
        posistion = float(self.mp3Length)*float(self.scale.get()/100)
        self.setpos(posistion)

        #update time
        self.playTime = time.time() - posistion

    def stopUpdateAutoUpdateForSlider(self, event):
        self.updateSlider = False

    def on_closing(self):
        #ask for closing
        ans = messagebox.askokcancel("TexToSpeach", "Do you want to quit?")

        #handle answere
        if ans:
            #close thread
            if self.updatePlayTime.is_alive():
                self.updatePlayTime.do_run= False
                self.updatePlayTime.join()

            #close window
            self.master.destroy()

    # helperfunctions #######################################################################
    def setpos(self, x):
        #play at new position
        mixer.music.rewind()
        mixer.music.play(0, x/2)

        #update play time
        self.playTime = time.time()-x

    def updateLabel(self, text):
        #update status label
        self.statusString.set(text)
        self.update_idletasks()

    # widgets ####################################################
    def createWidgets(self):
        #grid setup
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=0)

        #grid setup
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=0)
        self.rowconfigure(7, weight=0)
        self.rowconfigure(8, weight=1)
        self.rowconfigure(9, weight=0)
        self.rowconfigure(10, weight=0)
        self.rowconfigure(11, weight=0)
        self.rowconfigure(12, weight=0)

        #buttons
        self.bPlay = Button(self, width=20, text="PLAY", command=self.play)
        self.bStop = Button(self, text="STOP", command=self.stop)
        self.bPause = Button(self, text="PAUSE", command=self.pause)
        self.bp10 = Button(self, text="+10", command=self.p10)
        self.bm10 = Button(self, text="-10", command=self.m10)
        self.bp5 = Button(self, text="+5", command=self.p5)
        self.bm5 = Button(self,  text="-5", command=self.m5)
        self.bTex = Button(self,  text="Load Tex", command=self.openFile)
        self.bMP3 = Button(self,  text="Create MP3", command=self.openText)
        self.bPlay.grid(row=0,column = 0, columnspan =2, sticky="nsew")
        self.bPause.grid(row=1, column = 0, columnspan =2, sticky="nsew")
        self.bStop.grid(row=2, column = 0, columnspan =2, sticky="nsew")
        self.bm5.grid(row=3, column = 0, sticky="nsew")
        self.bp5.grid(row=4, column = 0, sticky="nsew")
        self.bm10.grid(row=3, column = 1, sticky="nsew")
        self.bp10.grid(row=4, column = 1, sticky="nsew")
        self.bTex.grid(row=10, column = 0, columnspan =2, sticky="nsew")
        self.bMP3.grid(row=11, column = 0, columnspan =2, sticky="nsew")

        #labels
        self.timeLabelString = StringVar()
        self.timeLabel = Label(self, textvariable=self.timeLabelString )
        self.timeLabelString.set("-- | --")
        self.timeLabel.grid(row=6, column = 0, columnspan =2, sticky="nsew")

        self.statusString = StringVar()
        self.statusLabel = Label(self, textvariable=self.statusString )
        self.statusString.set("-")
        self.statusLabel.grid(row=12, column = 0, columnspan =2, sticky="nsew")

        #slider
        self.scale = Scale(self, from_=0, to=100 ,tickinterval=20, orient=HORIZONTAL)
        self.scale.set(0)
        self.scale.grid(row=7, column = 0, columnspan =2, sticky="nsew")
        self.scale.bind("<ButtonRelease-1>", self.setPositionFromSilder)
        self.scale.bind("<ButtonPress-1>", self.stopUpdateAutoUpdateForSlider)

        #text
        self.S = Scrollbar(self)
        self.T = Text(self)
        self.S.grid(row=0, rowspan=13, column = 3, sticky="nsew")
        self.T.grid(row=0, rowspan=13, column = 2, sticky="nsew")
        self.S.config(command=self.T.yview)
        self.T.config(yscrollcommand=self.S.set)

    # threads #################################################################################################
    def thread_function(self, name):
        #check if closed
        t = threading.current_thread()
        while getattr(t, "do_run", True):
            time.sleep(0.25)

            #check if music is played and if thread should be closed
            while mixer.music.get_busy() and getattr(t, "do_run", True):
                #calc percentage
                perc = ((time.time() - self.playTime)/self.mp3Length)*100

                #create time strings
                ta =  time.strftime('%M:%S', time.gmtime(time.time() - self.playTime))
                tb =  time.strftime('%M:%S', time.gmtime(self.mp3Length))

                #set label
                self.timeLabelString.set(ta +" | " +   tb + " (" + str("{:.2f}".format(perc)) + "%)")
                
                #update slider position if needed
                if self.updateSlider == True:
                    self.scale.set(int(perc))
                    
                #check if perc is bigger then 100 => update max time
                if perc > 100:
                    self.mp3Length = time.time() - self.playTime

                time.sleep(0.25)

def main():
    root = Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()