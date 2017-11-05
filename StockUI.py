#!python2
import Tkinter as tkinter
import tkFileDialog
import os
import numpy as np
from time import sleep
import serial
import re
import serial.tools.list_ports
import ttk
import tkMessageBox
import threading
import Queue
import tkFont
d = [0]
i = 0

class SerialThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        global ser, actualLength

        while True:
            try:
                sleep(1)
                if ser.inWaiting():
                    pos = ser.readline(ser.inWaiting())
                    pos = pos[:-1]
                    actualLength.set(pos)
                    print actualLength.get()
                 #   ser.write('R')
            except:
                sleep(.1)

class MainWindow(tkinter.Tk, object):
    def __init__(self):
        tkinter.Tk.__init__(self)
        global targetLength, actualLength
        targetLength = tkinter.StringVar()
        actualLength = tkinter.StringVar()
        sizex = 800
        sizey = 600
        posx = 100
        posy = 100
        bigfont = tkFont.Font(family="Helvetica", size=18)
        self.option_add("*Font", bigfont)
        self.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
        self.state('zoomed')

        bframe = tkinter.Frame(self, width=sizex, height=100)  # This frame holds the motor controls
        bframe.pack(side=tkinter.BOTTOM)
        tframe = tkinter.Frame(self, relief=tkinter.GROOVE, width=sizex, height=1000)  # This frame holds the title
        tframe.pack(side=tkinter.TOP)

        rframe = tkinter.Frame(self, relief=tkinter.GROOVE, width=200, height=sizey,
                               bd=1)  # This frame holds the current cut list numbers

        rframe.pack(side=tkinter.RIGHT, fill="y")
        lframe = tkinter.Frame(self, relief=tkinter.GROOVE, width=200,
                           height=sizey)  # This frame holds the cutlist Controls

        lframe.pack(side=tkinter.LEFT)
        self.mframe = tkinter.Frame(self, width=sizex - 400, height=sizey - 200)  # This frame holds the Cutlength Displays
        self.mframe.pack(side=tkinter.TOP)

        self.canvas = tkinter.Canvas(rframe)
        self.frame = tkinter.Frame(self.canvas)
        myscrollbar = tkinter.Scrollbar(rframe, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=myscrollbar.set)

        myscrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="y")
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.frame.bind("<Configure>", self.myfunction)
        self.data()

        self.cb = ttk.Combobox(tframe, width=200, height = 100, values=self.serial_ports(), font=('Fixed', 22, 'bold'))
        # assign function to combobox
        self.cb.bind('<<ComboboxSelected>>', self.on_select)
        self.cb.pack(side=tkinter.LEFT, fill="y")

        sideButtonHeight = 5
        sideButtonWidth = 20
        bottomButtonHeight = 10
        bottomButtonWidth = 17
        font =("Courier", 10, 'bold')
        useButton = tkinter.Button(lframe, text="Use Cutlist", width = sideButtonWidth, height = sideButtonHeight,font = font, bg="orange", fg="black",command = self.useCutlist)
        useButton.bind("<Button-1>", self.useCutlist)  # left click button
        useButton.pack(side=tkinter.TOP)

        loadButton = tkinter.Button(lframe, text="Load Cutlist", width=sideButtonWidth, height=sideButtonHeight,font = font, bg="orange", fg="black")
        loadButton.bind("<Button-1>", self.loadCutlist)  # left click button
        loadButton.pack(side=tkinter.TOP)

        closeButton = tkinter.Button(lframe, text="Close Cutlist", width=sideButtonWidth, height=sideButtonHeight,font = font, bg="orange", fg="black")
        closeButton.bind("<Button-1>", self.closeCutlist)  # left click button
        closeButton.pack(side=tkinter.TOP)

        nextButton = tkinter.Button(lframe, text="Next Cut", bg="orange", width=sideButtonWidth, height=sideButtonHeight,font = font, fg="black")
        nextButton.bind("<Button-1>", self.nextCut)  # left click button
        nextButton.pack(side=tkinter.TOP)

        startButton = tkinter.Button(bframe, text="Start", width=bottomButtonWidth, height=bottomButtonHeight, font = font,bg="green", fg="black")
        startButton.bind("<Button-1>", self.start)  # left click button
        startButton.pack(side=tkinter.RIGHT)

        stopButton = tkinter.Button(bframe, text="STOP", width= bottomButtonWidth, height=bottomButtonHeight,font = font, bg="red", fg="white")
        stopButton.bind("<Button-1>", self.stop)  # left click button
        stopButton.pack(side=tkinter.LEFT)

        homeButton = tkinter.Button(bframe, text="Go Home", width=bottomButtonWidth, height=bottomButtonHeight,font = font, bg="orange", fg="black")
        homeButton.bind("<Button-1>", self.home)  # left click button
        homeButton.pack(side=tkinter.LEFT)

        customButton = tkinter.Button(bframe, text="Custom Length", width=bottomButtonWidth, height=bottomButtonHeight,font = font, bg="orange", fg="black")
        customButton.bind("<Button-1>", self.create_window)  # left click button
        customButton.pack(side=tkinter.RIGHT)

        ActualLabel = tkinter.Label(self.mframe, text="Current Length:", width=20, font=("Courier", 22), bg="orange",
                                    fg="black")
        ActualLabel.grid(row=0, column=1)
        ActualLengthLabel = tkinter.Label(self.mframe, textvariable=actualLength, width=20, font=("Courier", 22),
                                    bg="orange",fg="black")
        ActualLengthLabel.grid(row=1, column=1, padx = 2, pady = 2)



        TargetLabel = tkinter.Label(self.mframe, text="Next Length:", width=20, font=("Courier", 22), bg="orange",
                                    fg="black")
        TargetLabel.grid(row=3, column=1)
        TargetLengthLabel = tkinter.Label(self.mframe, textvariable=targetLength, width=20, font=("Courier", 22), bg="orange",
                                    fg="black")
        TargetLengthLabel.grid(row=4, column=1, padx = 2, pady = 2)

        # ForwardButton = tkinter.Button(self.mframe, text="Forward", width=8, height=2, font=("Courier", 16), bg="black",
        #                             fg="white")
        # ForwardButton.bind("<Button-1>",self.moveForward)
        # ForwardButton.grid(row=5, column=3, padx = 2, pady = 2)
        #
        # BackwardButton = tkinter.Button(self.mframe, text="Backward", width=8, height=2, font=("Courier", 16), bg="black",
        #                             fg="white")
        # BackwardButton.bind("<Button-1>",self.moveBackward)
        # BackwardButton.grid(row=5, column=0, padx = 2, pady = 2)
        self.mframe.grid_columnconfigure(1, weight=1)

        try:
            ser = serial.Serial(3, 9600)  # default try to connect to com port 4
        except:
            tkMessageBox.showinfo("COM not available", "Could not connect to to COM port 4, choose a valid COM port")


        self.queue = Queue.Queue()
        thread = SerialThread(self.queue)
        thread.start()
        self.process_serial()

    def process_serial(self):
        while self.queue.qsize():
            try:
                self.text.delete(1.0, 'end')
                self.text.insert('end', self.queue.get())
            except Queue.Empty:
                pass
        self.after(100, self.process_serial)

    def serial_ports(self):
        ports = tuple(serial.tools.list_ports.comports())
        ports = tuple(tuple(attribute.rsplit('}',1)[0] for attribute in port)for port in ports)
        #ports = tuple(port.lsplit('}', 1)[0] for port in ports)
        return tuple(ports)

    def on_select(self,event=None):
        global ser
        # get selection from event
        print("event.widget:", event.widget.get())
        # or get selection directly from combobox
        print("comboboxes: ", self.cb.get()[3])
        ser = serial.Serial(int(self.cb.get()[3])-1, 9600)

    def getInfo(self,fileName):
        global d
        d = np.genfromtxt(fileName, delimiter=',')

    def useCutlist(self, event):
        global i

        targetLength.set(d[i])
        #self.updateTargetLabel()
        self.update_data()

    def loadCutlist(self, event):
        global d, i, targetLength, TargetLabel
        i = 0
        self.clear_data()
        tkinter.Tk().withdraw()
        filename = tkFileDialog.askopenfilename()
        folder, fn = os.path.split(filename)
        jfn, ext = fn.split('.')
        self.getInfo(filename)

        if not any(not isinstance(y, (int, float)) for y in d):
            self.clear_data()
            self.data()
            targetLength.set(d[i])
            #self.updateTargetLabel()
            self.update_data()
            return

    def closeCutlist(self, event):
        self.clear_data()
        global d, targetLength, i
        i = 0
        d = []

    def nextCut(self,event):
        global d, i
        i = i + 1
        if (i >= len(d)):  # if it is the end of the list keep it at the end
            i = 0

        targetLength.set(d[i])
        #self.updateTargetLabel()
        self.update_data()

    def start(self,event):
        global targetLength, ser, actualLength
        if((targetLength.get() is 'S') or(targetLength.get() is 'H')or(targetLength.get() is 'R')):
            try:
                actualLength.set(targetLength.get())
                ser.write(str(targetLength.get()) + '\n')
            except:
                tkMessageBox.showinfo("No COM Port Selected", "Select a COM Port From the top selection Box")

        elif((float(targetLength.get()) > 88) or (float(targetLength.get()) < 0)):
            tkMessageBox.showinfo("NaN", "Bad Value")
        else:
            try:
                actualLength.set(targetLength.get())
                ser.write(str(targetLength.get()) + '\n')
            except:
                tkMessageBox.showinfo("No COM Port Selected", "Select a COM Port From the top selection Box")


    def home(self,event):
        global targetLength
        targetLength.set('H')
        #updateTargetLabel()
        # send 0 to arduino
        # ser.write("home")

    def stop(self,event):
        global targetLength
        targetLength.set('S')
        try:
            ser.write(str(targetLength.get()))
        except:
            tkMessageBox.showinfo("No COM Port Selected", "Select a COM Port From the top selection Box")
        # send stop to arduino

    def data(self):  # loads data into the rightside
        global d
        for i in range(len(d)):
            tkinter.Label(self.frame, text="Cut " + str(i + 1) + ":", font="bold").grid(row=i, column=1)
            tkinter.Label(self.frame, text=d[i], font="bold").grid(row=i, column=2)

    def update_data(self):
        global d, i
        if (i > 0):
            tkinter.Label(self.frame, text="Cut " + str(i) + ":", font="bold").grid(row=i - 1, column=1)
            tkinter.Label(self.frame, text=d[i - 1], font="bold").grid(row=i - 1, column=2)
        else:
            tkinter.Label(self.frame, text="Cut " + str(len(d) - 1) + ":", font="bold").grid(row=len(d) - 1, column=1)
            tkinter.Label(self.frame, text=d[len(d) - 1], font="bold").grid(row=len(d) - 1, column=2)
        tkinter.Label(self.frame, text="Cut " + str(i + 1) + ":", bg="green", font="bold").grid(row=i, column=1)
        tkinter.Label(self.frame, text=d[i], bg="green", font="bold").grid(row=i, column=2)

    def clear_data(self):  # loads data into the rightside
        global d
        i = 0
        for i in range(len(d)):
            tkinter.Label(self.frame, text="                    ", font="bold").grid(row=i, column=1)
            tkinter.Label(self.frame, text="                    ", font="bold").grid(row=i, column=2)

    def myfunction(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=200, height=200)

    def create_window(self,event):
        app = SampleApp()

    # def moveForward(self, event):
    #     global targetLength, ser
    #     try:
    #         print float(actualLength.get())  + .25
    #         ser.write(str(float(actualLength.get())  + .25) + '\n')
    #     except:
    #         tkMessageBox.showinfo("No COM Port Selected", "Select a COM Port From the top selection Box")

    # def moveBackward(self, event):
    #     global targetLength, ser
    #     try:
    #         print float(actualLength.get())  - .25
    #         ser.write(str(float(actualLength.get())  - .25) + '\n')
    #     except:
    #         tkMessageBox.showinfo("No COM Port Selected", "Select a COM Port From the top selection Box")

