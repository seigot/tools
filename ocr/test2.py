import cv2
import pytesseract
import re

# 動画ファイルからN秒毎にOCRする
N = 1

# 動画ファイル
video_path = r'/Users/seigo/Downloads/timer.mp4'
video_capture = cv2.VideoCapture(video_path)
# config
#  tessedit_char_whitelist: 検索対象の文字列を限定する
#  psm: 番号に応じてocrのアルゴリズムを切り替える（詳しくは、tesseract --help-psmを参照）
config = ("-c tessedit_char_whitelist=0123456789 --psm 4")

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
    # グレースケールに変換
    roi_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 二値化
    _, roi_binary = cv2.threshold(roi_gray, 127, 255, cv2.THRESH_BINARY)
    # 文字認識を実行する
    text = pytesseract.image_to_string(roi_binary, lang='eng', config=config)
    # 経過時間を取得する
    elapsed_time = frame_count / fps
    # 数字のみを抽出
    digits_only = ''.join(re.findall(r'\d', text))
    # 結果を出力
    print([f'{elapsed_time:.2f}', digits_only])

# release
video_capture.release()