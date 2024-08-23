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
            fp.write("name: tp0\nservices:\n\tserver:\n\t\tcontainer_name: server\n\t\timage: server:latest\n\t\tentrypoint: python3 /main.py\n\t\tenvironment:\n\t\t\t- PYTHONUNBUFFERED=1\n\t\t\t- LOGGING_LEVEL=DEBUG\n\t\tnetworks:\n\t\t\t- testing_net\n\n")
            client_count = int(sys.argv[2])
            for i in range(1,client_count+1):
                fp.write("client"+str(i)+":\n\tcontainer_name: client"+str(i)+"\n\timage: client:latest\n\tentrypoint: /client\n\tenvironment:\n\t\t- CLI_ID="+str(i)+"\n\t\t- CLI_LOG_LEVEL=DEBUG\n\tnetworks:\n\t- testing_net\n\tdepends_on:\n\t- server\n\n")
            fp.write("networks:\n\ttesting_net:\n\t\tipam:\n\t\t\tdriver: default\n\t\t\tconfig:\n\t\t\t\t- subnet: 172.25.125.0/24\n")
    
    fp.close()  
if __name__ == "__main__":
    main()
    
