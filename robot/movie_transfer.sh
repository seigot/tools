DATE="20211201_1900"
LEVEL="lv3"
TAKINOON="takinoon_${DATE}_${LEVEL}"
NANKANEMUIYO="nanka-nemuiyo_${DATE}_${LEVEL}"
KOUTAOHISHI="KoutaOhishi_${DATE}_${LEVEL}"
KONISHI="k-onishi_${DATE}_${LEVEL}"
CE31062="ce31062_${DATE}_${LEVEL}"
SOUND="poke2_m.wav"

# webm --> mp4
MP4FNAME="20211201-2.mp4"
ffmpeg -i 20211201-2.webm ${MP4FNAME}

# cut mp4
STEP=540
OFFSET=270 #0
ffmpeg -ss $((${STEP}*0+${OFFSET})) -i ${MP4FNAME} -t 270 -c copy ${TAKINOON}.mp4
ffmpeg -ss $((${STEP}*1+${OFFSET})) -i ${MP4FNAME} -t 270 -c copy ${NANKANEMUIYO}.mp4
ffmpeg -ss $((${STEP}*2+${OFFSET})) -i ${MP4FNAME} -t 270 -c copy ${KOUTAOHISHI}.mp4
ffmpeg -ss $((${STEP}*3+${OFFSET})) -i ${MP4FNAME} -t 270 -c copy ${KONISHI}.mp4
ffmpeg -ss $((${STEP}*4+${OFFSET})) -i ${MP4FNAME} -t 270 -c copy ${CE31062}.mp4

# integrate mp4 + wav
ffmpeg -i ${TAKINOON}.mp4 -i ${SOUND} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 ${TAKINOON}_2.mp4
ffmpeg -i ${NANKANEMUIYO}.mp4 -i ${SOUND} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 ${NANKANEMUIYO}_2.mp4
ffmpeg -i ${KOUTAOHISHI}.mp4 -i ${SOUND} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 ${KOUTAOHISHI}_2.mp4
ffmpeg -i ${KONISHI}.mp4 -i ${SOUND} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 ${KONISHI}_2.mp4
ffmpeg -i ${CE31062}.mp4 -i ${SOUND} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 ${CE31062}_2.mp4

