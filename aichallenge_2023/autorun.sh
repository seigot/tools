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

# check
AICHALLENGE2023_DEV_REPOSITORY="${HOME}/aichallenge2023-sim"
if [ ! -d ${AICHALLENGE2023_DEV_REPOSITORY} ]; then
   "please clone ~/aichallenge2023-sim on home directory (${AICHALLENGE2023_DEV_REPOSITORY})!!"
   return
fi

function do_game(){

    # Pre Process
    # AWSIMを実行する
    # run AWSIM
    AWSIM_ROCKER_NAME="awsim_rocker_container"
    AWSIM_ROCKER_EXEC_COMMAND="cd ~/aichallenge2023-sim/docker; \
    		        rocker --nvidia --x11 --user --net host --privileged --volume aichallenge:/aichallenge --name ${AWSIM_ROCKER_NAME} -- aichallenge-train" # run_container.shの代わりにrockerコマンド直接実行
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

    # MAIN Process
    # Autowareを実行する
    # run AUTOWARE
    AUTOWARE_ROCKER_NAME="autoware_rocker_container"
    AUTOWARE_ROCKER_EXEC_COMMAND="cd ~/aichallenge2023-sim/docker; \
    		        rocker --nvidia --x11 --user --net host --privileged --volume aichallenge:/aichallenge --name ${AUTOWARE_ROCKER_NAME} -- aichallenge-train" # run_container.shの代わりにrockerコマンド直接実行
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
    sleep 180

    # POST Process:
    # ここで何か結果を記録したい

    # finish..
    bash stop.sh
}

# main loop
for ((i=0; i<${LOOP_TIMES}; i++));
do
    echo "----- LOOP: ${i} -----"
    do_game
done
	
