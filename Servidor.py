# -*- coding: utf-8 -*-
import random


import os
import sys #para que salga del juego si se cierra la ventana
from paho.mqtt.client import Client
import time
from multiprocessing import Process, Value
from multiprocessing import Lock
from multiprocessing import Manager
from ctypes import c_char_p
#-----------------------------------------------------------------------------

#La funcion personajes distribuye aleatoriamente el lobo, la bruja y los ciudadanos entre los jugadores que haya conectados

def personajes(n):
        lista = []
        for i in range(n-2):
            lista.append("Ciudadano")

        lista.insert(random.randint(0,n-2), "Lobo")
        lista.insert(random.randint(0,n-1), "Bruja")
        return lista

#La funcion encontrar maximo te devuelve el elemento que mas se repite en una lista, para las votaciones finales.
#Si hay empate devuelve un False

def encontrar_maximo(lst): 
    lista_duplas = []
    for elem in lst:
        lista_duplas.append((elem, lst.count(elem)))
       
    a1 = set(lista_duplas)
    lista_duplas = list(a1)
    
    
    lista = []
    for i in range(len(lista_duplas)):
        lista.append(lista_duplas[i][1])
    
    maximo = max(lista)
    if lista.count(maximo) > 1:
        return False
    else:
        return lista_duplas[lista.index(maximo)][0]


"""
on_message está definido como una clase por la facilidad que supone
    su implementacion para transferir monitores y semaforos que entrarian en 
    juego al recibir un mensaje, y así poder pasarlos a más de un proceso.
 """

  
#Definimos la clase Message por facilidad de transferir los elementos

