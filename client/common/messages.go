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
	return buf.Bytes(),nil
}

func SendBatch(sock net.Conn, batch [][]string) error{
	var buffer []byte
	for _, bet := range batch{
		bet_msg, build_err := BuildMsg(bet)
		if build_err != nil{
			return fmt.Errorf("Could not encode bet record:%v Error: %v", bet, build_err)
		}
		buffer = append(buffer,bet_msg...)
	}
	n, err := sock.Write(buffer)
	var m int
	for err == nil && n < len(buffer) {
		m, err = sock.Write(buffer[m:len(buffer)])
		n += m
	}
	return err

}

func SendMsg(sock net.Conn, fields []string) error{
	msg, build_err  := BuildMsg(fields)
	if build_err != nil{
		return build_err
	}
	n, err := sock.Write(msg)
	var m int
	for err == nil && n < len(msg) {
		m, err = sock.Write(msg[m:len(msg)])
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
	
	