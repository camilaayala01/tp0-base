package common
import (
    "fmt"
	"net"
)
func BuildMsg(fields []string)string{
	msg := ""
	for i := 0; i < len(fields); i++ {
		msg += fmt.Sprintf("%v~%v",len(fields[i]), fields[i])
	}
	msg += "\n"
	return msg
}

func SendMsg(sock net.Conn, fields []string) error{
	msg  := BuildMsg(fields)
	n, err := fmt.Fprintf(sock, msg)
	var m int
	for err == nil && n < len(msg) {
		m, err = fmt.Fprintf(sock, msg[n:])
		n += m
	}
	return err
}