class Message():
    def __init__(self, manager, manager1, manager2, manager3, manager4, numero, bruja, contador):
        self.conectados = manager
        self.no_conectados = manager1
        self.conectados1 = manager3
        self.quieren_votar = Value('i', 0)
        self.votaciones = manager4
        self.numero = numero
        self.bruja = bruja
        self.contador = contador
        self.lista = personajes(self.numero.value)
  
  
    def on_message(self, client, userdata, msg, ):
        mensaje = str(msg.payload.decode("utf-8"))
        print("El mensaje que llega es: " + mensaje)
        topic = msg.topic
        password = topic[21:]
        userdata_short = mensaje[0:-19]
        #userdata_short devuelve el nombre del usuario
        userdata_medium = mensaje[0:-18]
        #userdata_medium devuelve el nombre del usuario y su numero de usuario
        numero = mensaje[-18:-17]
        #numero devuelve el numero del usuario
        #Viene bien definir el numero para saber a que hilo dentro del servidor al que está subscrito

        userdata_long = mensaje[0:-10]
        #userdata_long para saber el tipo de cliente que entra y su direccion         
        
        """
        Aquí se detallan todos los posibles mensajes que se pueden recibir: hola
        """

        if mensaje[-17:] == "Cliente.conectado":
            self.conectados.append(userdata_short)
            self.conectados1.append(userdata_medium)
            if len(self.conectados) == self.numero.value:
                client.publish('clients/SleepVillage/'+password+ '/chat', "SERVIDOR_CONECTADO" + userdata_short)
                for i in range(self.numero.value):
                    print(self.lista)
                    client.publish('clients/SleepVillage/'+password+ '/' + str((i+1)), 'SERVIDOR_CONECTADO')
            else:
                client.publish('clients/SleepVillage/'+password+ '/chat', "hola" + userdata_short)
            
        if mensaje == "hello":
            self.contador.value += 1
            if self.contador.value == len(self.conectados):
                client.publish('clients/SleepVillage/'+password+ '/chat', 'EMPEZAR')
                for i in range(self.numero.value):
                    client.publish('clients/SleepVillage/'+password+ '/' + str((i+1)), 'EMPEZAR')
                self.contador.value = 0
            
            
                
            
        #Solo enviamos el mensaje LOBO al cliente que coincida con el indice de la lista de personajes de lobo
        
        if mensaje == "wolf":
            self.contador.value += 1
            if self.contador.value == len(self.conectados):
                print(str((self.lista.index("Lobo") + 1)))
                client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Lobo") + 1)), 'LOBO')
                self.contador.value = 0
            
        if mensaje[0:6] == "muerto":
            time.sleep(1)
            if mensaje[6:] in self.conectados:
                self.no_conectados.append(mensaje[6:])
                self.conectados.remove(mensaje[6:])
                client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Lobo") + 1)), 'dep1')
                client.publish('clients/SleepVillage/'+password+ '/chat', 'dep1')
                for i in range(len(self.conectados1)):
                        client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), 'CONTINUAR')
                
            else: 
                client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Lobo") + 1)), 'dep2')
                
        #Solo enviamos el mensaje al cliente que coincida con el indice de la bruja en la lista de personajes
        #En el caso de la bruja ya haya actuado, pasamos directamente al chat

        if mensaje == "BRUJA":
            self.contador.value += 1
            if self.contador.value == self.numero.value:
                if self.bruja.value == 0 and self.conectados1[self.lista.index("Bruja")][0:-1] in self.conectados:
                    client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Bruja") + 1)), 'local'+ self.no_conectados[(len(self.no_conectados) - 1)])
                else:
                    client.publish('clients/SleepVillage/'+password, "FINALIZARS")
                    
                self.contador.value = 0
        
        if mensaje[0:6] == "opcion":
            if mensaje[6] == '1':
                self.bruja.value = 1
                self.conectados.append(self.no_conectados[(len(self.no_conectados) - 1)])
                self.no_conectados.remove(self.no_conectados[(len(self.no_conectados) - 1)])
                client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Bruja") + 1)), 'witch1')
                client.publish('clients/SleepVillage/'+password+ '/chat', 'witch1')                
            elif mensaje[6] == '2':
                client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Bruja") + 1)), 'witch2')
                client.publish('clients/SleepVillage/'+password+ '/chat', 'witch2') 
            else:
                client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Bruja") + 1)), 'witch3')
                client.publish('clients/SleepVillage/'+password+ '/chat', 'witch3') 
                
            
        if mensaje[0:9] == "FINALIZAR":
            if mensaje[9] == "N":
                for i in range(self.numero.value):
                    client.publish('clients/SleepVillage/'+password+ '/' + str((i+1)), 'TERMINARN')
                client.publish('clients/SleepVillage/'+password+ '/chat', 'TERMINARN') 
            else:
                for i in range(self.numero.value):
                    client.publish('clients/SleepVillage/'+password+ '/' + str((i+1)), 'TERMINAR' + self.no_conectados[(len(self.no_conectados) - 1)])
                client.publish('clients/SleepVillage/'+password+ '/chat', 'TERMINAR' + self.no_conectados[(len(self.no_conectados) - 1)]) 
                
             
        #Mandamos mensajes distintos a los vivos y a los muertos. Nos ayudamos de userdata_medium en self.conectados1 para mandar el mensaje 
        #al hilo especifico de cada cliente.
            
        if mensaje == "cliente":
            self.contador.value += 1
            if self.contador.value == len(self.conectados1):
                for i in range(len(self.conectados1)):
                    if (self.conectados1[i][0:(len(self.conectados1[i]) - 1)]) in self.conectados:
                        client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), 'CHAT_VIVOS')
                    else:
                        client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), 'CHAT_MUERTOS')
                self.contador.value = 0
                

        if mensaje[0:6] == "nombre":
                client.publish('clients/SleepVillage/'+password+ '/chat', 'MENSAJE' + mensaje[7:])
                client.publish('clients/SleepVillage/'+password+ '/' + mensaje[6], 'CHAT_VIVOS')
        
        if mensaje[0:10] == "Votaciones":
            self.quieren_votar.value += 1
            if self.quieren_votar.value == len(self.conectados):
                client.publish('clients/SleepVillage/'+password+ '/' + mensaje[10], "CHAT_VOTA")
                client.publish('clients/SleepVillage/'+password+ '/chat', "SALIR" + "***" + mensaje[11:] + " ha salido del chat y va a votar***")
                for i in range(len(self.conectados1)):
                    if (self.conectados1[i][0:(len(self.conectados1[i]) - 1)]) in self.conectados:
                        client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), "Sufragio")
                self.quieren_votar.value = 0
            else:
                client.publish('clients/SleepVillage/'+password+ '/' + mensaje[10], "CHAT_VOTA")
                client.publish('clients/SleepVillage/'+password+ '/chat', "SALIR" + "***" + mensaje[11:] + " ha salido del chat y va a votar***")
                
        
        if mensaje[0:5] == "FINAL":
            if mensaje[6:] in self.conectados:
                client.publish('clients/SleepVillage/'+password+ '/' + mensaje[5], "SufragioSI" + mensaje[6:])
                self.votaciones.append(mensaje[6:])
                if len(self.votaciones) == len(self.conectados):
                    maximo = encontrar_maximo(self.votaciones)
                    if maximo != False:
                        self.conectados.remove(maximo)
                        self.numero.value -= 1
                        self.no_conectados.append(maximo)
                        time.sleep(2)
                        client.publish('clients/SleepVillage/'+password+ '/chat', "END" + "La persona mas votada es: " + maximo)
                        client.publish('clients/SleepVillage/'+password+ '/' + str((self.lista.index("Lobo") + 1)), "COMPROBAR" + maximo)
                        for i in range(len(self.conectados1)):
                            if (self.conectados1[i][0:(len(self.conectados1[i]) - 1)]) == maximo:
                                client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), 'COMPROBAR' + 'ELECCION')
                        self.votaciones = []
                    else:
                        client.publish('clients/SleepVillage/'+password+ '/chat', "END" + "Hay un empate en los votos. No muere nadie")
                        client.publish('clients/SleepVillage/'+password, "CHECKNO")
                        client.publish('clients/SleepVillage/'+password+ '/chat', "EMPEZAR")
                        for i in range(len(self.conectados1)):
                            if (self.conectados1[i][0:(len(self.conectados1[i]) - 1)]) in self.conectados:
                                client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), "EMPEZAR")
                        self.votaciones = []
            else:
                client.publish('clients/SleepVillage/'+password+ '/' + mensaje[5], "SufragioNO")


        if mensaje[0:5] == "PASAR":
            client.publish('clients/SleepVillage/'+ password + '/chat', "derecho" + mensaje[5:])
                        
        if mensaje[0:5] == "CHECK":
            if mensaje[5:] == "SI":
                client.publish('clients/SleepVillage/'+password+ '/chat', "ACERTAR")
            else:
                client.publish('clients/SleepVillage/'+password+ '/chat', "FALLAR")
                if len(self.conectados) <= 2:
                    client.publish('clients/SleepVillage/'+password+ '/chat', "GANARTOTAL" + self.conectados1[(self.lista.index("Lobo"))][0:-1])
                else:
                    client.publish('clients/SleepVillage/'+password+ '/chat', "GANAREL JUEGO CONTINUA")
                    time.sleep(1)
                    client.publish('clients/SleepVillage/'+password+ '/chat', "EMPEZAR")
                    for i in range(len(self.conectados1)):
                        if (self.conectados1[i][0:(len(self.conectados1[i]) - 1)]) in self.conectados:
                            client.publish('clients/SleepVillage/'+password+ '/' + (self.conectados1[i][-1]), "EMPEZAR")
        
            
