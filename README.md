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
Siendo estos los valores que tome como maximos en cada campo por lo cual cada paquete tiene como maximo 64 bytes:
1 byte longitud agencia + 3 bytes de numero de agencia + 1 byte de longitud de nombre + 23 bytes de nombre + 1 byte de longitud de apellido + 10 bytes de apellido +
10 bytes de nacimiento + 8 bytes de documento + 4 bytes de numero
El numero de agencia se envia como string asi que 3 bytes le permitiria tener como maximo 999. 

Hay 78.697 apuestas