# TP0: Docker + Comunicaciones + Concurrencia
# Parte 1
Para poder correr el script  **generar-compose.sh** debe otorgarsele permisos con 
```
chmod +rwx generar-compose.sh
```
Para poder correr el script  **validar-echo-server.sh** debe otorgarsele permisos con 
```
chmod +rwx validar-echo-server.sh
```

# Parte 2
### Documentacion protocolo:
Los campos de una apuesta son: 
 - Nombre: longitud variable, como maximo 255
- Apellido: longitud variable, como maximo 255
- Documento: 8 digitos 
- Nacimiento: 10 digitos, formato YYYY-MM-DD
- Numero: 4 digitos

En el cliente solo se chequea que todas las longitudes entren en la cantidad de bytes asignados para la longitud. 
Se construye el mensaje de una apuesta precediendo a cada campo con su longitud en Big Endian. 

Una vez que se tiene el mensaje en bytes se lo envia todo junto por el socket y se mantiene en un bucle hasta que todos hayan sido enviados para evitar un short write

Del lado del servidor se conoce la cantidad de campos a recibir (en este caso 6) y se lee primero la cantidad de bytes asignados para la longitud (en mi caso tome 1). 

Se intenta leer del socket esa cantidad de bytes para llenar un campo. Una vez que se llenan los campos se devuelven.

En este caso tuve problemas para verificar el short read ya que en python si el socket es cerrado del otro lado no se lanza una excepcion sino que se te avisa devolviendo en el recv() un string vacio. Decidi que si leo 0 bytes salgo pero si leo mas de 0 y menos de lo necesario sigo intentando. 

Agregue en el almacenamiento de la apuesta que se verifique el tamanio del documento. 

Si todo sale bien el server responde con un mensaje de exito que el cliente conoce (lo defini como "OK")

Si el cliente recibe algo distinto a ese mensaje sabe que hubo un error y va a loggear lo que el servidor le mando, que sera del tipo "ERROR: {error que sucedio}"
