#!/bin/bash

function try_kill_process(){
    PROCESS_NAME=$1
    if [ -z "$PROCESS_NAME" ]; then
	return 0
    fi
    
    PROCESS_ID=`ps -e -o pid,cmd | grep ${PROCESS_NAME} | grep -v grep | awk '{print $1}'`
    if [ -z "$PROCESS_ID" ]; then
	echo "no process like... ${PROCESS_NAME}"
	return 0
    fi
    echo "kill process ... ${PROCESS_NAME}"
    #kill -SIGINT $PROCESS_ID
    kill $PROCESS_ID
}

function try_kill_docker_container(){

    local LOOP_MAX=10
    for ((i=0; i<${LOOP_MAX}; i++));
    do
	CNT=`docker ps | wc -l`
	if [ "${CNT}" == "1" ]; then
	    echo "no_running_docker_container..."
	    return
	fi
	HASHNO=`docker ps | tail -1 | cut -d" " -f1`
	echo "try_to_kill_docker_container... HASHNO:${HASHNO}"
	docker rm -f ${HASHNO}
	sleep 1
    done
}

function stop_process(){    
    try_kill_process "awsim_rocker_container"
    try_kill_process "autoware_rocker_container"
    try_kill_process "run_container.sh"
    try_kill_process "run_container.sh"
    try_kill_docker_container
}

stop_process
