import socket
import logging
import signal
from time import sleep

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
        logging.info("Closing server socket")
        self._server_socket.close()
        logging.info("There are "+str(len(self._client_sockets))+" open client sockets")
        for addr in self._client_sockets:
            print("Closing connection to" + str(addr))
            self._client_sockets[addr].close()
        

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        while self.running:
            try:
                client_sock, addr = self.__accept_new_connection()
                self._client_sockets[addr] = client_sock
                self.__handle_client_connection(client_sock)
                self._client_sockets.pop(addr)
            except OSError as e:
                if self.running:
                    logging.error("action: accept_connections | result: fail | error: {e}")
        
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
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
        return c, addr
        
