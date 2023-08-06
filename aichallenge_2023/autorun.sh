#!/bin/bash -x

#
# サンプルコード(run.sh)を自動実行するためのスクリプト
# README記載のサンプルコード実行手順をスクリプトで一撃でできるようにしてるだけ
#
# 以下を実行すれば動く想定
#   cd ${HOME}/aichallenge2023-sim
#   wget https://raw.githubusercontent.com/seigot/tools/master/aichallenge_2023/autorun.sh
#   wget https://raw.githubusercontent.com/seigot/tools/master/aichallenge_2023/stop.sh
#   bash autorun.sh  # 2回目以降はここだけ実行
#
# 以下を前提としている
# - ${HOME}/aichallenge2023-simが存在していること
# - README.mdに沿って事前準備完了していること
#   - 各種インストールが完了していること
#   - 地図データ(pcd,osm)のコピーが完了していること
#   - autowareのサンプルコードの手動実行が確認できていること

LOOP_TIMES=10
SLEEP_SEC=180

# check
AICHALLENGE2023_DEV_REPOSITORY="${HOME}/aichallenge2023-sim"
if [ ! -d ${AICHALLENGE2023_DEV_REPOSITORY} ]; then
   "please clone ~/aichallenge2023-sim on home directory (${AICHALLENGE2023_DEV_REPOSITORY})!!"
   return
fi

function run_awsim(){

    # Pre Process
    # AWSIMを実行する
    # run AWSIM
    AWSIM_ROCKER_NAME="awsim_rocker_container"
    AWSIM_ROCKER_EXEC_COMMAND="cd ~/aichallenge2023-sim/docker; \
    		        rocker --nvidia --x11 --user --net host --privileged --volume aichallenge:/aichallenge --name ${AWSIM_ROCKER_NAME} -- aichallenge-train" # run_container.shの代わりにrockerコマンド直接実行(コンテナに名前をつける必要がある)
    AWSIM_EXEC_COMMAND_ON_BASH="sudo ip link set multicast on lo; \
			source /autoware/install/setup.bash; \
			/aichallenge/AWSIM/AWSIM.x86_64;"
    AWSIM_EXEC_COMMAND="docker exec ${AWSIM_ROCKER_NAME} bash -c '${AWSIM_EXEC_COMMAND_ON_BASH}'"

    # exec awsim
    echo "-- run AWSIM rocker... -->"
    echo "CMD: ${AWSIM_ROCKER_EXEC_COMMAND}"
    gnome-terminal -- bash -c "${AWSIM_ROCKER_EXEC_COMMAND}" &
    sleep 5
    echo "-- run AWSIM... -->"
    echo "CMD: ${AWSIM_EXEC_COMMAND}"
    gnome-terminal -- bash -c "${AWSIM_EXEC_COMMAND}" &
    sleep 15
    return
}

