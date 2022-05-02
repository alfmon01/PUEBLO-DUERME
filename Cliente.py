# -*- coding: utf-8 -*-
import random

#te importa constantes de pygame que reconocen teclas del teclado
import os
import sys #para que salga del juego si se cierra la ventana
from paho.mqtt.client import Client
import time
from multiprocessing import Process, Value
from multiprocessing import Manager
from multiprocessing import Lock
from ctypes import c_char_p
#--------------------------------------


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

    #Definimos la clase mensaje por facilidad de transmision de mensajes
    
class Message:

    def __init__(self, cerrar_conexion, manager, password, string_chat, semaforo):
        self.conectados = manager
        self.password = password
        self.string_chat = string_chat
        self.semaforo = semaforo

        
        self.cerrar_conexion = cerrar_conexion
            
        
        
    def on_message(self, client, userdata, msg):
        mensaje = str(msg.payload.decode("utf-8"))
        
        nombre = userdata[0:-8]
        
        cerrar_conexion = self.cerrar_conexion
        password = self.password
            
        if mensaje[0:18] == "SERVIDOR_CONECTADO":
            #cerrar_conexion sirve para no dejar ejecutar el mismo juego en 
            #el cliente dos veces.
            print("Comieza el juego")
            client.publish('clients/SleepVillage/'+self.password, "hello")
                
        
        if mensaje == "EMPEZAR":
            client.publish('clients/SleepVillage/'+self.password, "wolf" )
        
        if mensaje == "LOBO":
            print("ERES EL LOBO. ¿A QUIEN QUIERES MATAR?")
            muerto = input()
            time.sleep(1)
            if muerto == nombre:
                print("No puedes matarte a ti mismo")
                client.publish('clients/SleepVillage/'+self.password + '/' + userdata[-1], "LOBO")
            else:
                client.publish('clients/SleepVillage/'+self.password, "muerto" + muerto)
            
        if mensaje == "dep1":
            print("El jugador que has elegido ha sido eliminado")
        if mensaje == "dep2":
            print("El jugador que has elegido ya ha muerto o no existe. Elige otro: ")
            client.publish('clients/SleepVillage/'+self.password + '/' + userdata[-1],  "LOBO")
        
        if mensaje == "CONTINUAR":
            client.publish('clients/SleepVillage/'+self.password, "BRUJA")
       
        if mensaje[0:5] == "local":
                print("ERES LA BRUJA")
                print("Ha muerto ", mensaje[5:])
                print("Tienes dos opciones:")



                print("1. Revivir a la persona que ha muerto")

                print("2. No hacer nada")

                print("Elige el numero de la opcion que quieras: ")
                numero = input()
                if numero == "1":
                    client.publish('clients/SleepVillage/'+self.password, "opcion"+numero)
                elif numero == "2":
                    client.publish('clients/SleepVillage/'+self.password, "opcion"+numero)
                    
                else:
                    print("La opcion que has elegido no esta entre las opciones")
                    client.publish('clients/SleepVillage/'+self.password + '/' + userdata[-1], "local" + mensaje[5:])

         
                
        if mensaje[0:5] == "witch":
            if mensaje[5] == '1':
                print("Has decidido revivir a la persona que ha muerto")
                client.publish('clients/SleepVillage/'+self.password, "FINALIZARN")
            elif mensaje[5] == '2':
                print("Has decidido no hacer nada")
                client.publish('clients/SleepVillage/'+self.password, "FINALIZARS")
            else:
                print("Ya has actuado antes. Ya no puedes")
                
                
        if mensaje[0:8] == "TERMINAR":
                client.publish('clients/SleepVillage/'+self.password, "cliente")
            
        
        
        if mensaje[0:4] == "CHAT":
            if mensaje[4:] == "_VIVOS":
                    chat=input("Escribe (Cuando quieras votar escribe 'votar'): ")
                    if (chat == "VOTAR") or (chat == "votar"):
                        client.publish('clients/SleepVillage/'+self.password, "Votaciones" + userdata[-1] + nombre)
                    else:
                        client.publish('clients/SleepVillage/'+self.password, "nombre" + userdata[-1] + nombre + ": " + chat)
                    
            elif mensaje[4:] == "_VOTA":
                print("Espera a que los demas tambien quieran votar")
            else:
                print("Estas en el chat de los muertos")
                print("No puedes escribir, estas muerto")



        if mensaje[0:8] == "Sufragio":
                if mensaje[8:10] == "SI":
                    client.publish('clients/SleepVillage/'+self.password, "PASAR" + nombre + " ha votado a " + mensaje[10:])
                elif mensaje[8:] == "NO":
                    print("Esa persona no existe")
                    time.sleep(1)
                    print("Elige quien crees que es el lobo")
                    lobo = input()
                    client.publish('clients/SleepVillage/'+self.password, "FINAL" + userdata[-1] + lobo)
                else:     
                    print("Elige quien crees que es el lobo")
                    lobo = input()
                    client.publish('clients/SleepVillage/'+self.password, "FINAL" + userdata[-1] + lobo)            
        

        if mensaje[0:9] == "COMPROBAR":
            if mensaje[9:] == nombre:
                print("Te han pillado")
                client.publish('clients/SleepVillage/'+self.password, "CHECKSI") 
            elif mensaje[9:] == "ELECCION":
                print("Estas muerto por votacion popular")
            else:
                print("Te has salvado")
                client.publish('clients/SleepVillage/'+self.password, "CHECKNO")
            
      





        


