package common
import (
    "encoding/binary"
	"net"
	"fmt"
	"bytes"
)
func BuildMsg(fields []string)[]byte{
	buf := new(bytes.Buffer)
	for _, field := range fields {
		if err := binary.Write(buf, binary.BigEndian, uint8(len(field))); err != nil {
			fmt.Println("binary.Write failed:", err)
		}
		if err := binary.Write(buf, binary.BigEndian, []byte(field)); err != nil {
			fmt.Println("binary.Write failed:", err)
		}
	}
	return buf.Bytes()
}

func SendMsg(sock net.Conn, fields []string) error{
	msg  := BuildMsg(fields)
	n, err := sock.Write(msg)
	var m int
	for err == nil && n < len(msg) {
		m, err = sock.Write(msg[m:len(msg)])
		n += m
	}
	return err
}

	
	