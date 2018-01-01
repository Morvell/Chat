from tkinter import *
import sys
import socket
import json

import time

from enterwindow import enterwindow
import veriable
import base64
import threading
from veriable import DATA_ARRAY, NICK_ARRAY, DATA_DICT


def smiley():
    """
    вставляет смайлик в TEXT окно
    """
    cv = Canvas(height=30, width=30)
    cv.create_oval(1, 1, 29, 29, fill="yellow")
    cv.create_oval(9, 10, 12, 12)
    cv.create_oval(19, 10, 22, 12)
    cv.create_polygon(9, 20, 15, 24, 22, 20)
    log.window_create(CURRENT, window=cv)


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

        self.s.sendto(
            json.dumps([DATA_ARRAY[0][0],
                        DATA_ARRAY[0][1],
                        veriable.NICKNAME]).encode(),
            (veriable.SEND_IP, veriable.SEND_PORT))
        print("You may send are message")

    def arrinstr(self, arr):
        """
        парсит массив в строку
        :param arr: массив чаров
        :return: возвращаяет строку
        """
        str = ''
        for e in arr:
            str = str + ' ' + e
        return str

    def confirm_message(self,message):
        self.s.settimeout(1)
        data = self.s.recv(1024)
        return data == message

    def new_thread(self, event):
        """
        обрабатывает ввод сообщения,
        файла и отправляет сообшение всем подключенным пользователям
        """

        msg = text.get()

        if str(msg) == ':)':
            log.insert(END, 'I:')
            smiley()
            log.insert(END, '\n')
            for addres in DATA_ARRAY:
                if addres != [veriable.YOUR_IP, veriable.YOUR_PORT]:
                    self.s.sendto(
                        json.dumps([veriable.NICKNAME, ':)']).encode(),
                        (addres[0], addres[1]))
                    if not self.confirm_message(b'yes'):
                        log.insert(END, 'Сообщение не доставлено\n')


        elif str(msg).split(' ')[0] == '-pm:':
            splitmsg = str(msg).split(' ')
            for e in self.splitnick(splitmsg):
                self.s.sendto(json.dumps(
                    'privat message: ' + self.splitmessage(
                        splitmsg) + ' |from ' + veriable.NICKNAME).encode(),
                              (DATA_DICT[e][0], DATA_DICT[e][1]))
            self.s.sendto(json.dumps('privat message: ' + self.splitmessage(
                splitmsg) + ' |to ' + self.arrinstr(
                self.splitnick(splitmsg))).encode(),
                          (veriable.YOUR_IP, veriable.YOUR_PORT))


        elif str(msg) == '-intochat':
            log.insert(END, 'into chat: ')
            for e in NICK_ARRAY:
                log.insert(END, e + ', ')
            log.insert(END, '\n')
        elif str(msg).split(' ')[0] == '-sendfile' \
                and len(str(msg).split(' ')) == 2:

            for addres in DATA_ARRAY:
                if (addres[0], addres[1]) != (
                veriable.YOUR_IP, veriable.YOUR_PORT):
                    self.s.sendto(json.dumps(['-sendfile',
                                              str(msg).split(' ')[
                                                  1]]).encode(),
                                  (addres[0], addres[1]))

            self.sendfile(str(msg).split(' ')[1])
        elif str(msg).split(' ')[0] == '-sendfile' and len(
                str(msg).split(' ')) != 2:
            self.s.sendto(json.dumps('Введены некоректные данные').encode(),
                          (veriable.YOUR_IP, veriable.YOUR_PORT))
        else:
            for addres in DATA_ARRAY:
                if addres != [veriable.YOUR_IP, veriable.YOUR_PORT]:
                    self.s.sendto(
                        json.dumps(veriable.NICKNAME + ': ' + msg).encode(),
                        (addres[0], addres[1]))
                    if not self.confirm_message(b"yes"):
                        log.insert(END, 'Cообщение не доставлено\n')
                else:
                    self.s.sendto(json.dumps("I" + ': ' + msg).encode(),
                                  (addres[0], addres[1]))

        text.set('')

    def sendfile(self, filename):
        """
        производит отправку файлов пользователям
        :param filename: имя дериктории для открытия файла
        :return: none
        """

        with open(filename, "rb") as file:
            i = 0
            self.s.settimeout(5)
            while True:
                buf = file.read(1024 * 5)
                if len(buf) == 0:
                    print('into break')
                    break
                for addres in DATA_ARRAY:
                    if (addres[0], addres[1]) != (
                            veriable.YOUR_IP, veriable.YOUR_PORT):
                        self.s.sendto(buf, (addres[0], addres[1]))

                while self.s.recv(1024) != bytes(buf[0]):
                    for addres in DATA_ARRAY:
                        if (addres[0], addres[1]) != (
                                veriable.YOUR_IP, veriable.YOUR_PORT):
                            self.s.sendto(buf, (addres[0], addres[1]))
                time.sleep(0.005)
                print(buf[0])
                print(buf)
                i += 1
                print('into while send')
        for addres in DATA_ARRAY:
            if (addres[0], addres[1]) != (
            veriable.YOUR_IP, veriable.YOUR_PORT):
                self.s.sendto(b'endfile', (addres[0], addres[1]))

        for addres in DATA_ARRAY:
            if addres != [veriable.YOUR_IP, veriable.YOUR_PORT]:
                self.s.sendto(json.dumps("файл передан").encode(),
                              (addres[0], addres[1]))

    def splitmessage(self, array):
        """
        :param array массив сообщения
        :return message
        отделяет тест сообщения от вспомогательных слов
        """
        newarr = []
        message = ''
        try:
            newarr = array[array.index('-pm:') + 1:array.index('-to')]
            for e in newarr:
                message = message + ' ' + e
            return message
        except Exception:
            log.insert(END, 'ошибка ввода')
            return []

    def splitnick(self, array):
        """
        сплитит ники в массив
        :param исходный массив
        :return массив ников
        """
        newarr = []

        try:
            newarr = array[array.index('-to') + 1:]
            return newarr
        except Exception:
            log.insert(END, 'input error')
            return []