def on_connect(server, userdata, flags, rc):
    print("Servidor conectado al Broker!")
    time.sleep(1)
def on_subscribe(server, userdata, mid, granted_qos):
    print("Servidor conectado al Channel!")
    time.sleep(0.5)
    print("Esperando confirmacion de Clientes...")
    time.sleep(1)
#-----------------------------------------------------------------------------

def main(numero_personas):
    numero = Value('i', int(numero_personas))
    bruja = Value('i', 0)
    contador = Value('i', 0)
    manager = Manager()
    conectados = manager.list()
    manager1 = Manager()
    no_conectados = manager1.list()
    manager2 = Manager()
    lista = manager2.list
    manager3 = Manager()
    conectados1 = manager3.list()
    manager4 = Manager()
    votaciones = manager4.list()
    message = Message(conectados, no_conectados, lista, conectados1, votaciones, numero, bruja, contador)
    server = Client(userdata="Server")
    server.enable_logger()
    server.on_message = message.on_message
    server.on_connect = on_connect
    server.on_subscribe = on_subscribe
    server.connect("test.mosquitto.org")
    server.subscribe('clients/SleepVillage/#')
    server.loop_forever()

if __name__ == "__main__":
    numero_personas = input("Introduce el número de jugadores: ")
    main(numero_personas)
#-----------------------------------------------------------------------------
