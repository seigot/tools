diff --git a/scripts/gameserver.sh b/scripts/gameserver.sh
index 160f8c9..d0baa5f 100644
--- a/scripts/gameserver.sh
+++ b/scripts/gameserver.sh
@@ -34,20 +34,23 @@ function update_result(){
     local LEVEL="$5"
     local RESULT="$6"
     local DROP_INTERVAL="$7"
-    local LINE1_SCORE="$8"
-    local LINE2_SCORE="$9"
-    local LINE3_SCORE="${10}"
-    local LINE4_SCORE="${11}"
-    local GAMEOVER_SCORE="${12}"
-    local DROPDOWN_SCORE="${13}"
-    local BLOCK_NO="${14}"
-    local TRIAL_NUM="${15}"
-    local SCORE_MEAN="${16}"
-    local SCORE_STDEV="${17}"
-    local SCORE_MAX="${18}"
-    local SCORE_MIN="${19}"
-    local HEADER_STR="DATETIME, REPOSITORY_URL, BRANCH, SCORE, LEVEL, RESULT, DROP_INTERVAL, 1LINE_SCORE, 2LINE_SCORE, 3LINE_SCORE, 4LINE_SCORE, GAMEOVER_SCORE, DROPDOWN_SCORE, BLOCK_NO, TRIAL_NUM, SCORE_MEAN, SCORE_STDEV, SCORE_MAX, SCORE_MIN"
-    local STR="${DATETIME}, ${REPOSITORY_URL}, ${BRANCH}, ${SCORE}, ${LEVEL}, ${RESULT}, ${DROP_INTERVAL}, ${LINE1_SCORE}, ${LINE2_SCORE}, ${LINE3_SCORE}, ${LINE4_SCORE}, ${GAMEOVER_SCORE}, ${DROPDOWN_SCORE}, ${BLOCK_NO}, ${TRIAL_NUM}, ${SCORE_MEAN}, ${SCORE_STDEV}, ${SCORE_MAX}, ${SCORE_MIN}"
+    local VALUE_MODE="$8"
+    local VALUE_PREDICT_WEIGHT="$9"
+    local LINE1_SCORE="${10}"
+    local LINE2_SCORE="${11}"
+    local LINE3_SCORE="${12}"
+    local LINE4_SCORE="${13}"
+    local GAMEOVER_SCORE="${14}"
+    local DROPDOWN_SCORE="${15}"
+    local BLOCK_NO="${16}"
+    local TRIAL_NUM="${17}"
+    local SCORE_MEAN="${18}"
+    local SCORE_STDEV="${19}"
+    local SCORE_MAX="${20}"
+    local SCORE_MIN="${21}"
+
+    local HEADER_STR="DATETIME, REPOSITORY_URL, BRANCH, SCORE, LEVEL, RESULT, DROP_INTERVAL, VALUE_MODE, VALUE_PREDICT_WEIGHT, 1LINE_SCORE, 2LINE_SCORE, 3LINE_SCORE, 4LINE_SCORE, GAMEOVER_SCORE, DROPDOWN_SCORE, BLOCK_NO, TRIAL_NUM, SCORE_MEAN, SCORE_STDEV, SCORE_MAX, SCORE_MIN"
+    local STR="${DATETIME}, ${REPOSITORY_URL}, ${BRANCH}, ${SCORE}, ${LEVEL}, ${RESULT}, ${DROP_INTERVAL}, ${VALUE_MODE}, ${VALUE_PREDICT_WEIGHT}, ${LINE1_SCORE}, ${LINE2_SCORE}, ${LINE3_SCORE}, ${LINE4_SCORE}, ${GAMEOVER_SCORE}, ${DROPDOWN_SCORE}, ${BLOCK_NO}, ${TRIAL_NUM}, ${SCORE_MEAN}, ${SCORE_STDEV}, ${SCORE_MAX}, ${SCORE_MIN}"
 
     ## update result file
     local RESULT_LOG="result.csv"
@@ -102,7 +105,7 @@ function error_result(){
     #RESULT="$5"
     #STR="${DATETIME}, ${REPOSITORY_URL}, ${SCORE}, ${LEVEL}, ${RESULT}"
     #update_result "${STR}"
-    update_result "$1" "$2" "$3" "$4" "$5" "$6" "$7" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
+    update_result "$1" "$2" "$3" "$4" "$5" "$6" "$7" "${8}" "${9}" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
 }
 
 function success_result(){
@@ -113,7 +116,7 @@ function success_result(){
     #LEVEL="$4"
     #STR="${DATETIME}, ${REPOSITORY_URL}, ${SCORE}, ${LEVEL}, SUCCESS"
     #update_result "${STR}"
-    update_result "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" "${13}" "${14}" "${15}" "${16}" "${17}" "${18}" "${19}"
+    update_result "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" "${13}" "${14}" "${15}" "${16}" "${17}" "${18}" "${19}" "${20}" "${21}"
 }
 
 function check_drop_interval_value(){
@@ -152,13 +155,16 @@ function do_tetris(){
     local BRANCH="$3"
     local LEVEL="$4"
     local DROP_INTERVAL="$5"
+    local VALUE_MODE="$6"
+    local VALUE_PREDICT_WEIGHT="$7"
+
     local GAME_TIME="180"
     if [ "${EXEC_MODE}" != "RELEASE" ]; then
	 GAME_TIME="3" # debug value
     fi 
 
     local PRE_COMMAND="cd ~ && rm -rf tetris && git clone ${REPOSITORY_URL} -b ${BRANCH} && cd ~/tetris && pip3 install -r requirements.txt"
-    local DO_COMMAND="cd ~/tetris && export DISPLAY=:1 && python3 start.py -l ${LEVEL} -t ${GAME_TIME} -d ${DROP_INTERVAL} && jq . result.json"
+    local DO_COMMAND="cd ~/tetris && export DISPLAY=:1 && python3 start.py -l ${LEVEL} -t ${GAME_TIME} -d ${DROP_INTERVAL} -m ${VALUE_MODE} --predict_weight ${VALUE_PREDICT_WEIGHT} && jq . result.json"
     local POST_COMMAND="cd ~/tetris && jq . result.json"
 
     local TMP_LOG="tmp.json"
@@ -177,7 +183,7 @@ function do_tetris(){
     # exec command
     docker exec ${CONTAINER_NAME} bash -c "${PRE_COMMAND}"
     if [ $? -ne 0 ]; then
	 -error_result "${DATETIME}" "${REPOSITORY_URL}" "${BRANCH}" "0" "${LEVEL}" "pip3_install_-r_requirements.txt_NG" "${DROP_INTERVAL}"
	 +error_result "${DATETIME}" "${REPOSITORY_URL}" "${BRANCH}" "0" "${LEVEL}" "pip3_install_-r_requirements.txt_NG" "${DROP_INTERVAL}" "${VALUE_MODE}" "${VALUE_PREDICT_WEIGHT}"
	 return 0
     fi
     docker network disconnect bridge ${CONTAINER_NAME}
@@ -192,7 +198,7 @@ function do_tetris(){
    # do command
    docker exec ${CONTAINER_NAME} bash -c "${DO_COMMAND}"
    if [ $? -ne 0 ]; then
	-    error_result "${DATETIME}" "${REPOSITORY_URL}" "${BRANCH}" "0" "${LEVEL}" "python_start.py_NG" "${DROP_INTERVAL}"
	+    error_result "${DATETIME}" "${REPOSITORY_URL}" "${BRANCH}" "0" "${LEVEL}" "python_start.py_NG" "${DROP_INTERVAL}" "${VALUE_MODE}" "${VALUE_PREDICT_WEIGHT}"
	    return 0
	    fi
    # get result
@@ -240,7 +246,7 @@ function do_tetris(){
     MAX=`cat ${TMP2_LOG} | grep "max" | cut -d' ' -f2`
     MIN=`cat ${TMP2_LOG} | grep "min" | cut -d' ' -f2`
 
-    success_result "${DATETIME}" "${REPOSITORY_URL}" "${BRANCH}" "${SCORE}" "${LEVEL}" "SUCCESS" "${DROP_INTERVAL}" "${LINE1_SCORE}" "${LINE2_SCORE}" "${LINE3_SCORE}" "${LINE4_SCORE}" "${GAMEOVER_SCORE}" "${DROPDOWN_SCORE}" "${BLOCK_NO}" "${TRIAL_NUM}" "${MEAN}" "${STDEV}" "${MAX}" "${MIN}"
+    success_result "${DATETIME}" "${REPOSITORY_URL}" "${BRANCH}" "${SCORE}" "${LEVEL}" "SUCCESS" "${DROP_INTERVAL}" "${VALUE_MODE}" "${VALUE_PREDICT_WEIGHT}" "${LINE1_SCORE}" "${LINE2_SCORE}" "${LINE3_SCORE}" "${LINE4_SCORE}" "${GAMEOVER_SCORE}" "${DROPDOWN_SCORE}" "${BLOCK_NO}" "${TRIAL_NUM}" "${MEAN}" "${STDEV}" "${MAX}" "${MIN}"
 }
 
 function do_polling(){
@@ -261,7 +267,7 @@ function do_polling(){
     RET=$?
     if [ $RET -ne 0 ]; then
	 echo "curl NG"
	 -error_result "-" "-" "-" "0" "-" "curl_google_speadsheet_NG" "-"
	 +error_result "-" "-" "-" "0" "-" "curl_google_speadsheet_NG" "-" "-" "-"
	 return 0
     fi
     VALUE_LENGTH=`jq .values ${JSONFILE} | jq length`
@@ -300,14 +306,14 @@ function do_polling(){
        if [[ "$VALUE_URL" =~ "http".*"://github.com/".*"tetris"$ ]]; then
	    echo "url string OK"
	        else
	    -error_result "${VALUE_TIME}" "${VALUE_URL}" "-" "0" "-" "github_url_string_NG" "-"
+error_result "${VALUE_TIME}" "${VALUE_URL}" "-" "0" "-" "github_url_string_NG" "-" "-" "-"
 continue
     fi
     git ls-remote ${VALUE_URL} > /dev/null
         RET=$?
	     if [ $RET -ne 0 ]; then
		 echo "git ls-remote NG"
		 -error_result "${VALUE_TIME}" "${VALUE_URL}" "-" "0" "-" "github_url_access_NG" "-"
		 +error_result "${VALUE_TIME}" "${VALUE_URL}" "-" "0" "-" "github_url_access_NG" "-" "-" "-"
		 continue
		     fi
	         VALUE_BRANCH=`jq .values[${idx}][4] ${JSONFILE} | sed 's/"//g'`
@@ -319,7 +325,7 @@ function do_polling(){
        RET=$?
	    if [ $RET -ne 0 ]; then
		echo "git ls-remote NG"
		-error_result "${VALUE_TIME}" "${VALUE_URL}" "${VALUE_BRANCH}" "0" "-" "github_url_branch_access_NG" "-"
+error_result "${VALUE_TIME}" "${VALUE_URL}" "${VALUE_BRANCH}" "0" "-" "github_url_branch_access_NG" "-" "-" "-"
 continue
     fi
 
@@ -340,18 +346,34 @@ function do_polling(){
        RET=$?
	    if [ $RET -ne 0 ]; then
		echo "check_drop_interval_valuegit NG"
		-error_result "${VALUE_TIME}" "${VALUE_URL}" "${VALUE_BRANCH}" "0" "-" "check_drop_interval_value_NG" "${VALUE_DROP_INTERVAL}"
+error_result "${VALUE_TIME}" "${VALUE_URL}" "${VALUE_BRANCH}" "0" "-" "check_drop_interval_value_NG" "${VALUE_DROP_INTERVAL}" "-" "-"
 continue
     fi    
+
+    # get MODE(predict,predict_sample,predict_sample2)
+    VALUE_MODE=`jq .values[${idx}][6] ${JSONFILE} | sed 's/"//g'`
+    if [ "$VALUE_MODE" == "null" -o "${VALUE_MODE}" == "" ]; then
+echo "use default VALUE_MODE"
+VALUE_MODE="default"
+    fi
+
+    # get PREDICT_WEIGHT
+    VALUE_PREDICT_WEIGHT=`jq .values[${idx}][6] ${JSONFILE} | sed 's/"//g'`
+    if [ "$VALUE_PREDICT_WEIGHT" == "null" -o "${VALUE_PREDICT_WEIGHT}" == "" ]; then
+echo "use default VALUE_PREDICT_WEIGHT"
+VALUE_PREDICT_WEIGHT="default"
+    fi
    
    echo "TIME: ${VALUE_TIME}"
     echo "URL: ${VALUE_URL}"
     echo "BRANCH: ${VALUE_BRANCH}"
     echo "LEVEL: ${VALUE_LEVEL}"
     echo "VALUE_DROP_INTERVAL: ${VALUE_DROP_INTERVAL}"
-    
+    echo "VALUE_MODE: ${VALUE_MODE}"
+    echo "VALUE_PREDICT_WEIGHT: ${VALUE_PREDICT_WEIGHT}"
+
     ## do tetris
-    do_tetris "${VALUE_TIME}" "${VALUE_URL}" "${VALUE_BRANCH}" "${VALUE_LEVEL}" "${VALUE_DROP_INTERVAL}"
+    do_tetris "${VALUE_TIME}" "${VALUE_URL}" "${VALUE_BRANCH}" "${VALUE_LEVEL}" "${VALUE_DROP_INTERVAL}" "${VALUE_MODE}" "${VALUE_PREDICT_WEIGHT}"
 done
 
     else