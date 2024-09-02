#!/bin/bash

docker run --rm -it --network=tp0_testing_net --name=validator ubuntu:20.04 bash -c '
  apt-get update && apt-get install -y netcat

  test_str="testing"
  err_str="action: test_echo_server | result: fail"
  success_str="action: test_echo_server | result: success"
  
  result=$((echo "$test_str" | nc -v -w 3 server 12345 2>&1) || echo  $err_str) 
  if [[ "$result" == *"$test_str"* ]]; then
    echo $success_str
  else 
    echo $err_str
  fi
'