class SampleApp(MainWindow, object):
    pass
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.entry = tkinter.Entry(self)
        self.button = tkinter.Button(self, text="Submit Value", command=self.get_entry)
        self.button.pack(side= tkinter.BOTTOM)
        self.entry.pack(side = tkinter.TOP)


    def is_number(self, posNumber):

        try:
            float(posNumber)
            return True
        except ValueError:
            return False

    def get_entry(self):
        number = self.entry.get()
        if (self.is_number(number)and(float(number)>=0)and(float(number)<=88)):
            global targetLength
            targetLength.set(number)
        else:
            tkMessageBox.showinfo("NaN Value", "Bad Value")
        self.destroy()

# --- Window Setup ---
root = MainWindow()
root.mainloop()





# def getInfo(fileName):
#     data = np.genfromtxt(fileName, delimiter=',')
#     return data
#
#
# def pullItAlltogether(gf, fileName):
#     d = getInfo(fileName)
#     for i in range(len(d)):
#         print(d[i])
#         ser.write(d[i])
#         ser.read()
#
#
# ser = serial.Serial(2, 9600)
# ser.write("Hello World")
#
# # Start of Execution
# folder = 'Stock'
# GraphFolder = 'Graphs'
# pat = os.path.join(folder, '*.csv')
# all_files = glob.glob(pat)
# for curFile in all_files:
#     print curFile
#     folder, fn = os.path.split(curFile)
#     jfn, ext = fn.split('.')
#     print "Info for %s:\n" % jfn
#     pullItAlltogether(GraphFolder, curFile)
#     print "\n"
#
