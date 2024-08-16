import cv2
import pytesseract
import time
import csv
import re

OUTPUT_FILENAME = r'measurement_recognition\2023-07-18 10-22-14.mkv'
# OUTPUT_FILENAME = 'output.csv'
# 動画ファイルを読み込む
video_path = r'C:\Users\4084224\work\recording_tool\video\2023-07-18 10-22-14.mkv'
cap = cv2.VideoCapture(video_path)

config = ("-c tessedit_char_whitelist=0123456789 --psm 6")

# 出力ファイルを開く
filename = OUTPUT_FILENAME
with open(filename, 'w', newline='') as output_file:
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(['Elapsed time', 'Text'])

    # 動画のフレームを1秒ごとに処理する
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % fps == 0:
            # 指定された領域の画像を切り取る (左上のx座標, y座標, 幅, 高さ)
            x, y, w, h = 710, 0, 330, 200
            # x, y, w, h = 880, 20, 80, 40
            roi = frame[y:y+h, x:x+w]

            # グレースケールに変換
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # 二値化
            _, roi_binary = cv2.threshold(roi_gray, 127, 255, cv2.THRESH_BINARY)

            # 文字認識を実行する
            text = pytesseract.image_to_string(roi_binary, lang='eng', config=config)

            # 経過時間を取得する
            elapsed_time = frame_count / fps

            # 数字のみを抽出
            digits_only = ''.join(re.findall(r'\d', text))

            # 結果をファイルに保存する
            csv_writer.writerow([f'{elapsed_time:.2f}', digits_only])
            print([f'{elapsed_time:.2f}', digits_only])

        frame_count += 1

    cap.release()