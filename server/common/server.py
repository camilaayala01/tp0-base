import socket
import logging
import signal
from common.messages import *
from common.utils import *

AGENCY_COUNT = 5
class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_sockets = {}
        self._is_finished = {}
        self._running = True

    def graceful_shutdown(self, signum, frame):
        self._running = False
        logging.info("action: shutdown | result: in_progress")
        self._server_socket.close()
        logging.debug("closed server socket")
        if len(self._client_sockets) > 0: 
            for addr in self._client_sockets:
                logging.debug("action: shutdown - closing client socket " + str(addr))
                self._client_sockets[addr].close()
        logging.info("action: shutdown | result: success")

    def run(self):
        """
        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                addr = client_sock.getpeername()
                self._client_sockets[addr] = client_sock
                self.__handle_client_connection(client_sock)
                self._client_sockets.pop(addr)
            except OSError as e:
                if self._running:
                    logging.error("action: accept_connections | result: fail | error: {}",  str(e))
    
    
    def __handle_place_bet(self, client_sock, agency_id):
        if self._is_finished.get(agency_id):
            send_msg(client_sock,MsgType.SERVER_ERR, "Was already notified of bet's end")
        bet_msgs, err = receive_bets(client_sock)
        if err:
            logging.error("action: apuesta_recibida | result: fail | cantidad: " +  str(len(bet_msgs)))
            send_msg(client_sock,MsgType.PLACE_BETS_ERR, str(len(bet_msgs)))
        store_bets(build_bets(bet_msgs))
        logging.info(f"action: apuesta_almacenada | result: success | cantidad: " +  str(len(bet_msgs)))
        send_msg(client_sock,MsgType.PLACE_BETS_OK ,str(len(bet_msgs)))
    
    def __handle_send_results(self, agency_id, client_sock):
        agency_winners = get_winners_for_agency(agency_id)
        send_msg(client_sock, MsgType.REQ_RESULTS_OK, format_list(agency_winners))

    def __receive_msg(self, client_sock, agency_id):
        msg_type = get_msg_type(client_sock)
        if msg_type < 0:
            raise OSError("Socket was closed")
        if msg_type == MsgType.PLACE_BETS.value:
            self.__handle_place_bet(client_sock, agency_id)
        if msg_type == MsgType.NOTIFY.value:
            self._is_finished[agency_id] = 1
        if msg_type == MsgType.REQ_RESULTS.value:
            if len(self._is_finished) == AGENCY_COUNT:
                self.__handle_send_results(agency_id, client_sock)
        
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            agency_id = get_agency_id(client_sock)
            if agency_id < 0:
                raise OSError("Socket was closed")
            self.__receive_msg(client_sock, agency_id)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: OsError " + str(e))
        except ValueError as e:
            logging.error("action: receive_message | result: fail | error:" +  str(e))
            send_msg(client_sock, MsgType.SERVER_ERR, str(e))
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
        