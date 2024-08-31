package common
import (
    "encoding/binary"
	"net"
	"fmt"
	"bytes"
	"bufio"
)
const EXPECTED_REPLY string = "OK\n"
const DELIMITER byte = '\n'
const UINT8_MAX = 255
func BuildMsg(fields []string)([]byte,error){
	buf := new(bytes.Buffer)
	for _, field := range fields {
		if len(field) > UINT8_MAX{
			return nil,fmt.Errorf("Length must be 255 or less")
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

func receiveServerResponse(sock net.Conn)error{
	response, err := bufio.NewReader(sock).ReadString(DELIMITER)
	if response != EXPECTED_REPLY{
		return fmt.Errorf("Server response was: %v", response)
	}
	return err
}
	
	