import json
import socket
from tkinter import *

global YourPort
global nickname
global SendPort
global YourIp
global SendIp
dataarray = []


class Client:
    """
    Класс клиент. Осуществляет отправку данных
    """

    def __init__(self):
        """
        Создает сокет и отправляет сокету-получателю свои данные(порт и ip)
        """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        self.s.sendto(json.dumps(dataarray).encode(), (SendIp, SendPort))
        print("You may send are message")

    def New_Thread(self, event):
        """
        обрабатывает ввод сообщения и отправляет сообшение
        всем подключенным пользователям
        """

        msg = text.get()
        for addres in dataarray:
            if addres != [YourIp, YourPort]:
                self.s.sendto(json.dumps(nickname + ': ' + msg).encode(),
                              (addres[0], addres[1]))
            else:
                self.s.sendto(json.dumps("I" + ': ' + msg).encode(),
                              (addres[0], addres[1]))

        text.set('')


class Server:
    """
    Сервер. Получает данные с других сокетов и обрабатывает их
    """
    def checkdata(self, data):
        """
        Проверяет, существует ли такой пользователь в базе данных, и если нет,
        то добаляет его
        """
        if None in dataarray:
            dataarray.append(data)
        if data not in dataarray:
            dataarray.append(data)

    def exit(self, event):
        print('Exit')
        return

    def __init__(self):
        """
        инициализирут сокет для получения данных
        """

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            print('Socket created')
        except socket.error as msg:
            print('Failed to create socket. Error Code : ')
            sys.exit()
        try:
            self.s.bind((YourIp, YourPort))
        except socket.error as msg:
            print('Bind failed. Error Code : ')
            sys.exit()

        print('Socket bind complete')

    def New_Thread(self):
        """
        получает данные и обрабатывает их. если поевляется новый пользователь,
        отправляет существующим новый список участников
        """
        global dataarray
        self.s.setblocking(False)
        try:

            self.d = self.s.recvfrom(1024)
            self.data = json.loads(self.d[0].decode())
            self.addr = self.d[1]
            if type(self.data) == list and len(self.data) == 1:
                self.checkdata(self.data[0])
                for e in dataarray:
                    self.s.sendto(json.dumps(dataarray).encode(), (e[0], e[1]))
                tk.after(1, self.New_Thread)
                return

            elif type(self.data) == list:
                dataarray = self.data

            log.insert(END, self.data + '\n')

        except:
            tk.after(1, self.New_Thread)
            return

        tk.after(1, self.New_Thread)
        return


tk = Tk()

text = StringVar()
name = StringVar()
name.set('User')
text.set('')
tk.title('Chat')
tk.geometry('400x300')

log = Text(tk)
ex = Entry(tk)
nick = Entry(tk, textvariable=name)
msg = Entry(tk, textvariable=text)
msg.pack(side='bottom', fill='x', expand='true')
log.pack(side='top', fill='both', expand='true')

"""
YourIp = input("Enter your ip: ")
YourPort = int(input("Enter your port(0-65535): "))
SendIp = input("Enter send ip: ")
SendPort = int(input("Enter SendPort(0-65535): "))
nickname = input("Enter your nickname: ")


"""

YourPort = 60004
SendPort = 60001
YourIp = 'localhost'
SendIp = 'localhost'
nickname = 'Добряк'

dataarray.append([YourIp, YourPort])

SRV = Server()
CLT = Client()

msg.bind('<Return>', CLT.New_Thread)
tk.after(1, SRV.New_Thread)
ex.bind('<Destroy>', SRV.exit)
tk.mainloop()
