# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import socket
import threading
import json

global YourPort
global nikname
global SendPort
global YourIp
global SendIp
dataarray = []


class Client:
    '''
    Класс клиент. Осуществляет отправку данных
    '''

    def __init__(self):
        """Создает сокет и отправляет сокету-получателю
        свои данные(порт и ip)"""
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()

        self.host = 'localhost'
        self.port = YourPort

        self.s.sendto(json.dumps(dataarray).encode(), (SendIp, SendPort))

    def New_Thread(self):
        """обрабатывает ввод сообщения и
        отправляет всем подключенным пользователям"""
        while 1:
            self.msg = input()

            try:
                for addres in dataarray:
                    if addres != [YourIp, YourPort]:
                        self.s.sendto(
                            json.dumps(nikname + ': ' + self.msg).encode(),
                            (addres[0], addres[1]))

            except socket.error as msg:
                print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                sys.exit()


class Server:
    """Сервер. Получает данные с других  сокетов и обрабатывает их"""

    def checkdata(self, data):
        """Проверяет, существует ли такой пользователь в базе данных,
        и если нет, то добаляет его"""
        if None in dataarray:
            dataarray.append(data)
        if data not in dataarray:
            dataarray.append(data)

    def __init__(self):
        """инициализирут сокет для получения данных"""

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
        while 1:
            self.d = self.s.recvfrom(1024)
            self.data = json.loads(self.d[0].decode())
            self.addr = self.d[1]
            if type(self.data) == list and len(self.data) == 1:
                self.checkdata(self.data[0])
                for e in dataarray:
                    self.s.sendto(json.dumps(dataarray).encode(), (e[0], e[1]))
                continue

            elif type(self.data) == list:
                dataarray = self.data
            else:

                if not self.data:
                    break

                print(self.data)

        self.s.close()


YourPort = int(input("Enter your port: "))
SendPort = int(input("Enter SendPort: "))
YourIp = input("Enter your ip: ")
SendIp = input("Enter send ip: ")
nikname = input("Enter your nikname: ")

"""
Данные для тестов
YourPort = 61985
SendPort = 61984
YourIp = 'localhost'
SendIp = 'localhost'
nikname = 'Morvell'
"""
dataarray.append([YourIp, YourPort])

SRV = Server()
CLT = Client()

t1 = threading.Thread(target=SRV.New_Thread).start()
t2 = threading.Thread(target=CLT.New_Thread).start()
