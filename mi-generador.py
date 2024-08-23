import sys

def main(): 
    if len(sys.argv) != 3 or not(sys.argv[2].isnumeric):
        print("Uso ./generar-compose.sh <archivo de output> <Cantidad de clientes>")
    output_file = sys.argv[1]
    try:
        fp = open(output_file,mode="w+")
    except PermissionError:
        print("No se cuenta con los permisos para editar ese archivo")
        return -1
    else:
        with fp:
            fp.write("name: tp0\nservices:\n  server:\n    container_name: server\n    image: server:latest\n    entrypoint: python3 /main.py\n    environment:\n      - PYTHONUNBUFFERED=1\n      - LOGGING_LEVEL=DEBUG\n    networks:\n      - testing_net\n\n")
            client_count = int(sys.argv[2])
            for i in range(1,client_count+1):
                fp.write("  client"+str(i)+":\n    container_name: client"+str(i)+"\n    image: client:latest\n    entrypoint: /client\n    environment:\n      - CLI_ID="+str(i)+"\n      - CLI_LOG_LEVEL=DEBUG\n    networks:\n      - testing_net\n    depends_on:\n      - server\n\n")
            fp.write("networks:\n  testing_net:\n    ipam:\n      driver: default\n      config:\n        - subnet: 172.25.125.0/24\n")
    
    fp.close()  
if __name__ == "__main__":
    main()
    