def main():
    
    
    print("Bienvenido a PUEBLO DUERME")
    print("Escribe tu nombre")
    apodo_client = input()
    
  
    print("Tienes dos opciones:")
    print("Puedes crear una partida y serás el jugador numero uno")
    print("O puedes unirte a una partida, eligiendo un numero de jugador entre 2 y el numero de personas que seais (maximo 9)")
    print("En ambos casos debes poner la contraseña de la interfaz")
    print("Escribe C para crear a una partida, o U para unirte a una partida")
    
    opcion = input()
    manager = Manager()
    conectados = manager.list()
    string_chat = manager.Value(c_char_p, "")
    semaforo = Lock()
    
    #Opcion de crear la sala, numero de jugador = 1
    if opcion == "C" or opcion == "c": 
        print('Muy bien! Introduce la contraseña de la interfaz')     
        
        password = input()      

       
        print('Ahora se creará la partida. Asegurate de pasar la contraseña correcta a tu rival para jugar')
        time.sleep(2)
        
        
        
        cerrar_conexion = False
       
        message = Message(cerrar_conexion, conectados, password, string_chat, semaforo)
        
        client_2 = Client(userdata=(apodo_client+".client1"))
        client_2.enable_logger()
        client_2.on_message = message.on_message
        client_2.on_connect = on_connect
        client_2.on_subscribe = on_subscribe
        client_2.connect("test.mosquitto.org", keepalive=300)
        client_2.subscribe('clients/SleepVillage/'+password + '/1')
        client_2.publish('clients/SleepVillage/'+password, apodo_client + '1.Cliente.conectado')
        client_2.loop_forever()
    
    #Opcion de unirse a partida. Hay que añadir el numero de jugador para que cada cliente se conecte a un hilo distinto
    #para que cada uno reciba mensajes distintos en funcion del desarrollo del juego
    
    elif opcion == "U" or opcion == "u":
        print('Introduce el código de la sala:')
        
        password = input()
        print ('Que numero de jugador eres')
        
        numero = input()
        print('Buscando salas con este codigo...')
        
        
        
        cerrar_conexion = False
        
        message = Message(cerrar_conexion, conectados, password, string_chat, semaforo)
        
        client_1 = Client(userdata=apodo_client+".client" + numero)
        client_1.enable_logger()
        client_1.on_message = message.on_message
        client_1.on_connect = on_connect
        client_1.on_subscribe = on_subscribe
        client_1.connect("test.mosquitto.org", keepalive=300)
        client_1.subscribe('clients/SleepVillage/'+password + '/' + numero)
        client_1.publish('clients/SleepVillage/'+password, apodo_client + numero + "." + 'Cliente.conectado')
        client_1.loop_forever()
    else:
        print('Parece que no has elegido ninguna opcion. ¡Hasta pronto!')
        sys.exit(0)
    
    
if __name__ == "__main__":
    main()
    
