#!/bin/sh

# プレーヤ一覧を取得する
PLAYERS=(
    "isshy-you@ish04e"
    "isshy-you@ish04f"
    "isshy-you@ish05a"
    "isshy-you@ish05b"
    "isshy-you@ish05c"
    "isshy-you@ish05d"
    "isshy-you@ish05f"
    "isshy-you@ish05g3"
    "isshy-you@ish05g6"
    "isshy-you@ish05h3"
    "seigot@master"
)

# Debug
function print_debug() {
    echo "--- UserList"
    for user in ${PLAYERS[@]}; do
	echo $user
    done
}

# プレーヤ一覧から、総当たり戦を実施するための組み合わせ一覧表を作成する
COMBINATION_LIST=()
function get_combination_list() {
    echo "--- CombinationList"
    N=`echo ${#PLAYERS[*]}`
    N=`expr ${N} - 1`
    for i in `seq 0 ${N}`; do
	for j in `seq 0 ${N}`; do
	    STR="${i}_${j}"
	#echo ${STR}
	    COMBINATION_LIST+=(${STR})
	done
    done
}

# 対戦する
CURRENT_SCORE_TEXT="current_score.txt"
function do_tetris(){
    # parameter declaration
    local DATETIME="$1"
    local REPOSITORY_URL="$2"
    local BRANCH="$3"
    local LEVEL="$4"
    local DROP_INTERVAL="$5"
    local RANDOM_SEED="$6"
    local GAME_TIME="180"
    if [ "${EXEC_MODE}" != "RELEASE" ]; then
	GAME_TIME="3" # debug value
    fi 

    local PRE_COMMAND="cd ~ && rm -rf tetris && git clone ${REPOSITORY_URL} -b ${BRANCH} && cd ~/tetris && pip3 install -r requirements.txt"
    local DO_COMMAND="cd ~/tetris && export DISPLAY=:1 && python3 start.py -l ${LEVEL} -t ${GAME_TIME} -d ${DROP_INTERVAL} -r ${RANDOM_SEED} && jq . result.json"
    local POST_COMMAND="cd ~/tetris && jq . result.json"

    local TMP_LOG="tmp.json"
    local TMP2_LOG="tmp2.log"
    local OUTPUTJSON="output.json"
    local CONTAINER_NAME="tetris_docker"

    # run docker with detached state
    RET=`docker ps -a | grep ${CONTAINER_NAME} | wc -l`
    if [ $RET -ne 0 ]; then
	docker stop ${CONTAINER_NAME}
	docker rm ${CONTAINER_NAME}
    fi
    docker run -d --name ${CONTAINER_NAME} -p 6080:80 --shm-size=512m seigott/tetris_docker
    
    # exec command
    docker exec ${CONTAINER_NAME} bash -c "${PRE_COMMAND}"
    if [ $? -ne 0 ]; then
	return 0
    fi
    docker network disconnect bridge ${CONTAINER_NAME}
    
    # do command
    docker exec ${CONTAINER_NAME} bash -c "${DO_COMMAND}"
    if [ $? -ne 0 ]; then
	return 0
    fi
    # get result
    docker exec ${CONTAINER_NAME} bash -c "${POST_COMMAND}" > ${TMP_LOG}

    # check if max score
    CURRENT_SCORE=`jq .judge_info.score ${TMP_LOG}`
    echo ${CURRENT_SCORE} > ${CURRENT_SCORE_TEXT}

    return 0
}

