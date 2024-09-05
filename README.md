# TP0: Docker + Comunicaciones + Concurrencia

### Parte 1
Para poder correr el script  **generar-compose.sh** debe otorgarsele permisos con 
```
chmod +rwx generar-compose.sh
```
Para poder correr el script  **validar-echo-server.sh** debe otorgarsele permisos con 
```
chmod +rwx validar-echo-server.sh
```

### Parte 2 
Para mantener los paquetes de un tamanio menor a 8kb necesito acotar el tamanio del nombre y apellido. Para asegurarme que mi programa sea compatible con los datos proveidos busque los maximos usando:
```
unzip dataset.zip -d dataset
cd dataset| cat *.csv | cut -d "," -f 1  | sort | uniq | awk '{print length, $0}' | sort -nr | head -n 1
cd dataset| cat *.csv | cut -d "," -f 2  | sort | uniq | awk '{print length, $0}' | sort -nr | head -n 1
```
Obteniendo
```
23 Milagros De Los Angeles
10 Valenzuela
```

# TP0: Docker + Comunicaciones + Concurrencia

### Parte 1
Para poder correr el script  **generar-compose.sh** debe otorgarsele permisos con 
```
chmod +rwx generar-compose.sh
```
Para poder correr el script  **validar-echo-server.sh** debe otorgarsele permisos con 
```
chmod +rwx validar-echo-server.sh
```

### Parte 2
#### Documentacion protocolo:
Los campos de una apuesta son: 
    Nombre: longitud variable, como maximo 255
    Apellido: longitud variable, como maximo 255
    Documento: 8 digitos 
    Nacimiento: 10 digitos, formato YYYY-MM-DD
    Numero: 4 digitos
En el cliente solo se chequea que todas las longitudes entren en la cantidad de bytes asignados para la longitud. 
Se construye el mensaje de una apuesta precediendo a cada campo con su longitud en Big Endian. 
Una vez que se tiene el mensaje en bytes se lo envia todo junto por el socket y se mantiene en un bucle hasta que todos hayan sido enviados para evitar un short write

Del lado del servidor se conoce la cantidad de campos a recibir (en este caso 6) y se lee primero la cantidad de bytes asignados para la longitud (en mi caso tome 1). Se intenta leer del socket esa cantidad de bytes para llenar un campo. Una vez que se llenan los campos se devuelven. En este caso tuve problemas para verificar el short read ya que en python si el socket es cerrado del otro lado no se lanza una excepcion sino que se te avisa devolviendo en el recv() un string vacio. Decidi que si leo 0 bytes salgo pero si leo mas de 0 y menos de lo necesario sigo intentando. 
Agregue en el almacenamiento de la apuesta que se verifique el tamanio del documento. 
Si todo sale bien el server responde con un mensaje de exito que el cliente conoce (lo defini como "OK")
Si el cliente recibe algo distinto a ese mensaje sabe que hubo un error y va a loggear lo que el servidor le mando, que sera del tipo "ERROR: {error que sucedio}"

### Cambios en el protocolo de ej6:
Se envia al servidor una cantidad de apuestas que va a haber en el batch y las apuestas.
Ahora el servidor responde con la cantidad de apuestas que pudo almacenar. El cliente compara lo recibido con la cantidad enviada y asi determina si hubo o no un error. Si se envia un -1 es porque hubo un ValueError en el server lo cual implica que el formato de alguna apuesta era incorrecto.

### Definicion de batch.maxAmount:

Siendo estos los valores que tome como maximos en cada campo por lo cual cada paquete tiene como *maximo 64 bytes*:
    1 byte longitud agencia + 3 bytes de numero de agencia + 1 byte de longitud de nombre + 23 bytes de nombre + 1 byte de longitud de apellido + 10 bytes de apellido +
    10 bytes de nacimiento + 8 bytes de documento + 4 bytes de numero
    El numero de agencia se envia como string asi que 3 bytes le permitiria tener como maximo 999. 
Por lo cual defini batch.maxAmount = 125 (8000 % 64)
