import socket
import logging
import signal
from time import sleep
from common.messages import *
from common.utils import *
class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_sockets = {}
        self.running = True

    def graceful_shutdown(self, signum, frame):
        self.running = False
        logging.info("action: shutdown | result: in_progress")
        self._server_socket.close()
        logging.info("closed server socket")
        if len(self._client_sockets) > 0: 
            for addr in self._client_sockets:
                print("action: shutdown - closing client socket " + str(addr))
                self._client_sockets[addr].close()
        logging.info("action: shutdown | result: success")

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        while self.running:
            try:
                client_sock = self.__accept_new_connection()
                addr = client_sock.getpeername()
                self._client_sockets[addr] = client_sock
                self.__handle_client_connection(client_sock)
                self._client_sockets.pop(addr)
            except OSError as e:
                if self.running:
                    logging.error("action: accept_connections | result: fail | error: {}",  str(e))
        
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            [agency, name, lastname, dni,birthdate, number] = receive_msg(client_sock)
            addr = client_sock.getpeername()
            logging.debug(f'action: receive_message | result: success | ip: {addr[0]} | name: {name}')
            store_bets([Bet(agency,name,lastname,dni, birthdate, number)])
            logging.info(f"action: apuesta_almacenada | result: success | dni: {dni} | numero: {number}")
            send_msg(client_sock, "OK\n")
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: OsError " + str(e))
        except ValueError as e:
            logging.error("action: receive_message | result: fail | error:" +  str(e))
            send_msg(client_sock, "ERROR " + str(e) + "\n")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
        
