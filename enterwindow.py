from tkinter import *
import veriable
import socket
import sys


def enterwindow():
    def init(event):
        veriable.YOUR_IP = EntryYIp.get()
        veriable.YOUR_PORT = int(EntryYPort.get())
        veriable.SEND_IP = EntrySIp.get()
        veriable.SEND_PORT = int(EntrySPort.get())
        veriable.NICKNAME = EntryNick.get()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            endinf.insert(END, 'Socket created' + '\n')
        except socket.error as msg:
            print('Failed to create socket. Error Code : ')
            sys.exit()
        try:
            s.bind((veriable.YOUR_IP, veriable.YOUR_PORT))
        except socket.error as msg:
            print('Bind failed. Error Code : ')
            sys.exit()

        endinf.insert(END, 'Socket bind complete' + '\n')
        endinf.insert(END, 'You may send a message' + '\n')

    datatk = Tk()
    endinf = Text(datatk)
    datatk.title('Enter data to connect')
    datatk.geometry('300x400')

    TkYIp = StringVar()
    TkYIp.set('127.0.0.1')
    TkYPort = IntVar()
    TkYPort.set(60001)
    TkSIp = StringVar()
    TkSIp.set('127.0.0.1')
    TkSPort = IntVar()
    TkSPort.set(60002)
    TkName = StringVar()
    TkName.set('User')

    lab1 = Label(datatk, text="Enter You Ip")
    lab1.pack()
    EntryYIp = Entry(datatk, textvariable=TkYIp)
    EntryYIp.pack()

    lab2 = Label(datatk, text="Enter You Port")
    lab2.pack()
    EntryYPort = Entry(datatk, textvariable=TkYPort)
    EntryYPort.pack()

    lab3 = Label(datatk, text="Enter send Ip")
    lab3.pack()
    EntrySIp = Entry(datatk, textvariable=TkSIp)
    EntrySIp.pack()

    lab4 = Label(datatk, text="Enter send Port")
    lab4.pack()
    EntrySPort = Entry(datatk, textvariable=TkSPort)
    EntrySPort.pack()

    lab5 = Label(datatk, text="Enter your nickname")
    lab5.pack()
    EntryNick = Entry(datatk, textvariable=TkName)
    EntryNick.pack()

    but = Button(datatk,
                 text="Connect",  # надпись на кнопке
                 width=30, height=5,  # ширина и высота
                 bg="white", fg="blue")  # цвет фона и надписи

    but.bind('<Button-1>', init)

    but.pack()
    endinf.pack()
    datatk.mainloop()
