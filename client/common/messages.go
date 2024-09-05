package common
import (
    "encoding/binary"
	"net"
	"fmt"
	"bytes"
	"bufio"
	"strconv"
	"strings"
	"time"
)
const DELIMITER byte= '\n'
const SEPARATOR = ","
const UINT8_MAX = 255
const FIELDS_TO_READ = 5
const (
	PLACE_BETS = iota
	NOTIFY 
	REQ_RESULTS
	PLACE_BETS_OK
	REQ_RESULTS_OK
	SERVER_ERR
	PLACE_BETS_ERR
)

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

func GetBytesOfU8(number int)([]byte,error){
	buf := new(bytes.Buffer)
	if number > UINT8_MAX{
		return nil, fmt.Errorf("Length must be 255 or less")
	}
	if err := binary.Write(buf, binary.BigEndian, uint8(number)); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func GetAgencyBytes(agency_id string)([]byte,error){
	id, atoi_err := strconv.Atoi(agency_id)
	if atoi_err != nil{
		return nil, atoi_err
	}
	return GetBytesOfU8(id)
}

func SendBatch(sock net.Conn, batch [][]string, agency_id string) error{
	buffer, header_err := BuildHeader(agency_id, PLACE_BETS)
	if header_err != nil{
		return header_err
	}
	batch_len, batch_len_err := GetBytesOfU8(len(batch))
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
func BuildHeader(agency_id string, msg_type int)([]byte, error){
	var buffer []byte
	agency_id_bytes, agency_id_err := GetAgencyBytes(agency_id)
	if agency_id_err != nil{
		return nil, agency_id_err
	}
	buffer = append(buffer, agency_id_bytes...)
	msg_type_bytes, msg_type_err := GetBytesOfU8(msg_type)
	if msg_type_err != nil{
		return nil, msg_type_err
	}
	buffer = append(buffer, msg_type_bytes...)
	return buffer, nil
}

func NotifyServer(sock net.Conn, agency_id string) error{
	buffer, err := BuildHeader(agency_id, NOTIFY)
	if err != nil{
		return err
	}
	return SendMsg(sock, buffer)
}
func AskForResults(sock net.Conn, agency_id string, timeout time.Duration)(int, error){
	buffer, err := BuildHeader(agency_id, REQ_RESULTS)
	if err != nil{
		return -1, err
	}
	if send_err := SendMsg(sock, buffer); send_err != nil {
		return -1, send_err
	}
	
	return receiveServerResponse(sock, timeout)
}

func SendMsg(sock net.Conn, msg []byte)error{
	n, err := sock.Write(msg)
	var m int
	for err == nil && n < len(msg) {
		m, err = sock.Write(msg[n:len(msg)])
		n += m
	}
	return err
}

func receiveServerResponse(sock net.Conn, timeout time.Duration)(int, error){
	sock.SetReadDeadline(time.Now().Add(timeout))
	response, read_err := bufio.NewReader(sock).ReadString(DELIMITER)
	if read_err != nil{
		return -1, read_err
	}
	sock.SetReadDeadline(time.Time{})
	response = strings.TrimRight(response, string(DELIMITER))
	response_fields := strings.Split(response, SEPARATOR)
	response_code, parse_err := strconv.Atoi(response_fields[0])
	if len(response_fields) < 2 ||  parse_err != nil{
		return -1, fmt.Errorf("Server response did not follow protocol: %v", response)
	}
	switch response_code{
	case SERVER_ERR :
		return -1, fmt.Errorf("Server responded with error: %v", response_fields[1])
	case PLACE_BETS_ERR:
		return -1, fmt.Errorf("Server detected error when processing bets. Bets processed: %v", response_fields[1])
	case PLACE_BETS_OK :
		return strconv.Atoi(response_fields[1])
	case REQ_RESULTS_OK:
		return len(response_fields) - 1, nil
	default:
		return -1, fmt.Errorf("Server response did not follow protocol: %v", response)
	}
	
}
	
	