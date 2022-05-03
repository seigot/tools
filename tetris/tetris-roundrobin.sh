#!/bin/sh

# プレーヤ一覧を取得する
PLAYERS=(
    "testA@master" # 0
    "testB@master"
    "testC@master"
    "testD@master"
    "testE@master"
    "testF@master"
    "testG@master"
    "testH@master"
    "testI@master"
    "testJ@master" # N
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
function do_battle(){
    local PLAYER1_=${1}
    local PLAYER2_=${2}
    #echo "${PLAYER1}, ${PLAYER2}"
    ## とりあえず勝ちを返す
    return 0 # win
    #return 1 # lose
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
	else
	    RESULT="L"
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
	    else
		echo -n "W,"
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
