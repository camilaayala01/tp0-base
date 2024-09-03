package common
import (
    "encoding/binary"
	"net"
	"fmt"
	"bytes"
	"bufio"
	"strconv"
	"strings"
)
const EXPECTED_REPLY string = "OK\n"
const DELIMITER byte = '\n'
const UINT8_MAX = 255
const (
	PLACE_BETS = iota
	NOTIFY 
	REQ_RESULTS
)
func GetMsgType(msg_type: int){
	buf := new(bytes.Buffer)
	if err := binary.Write(buf, binary.BigEndian, uint8(msg_type)); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}
func BuildMsg(fields []string)([]byte,error){
	buf := new(bytes.Buffer)
	for _, field := range fields {
		if len(field) > UINT8_MAX{
			return nil, fmt.Errorf("Length must be 255 or less")
		}
		if err := binary.Write(buf, binary.BigEndian, uint8(len(field))); err != nil {
			return nil, err
		}
		if err := binary.Write(buf, binary.BigEndian, []byte(field)); err != nil {
			return nil, err
		}
	}
	return buf.Bytes(), nil
}

func GetBatchLen(batch_len int)([]byte,error){
	buf := new(bytes.Buffer)
	if batch_len > UINT8_MAX{
		return nil, fmt.Errorf("Batch Length must be 255 or less")
	}
	if err := binary.Write(buf, binary.BigEndian, uint8(batch_len)); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func SendBatch(sock net.Conn, batch [][]string) error{
	var buffer []byte
	msg_type, msg_type_err := GetMsgType(PLACE_BETS)
	if msg_type_err != nil{
		return msg_type_err
	}
	buffer = append(buffer, msg_type...)
	batch_len, batch_len_err := GetBatchLen(len(batch))
	if batch_len_err != nil{
		return batch_len_err
	}
	buffer = append(buffer, batch_len...)
	for _, bet := range batch{
		bet_msg, build_err := BuildMsg(bet)
		if build_err != nil{
			return fmt.Errorf("Could not encode bet record:%v Error: %v", bet, build_err)
		}
		buffer = append(buffer,bet_msg...)
	}
	return SendMsg(sock, buffer)
}

func NotifyServer(sock net.Conn) error{
	var buffer []byte
	msg_type, msg_type_err := GetMsgType(NOTIFY)
	if msg_type_err != nil{
		return msg_type_err
	}
	buffer = append(buffer, msg_type...)
	return SendMsg(sock, buffer)
}

//func RequestResults(sock net.Conn)
func SendMsg(sock net.Conn, msg []byte)error{
	n, err := sock.Write(buffer)
	var m int
	for err == nil && n < len(msg) {
		m, err = sock.Write(msg[n:len(msg)])
		n += m
	}
	return err
}

func receiveServerResponse(sock net.Conn)(int,error){
	response, read_err := bufio.NewReader(sock).ReadString(DELIMITER)
	if read_err != nil{
		return -1, read_err
	}
	i, err := strconv.Atoi(strings.TrimRight(response, " \t\r\n"))
	return i, err
}
	
	