package common

import (
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
		return err
	}
	c.conn = conn
	return nil
}

func (c *Client) PlaceBet(){
	if c.createClientSocket() != nil{
		return  
	}
	send_err:= SendMsg(c.conn,[]string{c.config.ID,c.config.NOMBRE,c.config.APELLIDO, c.config.DOCUMENTO, c.config.NACIMIENTO, c.config.NUMERO})
	if  send_err != nil {
		log.Errorf("action: apuesta enviada | result: fail | dni: %v | numero: %v | error: %v",
			c.config.DOCUMENTO,
			c.config.NUMERO,
			send_err,
		)
		return
	}
	response_err := receiveServerResponse(c.conn)
	
	c.conn.Close()

	if response_err != nil {
		log.Errorf("action: apuesta enviada | result: fail | dni: %v | numero: %v  | error: %v",
			c.config.DOCUMENTO,
			c.config.NUMERO,
			response_err,
		)
		return
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