function do_battle(){
    local PLAYER1_=${1}
    local PLAYER2_=${2}

    #echo "${PLAYER1}, ${PLAYER2}"
    PLAYER1_NAME=`echo ${PLAYER1_} | cut -d'@' -f1`
    PLAYER1_BRANCH=`echo ${PLAYER1_} | cut -d'@' -f2`
    PLAYER2_NAME=`echo ${PLAYER2_} | cut -d'@' -f1`
    PLAYER2_BRANCH=`echo ${PLAYER2_} | cut -d'@' -f2`
    ## Player1
    do_tetris 0 "https://github.com/${PLAYER1_NAME}/tetris" "${PLAYER1_BRANCH}" 2 1000 1234
    RET=$?
    if [ $RET -ne 0 ]; then
	PLAYER1_SCORE=0
    else
	PLAYER1_SCORE1=`cat ${CURRENT_SCORE_TEXT}`
    fi
    ## Player2
    do_tetris 0 "https://github.com/${PLAYER2_NAME}/tetris" "${PLAYER2_BRANCH}" 2 1000 1234
    RET=$?
    if [ $RET -ne 0 ]; then
	PLAYER2_SCORE=0
    else
	PLAYER2_SCORE1=`cat ${CURRENT_SCORE_TEXT}`
    fi

    if [ $PLAYER1_SCORE -gt $PLAYER2_SCORE ]; then
	return 0 # win
    elif [ $PLAYER1_SCORE -lt $PLAYER2_SCORE ]; then
	return 1 # lose
    else
	return 2 # draw
    fi
}

# 組み合わせ一覧表の順番に総当たり戦をする
function do_battle_main() {
    #echo ${COMBINATION_LIST[@]}
    for i in ${COMBINATION_LIST[@]}; do

        # 変数を取得
	PLAYER1_NUM=`echo ${i} | cut -d'_' -f1`
	PLAYER2_NUM=`echo ${i} | cut -d'_' -f2`
	PLAYER1=${PLAYERS[${PLAYER1_NUM}]}
	PLAYER2=${PLAYERS[${PLAYER2_NUM}]}
	echo "${PLAYER1_NUM}:${PLAYER1}, ${PLAYER2_NUM}:${PLAYER2}"

        # 対戦不要の組み合わせの場合
        # 結果を取得して対戦はスキップする
	if [ ${PLAYER1_NUM} -ge ${PLAYER2_NUM} ]; then
	    RESULT="-"
	    RESULT_LIST+=(${RESULT})
	    continue
	fi

        # 対戦必要な組み合わせの場合
        # ここで対戦する(PLAYER1 vs PLAYER2) -->
	do_battle "${PLAYER1}" "${PLAYER2}"
	RET=$?
	if [ $RET -eq 0 ]; then
	    RESULT="W"
	elif [ $RET -eq 1 ]; then
	    RESULT="L"
	else
	    RESULT="D"
	fi
        # <---- ここまで対戦

        # 対戦結果を格納する
	RESULT_LIST+=(${RESULT})
    done
}

# 対戦結果の配列から結果表を出力する
function get_result() {
    # show result list
    #echo ${RESULT_LIST[@]}
    echo "--- Result"
    count=0
    for i in ${COMBINATION_LIST[@]}; do

	PLAYER1_NUM=`echo ${i} | cut -d'_' -f1`
	PLAYER2_NUM=`echo ${i} | cut -d'_' -f2`
	RESULT=${RESULT_LIST[${count}]}

        # 結果を出力
	if [ ${PLAYER1_NUM} -lt ${PLAYER2_NUM} ]; then
	    echo -n "${RESULT},"
	elif [ ${PLAYER1_NUM} -gt ${PLAYER2_NUM} ]; then
            # 既存の結果を再利用(総当たり表の反対側の要素を取得)
	    AA=`expr ${count} / ${#PLAYERS[@]}`
	    BB=`expr ${count} % ${#PLAYERS[@]}`
	    CC=`expr ${BB} \* ${#PLAYERS[@]} + ${AA}`
	    RESULT=${RESULT_LIST[${CC}]}
	    if [ "${RESULT}" == "W" ]; then
		echo -n "L,"
	    elif [ "${RESULT}" == "L" ]; then
		echo -n "W,"
	    else
		echo -n "D," # draw
	    fi
	else
	    echo -n "-,"
	fi

        # PLAYERS分だけループ処理したら改行する
	count=`expr $count + 1`
	TMP_NUM=`expr $count % ${#PLAYERS[@]}`
	if [ "${TMP_NUM}" == "0" ]; then
	    echo ""
	fi
    done
}

print_debug
get_combination_list
do_battle_main
get_result
