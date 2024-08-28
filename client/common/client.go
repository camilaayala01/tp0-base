package common

import (
	"bufio"
	"fmt"
	"net"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	NOMBRE 		  string
	APELLIDO 	  string
	DOCUMENTO 	  string
	NACIMIENTO	  string
	NUMERO 		  string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}


// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (c *Client) PlaceBet(){
	c.createClientSocket()
	msg  := fmt.Sprintf("%v%v%v%v%v%v%v%v",c.config.ID, len(c.config.NOMBRE), c.config.NOMBRE, len(c.config.APELLIDO), c.config.APELLIDO, c.config.DOCUMENTO, c.config.NACIMIENTO, c.config.NUMERO)
	n, err := fmt.Fprintf(c.conn, msg)
	var m int
	for err == nil && n < len(msg){
		m, err = fmt.Fprintf(c.conn, msg[n:])
		n += m
	}
	if err != nil {
		log.Errorf("action: apuesta enviada | result: fail | dni: %v | numero: %v | error: %v",
			c.config.DOCUMENTO,
			c.config.NUMERO,
			err,
		)
		return
	}
	res, err := bufio.NewReader(c.conn).ReadString('\n')
	
	c.conn.Close()

	if err != nil || res != "OK\n" {
		log.Errorf("action: apuesta enviada | result: fail | dni: %v | numero: %v  | error: %v",
			c.config.DOCUMENTO,
			c.config.NUMERO,
			err,
		)
		return
	}
	if res != "OK\n" {
		log.Debugf("action: apuesta enviada | result: fail |  dni: %v | numero: %v  | server_response: %v",
			c.config.DOCUMENTO,
			c.config.NUMERO,
			res,
		)
	}

	log.Infof("action: apuesta enviada  | result: success | dni: %v | numero: %v",
		c.config.DOCUMENTO,
		c.config.NUMERO,
	)
	return
}

func (c *Client) Shutdown() {
	log.Infof("action: shutting down | result: in progress | client_id: %v", c.config.ID)
	c.conn.Close()
	log.Infof("action: shutting down | result: success | client_id: %v", c.config.ID)
}
