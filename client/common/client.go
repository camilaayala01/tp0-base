package common

import (
	"net"
	"github.com/op/go-logging"
	"encoding/csv"
	"io"
	"os"
	"time"
)

var log = logging.MustGetLogger("log")


// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	MaxBatchSize     int
	ServerAddress string
	Timeout 	time.Duration
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
func BuildBatch(c *Client, reader *csv.Reader)([][]string,error){
	var batch [][]string 
	for i := 0; i < c.config.MaxBatchSize; i++ {
		record, err := reader.Read()
		if err != nil {
			return batch, err
		}
		bet := append([]string{c.config.ID}, record...)
		batch = append(batch,bet)
	}
	return batch, nil

}
func (c *Client)SendNotification()error{
	for{
		if sock_err := c.createClientSocket(); sock_err != nil{
			return sock_err
		}
		err := NotifyServer(c.conn, c.config.ID)
		c.conn.Close()
		if err == nil{
			break
		}
		
	}
	return nil
}
func (c *Client)RequestResponse()error{
	for{
		if sock_err := c.createClientSocket(); sock_err != nil{
			return sock_err
		}
		res, err := AskForResults(c.conn, c.config.ID, c.config.Timeout)
		c.conn.Close()
		if err == nil{
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", res)
			break
		}
		log.Infof("action: consulta_ganadores | result: fail")
	}
	return nil

}


func (c *Client) PlaceBets(){
	file, err := os.Open("betfile.csv") 
      
    if err != nil { 
        log.Criticalf("Error while reading the file %v", err) 
    } 
  
    defer file.Close() 
  
    reader := csv.NewReader(file)
	reader.FieldsPerRecord = FIELDS_TO_READ
	for{
		batch, err := BuildBatch(c, reader)
		log.Debugf("action: build batch  | result: batch de size %v", len(batch))
		if len(batch) > 0 {
			if c.createClientSocket() != nil{
				return  
			}
			send_err := SendBatch(c.conn, batch, c.config.ID)
			if  send_err != nil {
				c.conn.Close()
				log.Criticalf("action: apuesta enviada | result: fail | error: %v",
					send_err,
				)
				return
			}
			log.Infof("action: apuestas enviadas | result: in_progress | cantidad: %v", len(batch))
			response, response_err := receiveServerResponse(c.conn, c.config.Timeout)
			c.conn.Close()
			if response_err != nil {
				log.Errorf("action: apuestas enviadas | result: fail | error: %v",
					response_err,
				)
				return
			}
			
			if response != len(batch) {
				log.Errorf("action: apuestas enviadas | result: fail | enviadas: %v, recibidas: %v",
					len(batch), 
					response,
				)
				return
			}

			log.Infof("action: apuestas enviadas  | result: success | cantidad: %v", response )
		}
		if err == io.EOF{
			break
		}
		if err != nil {
			log.Criticalf("Error while reading records %v", err)
			return
		}
	}
	
	if notify_err := c.SendNotification(); notify_err != nil{
		return
	}
	if response_err := c.RequestResponse(); response_err != nil{
		return
	}

}


func (c *Client) Shutdown() {
	log.Infof("action: shutting down | result: in progress | client_id: %v", c.config.ID)
	c.conn.Close()
	log.Infof("action: shutting down | result: success | client_id: %v", c.config.ID)
}
