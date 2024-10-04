import cv2
import pytesseract
import re
import csv
from argparse import ArgumentParser

# 動画ファイルからN秒毎にOCRする
N = 1

# pip install pytesseract
# python.exe .\tesseract-test.py -f 2024-00-00-00-00-00.mkv
# if windows, need to specify tesseract command path.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def get_option(fname):
    argparser = ArgumentParser()
    argparser.add_argument('-f', '--filename', type=str,
                            default=fname,
                            help='Specify filename')
    return argparser.parse_args()

# 動画ファイル
video_name_default = '2024-09-17-evalx.mkv'
args = get_option(video_name_default)
video_name = args.filename
#video_name = '2024-08-12 13-42-32.mkv'
video_path = r'/Users/XXX.XXX/Desktop/python/' + video_name
video_capture = cv2.VideoCapture(video_path)
# config
# tessedit_char_whitelist: 検索対象の文字列を限定する
# psm: 番号に応じてocrのアルゴリズムを切り替える（詳しくは、tesseract --help-psmを参照）
config = ("-c tessedit_char_whitelist=0123456789 --psm 8")

# 指定された領域の画像を切り取る（左上のx座標、左上のy座標、幅、高さ）
xywl = [[710, 50, 200, 140], # 領域1
        [720, 300, 190, 130], # 領域2
        [670, 440, 125, 75], # 領域3
        [820, 440, 135, 75]] # 領域4
# 領域のrange、異常処理用
AvailableRange = [[50,200], [6,30], [100,180], [40,180]]
# 前の値、異常処理用
PrevValue = ['N/A', 'N/A', 'N/A', 'N/A']
# csv write
csvfname = video_name + ".csv"
with open(csvfname, 'w', newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "HR", "RR", "BP(MAX)", "BP(MIN)"])

# 動画のフレームを1秒ごとに処理する
fps = int(video_capture.get(cv2.CAP_PROP_FPS))
frame_count = -1
while video_capture.isOpened():
    ret, frame = video_capture.read()
    if not ret:
        break
    frame_count += 1
    if frame_count % (fps*N) != 0:
        continue

    digits_only_list = []
    digits_only_list.append(frame_count // (fps*N))
    digits_only_list_debug = []
    for id in range(len(xywl)):
        x, y, w, h = xywl[id][0], xywl[id][1], xywl[id][2], xywl[id][3]

        # Get Region of Interest
        roi = frame[y:y+h, x:x+w]
        # グレースケールに変換
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # 二値化
        threshold = [55, 255] #[55, 255]
        if id == 2 or id == 3: threshold = [135, 255] # id == 2 or 3 の場合のみグレイが存在するのでしきい値を調整
        _, roi_binary = cv2.threshold(roi_gray, threshold[0], threshold[1], cv2.THRESH_BINARY)
        # 文字認識を実行する
        text = pytesseract.image_to_string(roi_binary, lang='eng', config=config)
        # 経過時間を取得する
        elapsed_time = frame_count / fps
        # 数字のみを抽出
        digits_only = ''.join(re.findall(r'\d', text))
        digits_only_list_debug.append(digits_only)
        # Value Range Check
        if id == 0 or id == 1:
            # if brank, use prev value
            if digits_only == '':
                digits_only = -1
            if not (AvailableRange[id][0] < int(digits_only) < AvailableRange[id][1]):
                digits_only = PrevValue[id]
        else:
            # id == 2 or id == 3
            # if brank, use 'N/A', and reset PrevValue
            if digits_only == '':
                digits_only = 'N/A'
                PrevValue[id] = 'N/A'
            elif not (AvailableRange[id][0] < int(digits_only) < AvailableRange[id][1]):
                digits_only = PrevValue[id]
        if digits_only != 'N/A':
            PrevValue[id] = digits_only
        digits_only_list.append(digits_only)

        # 結果を出力
        fname = 'test'+str(id)+'.png'
        fname_gray = 'test'+str(id)+'-gray'+'.png'
        cv2.imwrite('test.png', frame)
        cv2.imwrite(fname, roi_binary)
        cv2.imwrite(fname_gray, roi_gray)

    # output .csv file.
    with open(csvfname, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(digits_only_list)
    # debug
    print([f'{elapsed_time:.2f}', *digits_only_list, ' <---org:', *digits_only_list_debug])

# release
video_capture.release()