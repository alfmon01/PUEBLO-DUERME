# PUEBLO-DUERME

Trabajo realizado por Alfonso Montalvo para la asignatura de Programación Paralela.


INSTRUCCIONES DE USO
----------------------
1. En primer lugar, se ejecuta el servidor y espera la llegada de clientes. También eliges el numero de jugadores que quieres que juegen entre 4 y 9.
2. Se ejecuta la interfaz donde te pedirán una contraseña. Todos los clientes se conectan a la misma interfaz con la misma contraseña. Se pueden abrir tantas interfaces como se desee
3. Ejecutar los clientes utilizando la misma contraseña que la interfaz y escribiendo un nombre propio. Además debes elegir el numero de jugador que eres en caso de que te unas a la partida entre 2 y el numero total. El primer cliente que se conecte creará la partida y será el jugador 1 automaticamente.
4. Disfrute del juego


JUEGO
-------
Hay varios roles en el juego:
 - Puedes ser el lobo y tienes que eliminar a los demás.
 - Puedes ser la bruja y tienes la capacidad de salvar a alguien una vez por partida.
 - Puedes ser ciudadano y debes intentar encontrar al lobo.

Después de actuar el lobo y la bruja, comienza un chat en el que se procede a una votación cuando todos los jugadores lo decidan.
El jugador más votado será eliminado. Si hay empate, no se elimina a nadie y el juego vuelve a proceder.
El juego acaba cuando el lobo elimina a todos los demás o los ciudadanos pillan al lobo.
