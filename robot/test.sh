#!/bin/bash

CATKIN_WS_SRC=${HOME}/catkin_ws/src

# sample
function common(){
    REPOSITORY_URL=$1
    if [ -z "${REPOSITORY_URL}" ];then
	# sample
	REPOSITORY_URL="https://github.com/seigot/burger_war_dev"
    fi

    cd $HOME/catkin_ws/src
    rm -rf burger_war_dev
    git clone ${REPOSITORY_URL}
    pushd burger_war_dev
    git remote -v
    popd
    
    # catkin build
    cd $HOME/catkin_ws
    catkin build
    source $HOME/catkin_ws/devel/setup.bash

    # autotest
    cd $HOME/catkin_ws/src/burger_war_kit
    bash autotest/autotest.sh #-c "true" #-c "true"
}

# takino-san
function takinoon(){
    common "https://github.com/takinoon/burger_war_dev"
}

# amamiya-san
function nanka-nemuiyo(){
    common "https://github.com/nanka-nemuiyo/burger_war_dev"
}

# ohishi-san
function KoutaOhishi(){
    common "https://github.com/KoutaOhishi/burger_war_dev -b develop"    
}

# onishi-san
function k-onishi(){
    common "https://github.com/k-onishi/burger_war_dev -b develop"
}

# tanimura-san
function ce31062(){
    common "https://github.com/ce31062/burger_war_dev -b develop"
}

#common
#takinoon
#nanka-nemuiyo
#KoutaOhishi
k-onishi
#ce31062
