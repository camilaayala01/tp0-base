import socket
import logging
import signal
from time import sleep
from common.messages import *
from common.utils import *
from enum import Enum
from threading import Lock, Thread, Condition
import queue
class MsgType(Enum):
    PLACE_BET = 0
    NOTIFY = 1
    REQ_RESPONSE = 2
AGENCY_COUNT = 5
class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._socket_queue =  queue.Queue()
        self._threads = []
        self._running = True
        self._read_storage_lock = Lock() # que es mas correcto, tenerlo aca o en stack y lo paso como arg a funciones? 
        self._write_storage_lock = Lock()
        self._ready_agencies_count_cv = Condition()
        self._ready_agencies_count = 0

    def graceful_shutdown(self, signum, frame):
        self._running = False
        print("running es" ,self._running)
        logging.info("action: shutdown | result: in_progress")
        self._server_socket.close()
        logging.debug("closed server socket")
        self._socket_queue.join() 
        for _ in range(AGENCY_COUNT):
            self._socket_queue.put(None)
        for thread in self._threads:
            thread.join()
        logging.info("action: shutdown | result: success")
    
    def __start_threads(self):
        for _ in range(AGENCY_COUNT):
            thread = Thread(target=self.___handle_client_connection,
                                args=())
            self._threads.append(thread)
            thread.start()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        self.__start_threads()
        
        while self._running:
            try:
                client_sock = self.__accept_new_connection()
                self._socket_queue.put(client_sock)
            except OSError as e:
                if self._running:
                    logging.error("action: accept_connections | result: fail | error: {}",  str(e))
      
    def ___handle_place_bet(self, client_sock: socket):
        bet_msgs, err = receive_bets(client_sock)
        if err:
            logging.error("action: apuesta_recibida | result: fail | cantidad: " +  str(len(bet_msgs)))
            send_error_msg(client_sock, "ERROR: unexpected format in bet number " + str(len(bet_msgs) + 1)) ## cambiar
        bets = build_bets(bet_msgs)
        with self._write_storage_lock:
            store_bets(bets)
        logging.debug(f"action: apuesta_almacenada | result: success | cantidad: " +  str(len(bet_msgs)))
        send_batch_size(client_sock, str(len(bet_msgs)))
    
    def __handle_send_results(self, client_sock: socket, agency_id: int):
        agency_winners = get_winners_for_agency(agency_id, self._read_storage_lock)
        if len(agency_winners) == 0:
            send_no_winners(client_sock)
        send_winners(client_sock, agency_winners)
    
    def __handle_response_request(self, client_sock: socket, agency_id: int):
        logging.info(f"action: request for result | result: in progress | agencia: " +  str(agency_id))
        with self._ready_agencies_count_cv:
            while not self._ready_agencies_count == AGENCY_COUNT and self._running: 
                self._ready_agencies_count_cv.wait()
        if self._running:
            self.__handle_send_results(client_sock, agency_id)
            logging.info(f"action: request for result | result: success | agencia: " +  str(agency_id))

    def __handle_notification(self):
        with self._ready_agencies_count_cv:
            self._ready_agencies_count += 1
            if self._ready_agencies_count == AGENCY_COUNT:
                self._ready_agencies_count_cv.notify_all()
    
    def __process_msg(self, client_sock: socket, agency_id: int):
        try:
            msg_type = get_msg_type(client_sock)
            if msg_type < 0:
                raise OSError("Socket was closed")
            logging.debug(f'action: receive_message | result: success | agency {agency_id}')
            if msg_type == MsgType.PLACE_BET.value:
                self.___handle_place_bet(client_sock)
            if msg_type == MsgType.NOTIFY.value:
                self.__handle_notification()
            if msg_type == MsgType.REQ_RESPONSE.value:
                self.__handle_response_request(client_sock, agency_id)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: OsError " + str(e))
        except ValueError as e:
            logging.error("action: receive_message | result: fail | error:" +  str(e))
            send_error_msg(client_sock, "ERROR " + str(e))
        finally:
            client_sock.close()

    def ___handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        while True:
            client_sock = self._socket_queue.get()
            if client_sock is None:
                break
            try:
                agency_id = get_agency_id(client_sock)
                if agency_id < 0:
                    raise OSError("Socket was closed")
            except OSError as e:
                logging.error("action: receive_message | result: fail | error: OsError " + str(e))
                client_sock.close()
            except ValueError as e:
                logging.error("action: receive_message | result: fail | error:" +  str(e))
                send_error_msg(client_sock, "ERROR " + str(e))
                client_sock.close()
            
            self.__process_msg(client_sock, agency_id)
            self._socket_queue.task_done()


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
        