class Server:
    """
    Сервер. Получает данные с других сокетов и обрабатывает их
    """

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
            self.s.bind((veriable.YOUR_IP, veriable.YOUR_PORT))
        except socket.error as msg:
            print('Bind failed. Error Code : ')
            sys.exit()

        print('Socket bind complete')

    def checkdata(self, data):
        """
        Проверяет, существует ли такой пользователь в базе данных, и если нет, то добаляет его
        :param data: пользователь которго нужно проверить на наличие в базе пользователей(массив типа [ip,port,nikname]
        :return: none
        """
        if data not in DATA_ARRAY:
            DATA_ARRAY.append(data)

    def deletenickname(self, nick):
        """
        удаляет ник пользователя
        :param nick: имя пользователя для удаления
        :return:
        """
        NICK_ARRAY.pop(NICK_ARRAY.index(nick))

    def addnickname(self, nick):
        """
        добавляет ник в массив
        """
        if nick not in NICK_ARRAY:
            NICK_ARRAY.append(nick)

    def deletedata(self, data):
        """
        удаляет пользователя из базы пользователей
        :param data: пользователь которго нужно удалить(массив типа [ip,port,nikname]
        :return: none
        """
        DATA_ARRAY.pop(DATA_ARRAY.index(data))

    def exit(self, event):
        """
        обработка нажатия на крестик. Отправляет всем пользователям данные о выходе из чата
        :param event: не нужно вводить. Пременная для tkinter
        :return:
        """

        for e in DATA_ARRAY:
            self.s.sendto(json.dumps(
                veriable.NICKNAME + ' disconnected to chat').encode(),
                          (e[0], e[1]))
        for e in DATA_ARRAY:
            self.s.sendto(json.dumps(
                [veriable.YOUR_IP, veriable.YOUR_PORT, veriable.NICKNAME,
                 'exit']).encode(),
                          (e[0], e[1]))

    def addindict(self, nick, e1, e2):
        """
        добавляет пользвателя в словарь
        :param nick: ник
        :param e1: IP
        :param e2: PORT
        """
        DATA_DICT[nick] = (e1, e2)

    def senddict(self):
        """
        Производит отправку словаря всем пользователям чата
        """
        for e in DATA_ARRAY:
            if (e[0], e[1]) != (veriable.YOUR_IP, veriable.YOUR_PORT):
                self.s.sendto(json.dumps(DATA_DICT).encode(), (e[0], e[1]))

    def new_thread(self):
        """
        получает данные и обрабатывает их. если поевляется новый пользователь,
        отправляет существующим новый список участников
        А так же обрабатывает получение файла
        """
        global DATA_ARRAY
        global NICK_ARRAY
        global DATA_DICT
        self.s.setblocking(False)
        try:
            self.streamdata = self.s.recvfrom(1024)
            self.data = json.loads(self.streamdata[0].decode())
            self.addr = self.streamdata[1]

            if isinstance(self.data, list) and len(
                    self.data) == 3 and isinstance(self.data[2], str):
                self.checkdata([self.data[0], self.data[1]])
                self.addnickname(self.data[2])
                self.addindict(self.data[2], self.data[0], self.data[1])
                for e in DATA_ARRAY:
                    if (e[0], e[1]) != (veriable.YOUR_IP, veriable.YOUR_PORT):
                        self.s.sendto(
                            json.dumps([DATA_ARRAY, NICK_ARRAY]).encode(),
                            (e[0], e[1]))
                self.senddict()

                for e in DATA_ARRAY:
                    self.s.sendto(
                        json.dumps(self.data[2] + ' connect to chat').encode(),
                        (e[0], e[1]))

                tk.after(1, self.new_thread)
                return
            elif isinstance(self.data, list) and len(
                    self.data) == 4 and isinstance(self.data[3], str):
                self.deletedata([self.data[0], self.data[1]])
                self.deletenickname(self.data[2])
                for e in DATA_ARRAY:
                    self.s.sendto(
                        json.dumps([DATA_ARRAY, NICK_ARRAY]).encode(),
                        (e[0], e[1]))
                tk.after(1, self.new_thread)
                return
            elif isinstance(self.data, list) and len(self.data) == 2 and \
                            self.data[0] == '-sendfile':
                try:
                    # msg.bind('<Return>', None)
                    self.getfile(self.data[1])
                except Exception as e:
                    # msg.bind('<Return>', CLT.new_thread)
                    print(e)
                for addres in DATA_ARRAY:
                    if (addres[0], addres[1]) != (
                    veriable.YOUR_IP, veriable.YOUR_PORT):
                        self.s.sendto(json.dumps("файл получен").encode(),
                                      (addres[0], addres[1]))
                # msg.bind('<Return>', CLT.new_thread)
            elif isinstance(self.data, list) and self.data[1] == ':)':
                log.insert(END, self.data[0] + ':')
                smiley()
                log.insert(END, '\n')
                self.s.sendto(b'yes',self.addr)

            elif isinstance(self.data, list):
                DATA_ARRAY = self.data[0]
                NICK_ARRAY = self.data[1]
            elif isinstance(self.data, dict):
                DATA_DICT = self.data

            log.insert(END, self.data + '\n')
            self.s.sendto(b'yes', self.addr)

        except Exception:
            tk.after(1, self.new_thread)
            return

        tk.after(1, self.new_thread)
        return

    def getfile(self, filename):
        """
        производит прием файла
        :param filename: имя файла
        :return: none
        """
        with open(str(filename).split('/')[1], "wb") as file:
            i = 0
            buf = 1
            lastbuf=1
            while buf:
                self.s.settimeout(30)
                buf, addr = self.s.recvfrom(1024 * 100)
                if buf == lastbuf:
                    continue
                str1 = buf
                number = buf[0]
                lastbuf = buf
                self.s.sendto(bytes(number), addr)
                try:
                    if str1 == b"endfile":
                        print('into end')
                        break
                except Exception:
                    print('error')
                file.write(str1)

                print(addr)
                print(str1)
                i += 1
                print('into while')

        print('all get')


enterwindow()
tk = Tk()

text = StringVar()
name = StringVar()
name.set('User')
text.set('')
tk.title('Chat')
tk.geometry('500x400')

log = Text(tk)
ex = Entry(tk)  # моя перменная для обработки закрытия окна
msg = Entry(tk, textvariable=text)
msg.pack(side='bottom', fill='x', expand='true')
log.pack(side='top', fill='both', expand='true')

DATA_ARRAY.append([veriable.YOUR_IP, veriable.YOUR_PORT])
NICK_ARRAY.append(veriable.NICKNAME)
DATA_DICT[veriable.NICKNAME] = (veriable.YOUR_IP, veriable.YOUR_PORT)

SRV = Server()
CLT = Client()

msg.bind('<Return>', CLT.new_thread)
tk.after(1, SRV.new_thread)
ex.bind('<Destroy>', SRV.exit)
tk.mainloop()
