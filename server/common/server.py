import socket
import logging
import signal
from common.messages import *
from common.utils import *
from threading import Lock, Thread, Condition
import queue

AGENCY_COUNT = 5
class SyncTools:
    def __init__(self):
        self._socket_queue =  queue.Queue()
        self._read_storage_lock = Lock()
        self._write_storage_lock = Lock()
        self._ready_agencies_count_cv = Condition()
        
class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self._ready_agencies = {}
        self._threads = []
        self._sync_tools = SyncTools()

    def graceful_shutdown(self, signum, frame):
        self._running = False
        logging.info("action: shutdown | result: in_progress")
        self._server_socket.close()
        logging.debug("closed server socket")
        self._sync_tools._socket_queue.join() 
        for _ in range(AGENCY_COUNT):
            self._sync_tools._socket_queue.put(None)
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
                self._sync_tools._socket_queue.put(client_sock)
            except OSError as e:
                if self._running:
                    logging.error("action: accept_connections | result: fail | error:" +  str(e))
      
    def ___handle_place_bet(self, client_sock: socket, agency_id: int):
        with self._sync_tools._ready_agencies_count_cv:
            if self._ready_agencies.get(agency_id):
                send_msg(client_sock, MsgType.SERVER_ERR, "Was already notified of end of bets")
        bet_msgs, err = receive_bets(client_sock)
        if err:
            logging.error("action: apuesta_recibida | result: fail | cantidad: " + str(len(bet_msgs)))
            send_msg(client_sock, MsgType.PLACE_BETS_ERR, str(len(bet_msgs))) 
        bets = build_bets(bet_msgs)
        with self._sync_tools._write_storage_lock:
            store_bets(bets)
        logging.debug(f"action: apuesta_recibida | result: success | cantidad: {len(bet_msgs)}")
        send_msg(client_sock, MsgType.PLACE_BETS_OK, str(len(bet_msgs)))
    

    def __handle_results_request(self, client_sock: socket, agency_id: int):
        with self._sync_tools._ready_agencies_count_cv:
            while (not len(self._ready_agencies) == AGENCY_COUNT) and self._running: 
                self._sync_tools._ready_agencies_count_cv.wait()
        if self._running:
            with self._sync_tools._read_storage_lock:
                winners = get_winners_for_agency(agency_id)
            send_msg(client_sock, MsgType.REQ_RESULTS_OK, format_list(winners))

    def __handle_notification(self, agency_id: int):
        with self._sync_tools._ready_agencies_count_cv:
            self._ready_agencies[agency_id] = 1
            if len(self._ready_agencies) == AGENCY_COUNT:
                self._sync_tools._ready_agencies_count_cv.notify_all()
                logging.info("action: sorteo | result: success")
    
    def __process_msg(self, client_sock: socket, agency_id: int):
        msg_type = get_msg_type(client_sock)
        if msg_type < 0:
            raise OSError("Could not get message type")
        logging.debug(f'action: receive_message | result: success | agency {agency_id}')
        if msg_type == MsgType.PLACE_BETS.value:
            self.___handle_place_bet(client_sock, agency_id)
        if msg_type == MsgType.NOTIFY.value:
            self.__handle_notification(agency_id)
        if msg_type == MsgType.REQ_RESULTS.value:
            self.__handle_results_request(client_sock, agency_id)
        client_sock.close()

    def ___handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        while True:
            client_sock = self._sync_tools._socket_queue.get()
            if client_sock is None:
                break
            try:
                agency_id = get_agency_id(client_sock)
                if agency_id < 0:
                    raise OSError("Could not get agency's id")
                self.__process_msg(client_sock, agency_id)
            except OSError as e:
                logging.error("action: receive_message | result: fail | error:" + str(e))
                client_sock.close()
            except ValueError as e:
                logging.error("action: receive_message | result: fail | error:" +  str(e))
                send_msg(client_sock, MsgType.SERVER_ERR, "Could not parse agency's id")
                client_sock.close()
            
            self._sync_tools._socket_queue.task_done()


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
        
