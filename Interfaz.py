# -*- coding: utf-8 -*-
import random


import os
import sys #para que salga del juego si se cierra la ventana
from paho.mqtt.client import Client
import time
from multiprocessing import Process, Value
from multiprocessing import Manager
from multiprocessing import Lock


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        time.sleep(1)
        print("Conectado al Broker con exito!")
        time.sleep(1)
    else:
        print("No se pudo establecer conexión con el Broker: codigo rc=", rc)
        
def on_subscribe(client, userdata, mid, granted_qos):
    print("Conectado al Channel con exito!") 
    time.sleep(1)
    print("Esperando al Servidor...")
    time.sleep(1)


class Message:

    def __init__(self, cerrar_conexion, manager, password):
        self.conectados = manager
        self.password = password
        self.cerrar_conexion = cerrar_conexion

        
    
    def on_message(self, client, userdata, msg):
            mensaje = str(msg.payload.decode("utf-8"))
            nombre = userdata[0:-8]
            cerrar_conexion = self.cerrar_conexion
                
            if mensaje[0:18] == "SERVIDOR_CONECTADO":
                #cerrar_conexion sirve para no dejar ejecutar el mismo juego en 
                #el cliente dos veces.
                if cerrar_conexion == False:
                    cerrar_conexion = True
                    print(mensaje[18:] + " se ha conectado")
                    self.conectados.append(mensaje[18:])
                    print("--------------------------")
                    print("El juego empieza en...")
                    i = 5
                    while i != 0:
                        print(i,"!")
                        time.sleep(1)
                        i -= 1
                    

            if mensaje[0:4] == "hola":
                print(mensaje[4:] + " se ha conectado")
                self.conectados.append(mensaje[4:])

        
            if mensaje == "EMPEZAR":
                print("PUEBLO DUERME")
                print("--------------------------")
                time.sleep(1)
                print("EL LOBO SE DESPIERTA")

            if mensaje == "dep1":
                print("EL LOBO YA HA ACTUADO")
                time.sleep(1)
                print("EL LOBO VUELVE A DORMIR")
                time.sleep(2)
                print("LA BRUJA SE DESPIERTA")

            if mensaje[0:5] == "witch":
                print("LA BRUJA YA HA ACTUADO")
                time.sleep(1)
                print("LA BRUJA VUELVE A DORMIRSE")


            if mensaje[0:8] == "TERMINAR":
                if mensaje[8] == "N":
                    print("EL PUEBLO SE DESPIERTA")
                    time.sleep(1)
                    print("--------------------------")
                    print("NO HA MUERTO NADIE")
                    time.sleep(1)
                    print("COMIENZA EL DEBATE")
                    print("--------------------------")
                else:
                    print("EL PUEBLO SE DESPIERTA")
                    time.sleep(1)
                    print("--------------------------")
                    print("HA MUERTO ", mensaje[8:])
                    print("COMIENZA EL DEBATE")
                    print("--------------------------")
                    
            
            if mensaje[0:7] == "MENSAJE":
                print(mensaje[7:])
                

            if mensaje[0:5] == "SALIR":
                print(mensaje[5:])


            if mensaje[0:7] == "derecho":
                print(mensaje[7:])

            if mensaje[0:3] == "END":
                print(mensaje[3:])
                
            if mensaje == "ACERTAR":
                print("Habeis dado con el lobo")
                print("Ganan los ciudadanos")
                
            if mensaje == "FALLAR":
                print("No habeis dado con el lobo")
                

            if mensaje[0:5] == "GANAR":
                if mensaje[5:10] == "TOTAL":
                    print("El lobo ha ganado")
                    print("El lobo era: " + mensaje[10:])
                else:
                    print(mensaje[5:])

def main():
    
    
    print("Bienvenido a la interfaz del PUEBLO DUERME")
    print("Esta será tu pantalla de juego")
    
    
    manager = Manager()
    conectados = manager.list()
    
    
    
    print('Ahora crea un codigo para la sala:')    
    print('Todos los participantes deberan conectarse con la misma contraseña')
        
    password = input()        
    
   
    print('Ahora se creará la partida. Todos los jugadores debereis estar conectados a la misma interfaz')
    print("Pasa la contraseña a tus compañeros")
    time.sleep(2)
        
        
        
    cerrar_conexion = False
       
    message = Message(cerrar_conexion, conectados, password)
        
    client_2 = Client(userdata= "chat")
    client_2.enable_logger()
    client_2.on_message = message.on_message
    client_2.on_connect = on_connect
    client_2.on_subscribe = on_subscribe
    client_2.connect("test.mosquitto.org", keepalive=300)
    client_2.subscribe('clients/SleepVillage/'+password + '/chat')
    client_2.publish('clients/SleepVillage/'+password, "Interfaz conectada")
    client_2.loop_forever()
    
    
    
if __name__ == "__main__":
    main()