function run_autoware(){

    # 起動後何秒くらい待つか(sec)
    WAIT_SEC=$1

    # MAIN Process
    # Autowareを実行する
    # run AUTOWARE
    AUTOWARE_ROCKER_NAME="autoware_rocker_container"
    AUTOWARE_ROCKER_EXEC_COMMAND="cd ~/aichallenge2023-sim/docker; \
    		        rocker --nvidia --x11 --user --net host --privileged --volume aichallenge:/aichallenge --name ${AUTOWARE_ROCKER_NAME} -- aichallenge-train" # run_container.shの代わりにrockerコマンド直接実行(コンテナに名前をつける必要がある)
    # bash起動時の環境変数を追加しておく(source /etc/bash.bashrc; source /etc/profile;)
    # rockerはおそらくここにros2用の環境変数を記載している
    AUTOWARE_EXEC_COMMAND_ON_BASH="source /etc/bash.bashrc; source /etc/profile; \
			sudo ip link set multicast on lo; \
			cd /aichallenge; \
			bash build.sh; \
			source aichallenge_ws/install/setup.bash; \
			bash run.sh"
    AUTOWARE_EXEC_COMMAND="docker exec ${AUTOWARE_ROCKER_NAME} bash -c '${AUTOWARE_EXEC_COMMAND_ON_BASH}'"

    echo "-- run AUTOWARE rocker... -->"    
    echo "CMD: ${AUTOWARE_ROCKER_EXEC_COMMAND}"
    gnome-terminal -- bash -c "${AUTOWARE_ROCKER_EXEC_COMMAND}" &
    sleep 5
    echo "-- run AUTOWARE run.sh... -->"
    echo "CMD: ${AUTOWARE_EXEC_COMMAND}"    
    gnome-terminal -- bash -c "${AUTOWARE_EXEC_COMMAND}" &
    sleep 15

    # wait until game finish
    sleep ${WAIT_SEC}

    # POST Process:
    # ここで何か結果を記録したい
    RESULT_JSON="result.json" #"${HOME}/result.json"
    RESULT_TMP_JSON="result_tmp.json" #"${HOME}/result_tmp.json"
    GET_RESULT_LOOP_TIMES=10
    for ((jj=0; jj<${GET_RESULT_LOOP_TIMES}; jj++));
    do
	docker exec ${AUTOWARE_ROCKER_NAME} cat /aichallenge/result.json > ${RESULT_TMP_JSON}
	if [ $? == 0 ]; then
	    # result
	    VAL1=`jq .rawDistanceScore ${RESULT_TMP_JSON}`
	    VAL2=`jq .distanceScore ${RESULT_TMP_JSON}`
	    VAL3=`jq .task3Duration ${RESULT_TMP_JSON}`
	    VAL4=`jq .isOutsideLane ${RESULT_TMP_JSON}`
	    VAL5=`jq .isTimeout ${RESULT_TMP_JSON}`
	    VAL6=`jq .hasCollided ${RESULT_TMP_JSON}`
	    VAL7=`jq .hasExceededSpeedLimit ${RESULT_TMP_JSON}`
	    VAL8=`jq .hasFinishedTask1 ${RESULT_TMP_JSON}`
	    VAL9=`jq .hasFinishedTask2 ${RESULT_TMP_JSON}`
	    VAL10=`jq .hasFinishedTask3 ${RESULT_TMP_JSON}`
	    if [ ! -e ${RESULT_JSON} ]; then
		echo -e "Time\trawDistanceSocre\tdistanceScore\ttask3Duration\tisOutsideLane\tisTimeout\thasCollided\thasExceededSpeedLimit\thasFinishedTask1\thasFinishedTask2\thasFinishedTask3" > ${RESULT_JSON}
	    fi
	    TODAY=`date +"%Y%m%d%I%M%S"`
	    OWNER=`git remote -v | grep fetch | cut -d"/" -f4`
	    BRANCH=`git branch | cut -d" " -f 2`	    
	    echo -e "${TODAY}_${OWNER}_${BRANCH}\t${VAL1}\t${VAL2}\t${VAL3}\t${VAL4}\t${VAL5}\t${VAL6}\t${VAL7}\t${VAL8}\t${VAL9}\t${VAL10}" >> ${RESULT_JSON}
	    
	    break
	fi
	# retry..
	sleep 10
    done

    # finish..
    bash stop.sh
}

function do_game(){
    SLEEP_SEC=$1
    run_awsim
    run_autoware ${SLEEP_SEC}
}

# 引数に応じて処理を分岐
# 引数別の処理定義
while getopts "a:l:s:" optKey; do
    case "$optKey" in
	a)
	    echo "-a = ${OPTARG}";
	    run_awsim;
	    ;;
	l)
	    echo "-l = ${OPTARG}"
	    LOOP_TIMES=${OPTARG}
	    ;;
	s)
	    echo "-s = ${OPTARG}"
	    SLEEP_SEC=${OPTARG}
	    ;;
    esac
done

# main loop
echo "LOOP_TIMES: ${LOOP_TIMES}"
echo "SLEEP_SEC: ${SLEEP_SEC}"
for ((i=0; i<${LOOP_TIMES}; i++));
do
    echo "----- LOOP: ${i} -----"
    do_game ${SLEEP_SEC}
done
	
