#!/bin/sh

# ユーザ一覧を取得する
USERS=(
    "testA@master" # 0
    "testB@master"
    "testC@master"
    "testD@master"
    "testE@master"
    "testF@master"
    "testG@master"
    "testH@master"
    "testI@master"
    "testJ@master"
)

echo "---"
for user in ${USERS[@]}; do
  echo $user
done
echo ${USERS[2]}  # ２番目の要素を出力
echo ${USERS[@]}  # 全ての要素を出力
echo ${#USERS[*]} # 数
echo ${#USERS[@]} # 数

# 組み合わせ一覧表を作成する
echo "---"
NUMBER_LIST=()
N=`echo ${#USERS[*]}`
N=`expr ${N} - 1`
for i in `seq 0 ${N}`; do
    for j in `seq 0 ${N}`; do
	STR="${i}_${j}"
	#echo ${STR}
	NUMBER_LIST+=(${STR})
    done
done

# 組み合わせ一覧表の順番に対戦する
#echo ${NUMBER_LIST[@]}
for i in ${NUMBER_LIST[@]}; do

    # 変数を取得
    PLAYER1_NUM=`echo ${i} | cut -d'_' -f1`
    PLAYER2_NUM=`echo ${i} | cut -d'_' -f2`
    PLAYER1=${USERS[${PLAYER1_NUM}]}
    PLAYER2=${USERS[${PLAYER2_NUM}]}
    echo "${PLAYER1_NUM}:${PLAYER1}, ${PLAYER2_NUM}:${PLAYER2}"

    # 対戦不要の組み合わせの場合
    # 結果を取得して対戦はスキップする
    if [ ${PLAYER1_NUM} -ge ${PLAYER2_NUM} ]; then
	RESULT="-"
	RESULT_LIST+=(${RESULT})
	continue
    fi

    # 対戦必要な組み合わせの場合
    # ここで対戦する
    # <---->
    RESULT="○"
    RESULT_LIST+=(${RESULT})
done

# show result list
echo ${RESULT_LIST[@]}
#echo ${RESULT_LIST[1]}
#echo ${NUMBER_LIST[1]}
#exit 0
count=0
for i in ${NUMBER_LIST[@]}; do

    PLAYER1_NUM=`echo ${i} | cut -d'_' -f1`
    PLAYER2_NUM=`echo ${i} | cut -d'_' -f2`
    RESULT=${RESULT_LIST[${count}]}

    # 結果を出力
    if [ ${PLAYER1_NUM} -lt ${PLAYER2_NUM} ]; then
	echo -n "${RESULT},"
    elif [ ${PLAYER1_NUM} -gt ${PLAYER2_NUM} ]; then
        # 既存の結果を再利用(総当たり表の反対側の要素を取得)
	AA=`expr ${count} / ${#USERS[@]}`
	BB=`expr ${count} % ${#USERS[@]}`
	CC=`expr ${BB} \* ${#USERS[@]} + ${AA}`
	RESULT=${RESULT_LIST[${CC}]}
	if [ "${RESULT}" == "○" ]; then
	    echo -n "*,"
	else
	    echo -n "○,"
	fi
    else
	echo -n "-,"
    fi

    # USERS分だけループ処理したら改行する
    count=`expr $count + 1`
    TMP_NUM=`expr $count % ${#USERS[@]}`
    if [ "${TMP_NUM}" == "0" ]; then
	echo ""
    fi
done
