import sys
import os
import json
import math
import requests
import pyttsx3
from datetime import datetime
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QUrl, QTimer, QVariant, QPointF
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtPositioning import QGeoCoordinate

# OpenRouteService API キー（実際に使用する場合は自分のAPIキーに置き換えてください）
ORS_API_KEY = "5b3ce3597851110001cf6248598d70c197ae48ec92978dc2e778aab2"

class NavigationController(QObject):
    # シグナル定義
    routeFound = pyqtSignal(list, list, arguments=['coordinates', 'instructions'])
    positionUpdated = pyqtSignal(QGeoCoordinate, arguments=['coordinate'])
    nextInstruction = pyqtSignal(str, arguments=['instruction'])
    remainingDistance = pyqtSignal(float, arguments=['distance'])
    
    # 距離更新のための特別なシグナル（型情報を明示）
    updateDistance = pyqtSignal(float, arguments=['meters'])
    
    # ルートデバッグ情報用のシグナル
    routeDebugInfo = pyqtSignal(list, arguments=['debug_info'])
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 基本変数の初期化
        self.route_coordinates = []
        self.route_instructions = []
        self.current_route_index = 0
        self.current_instruction_index = 0
        self.update_count = 0
        self.simulation_active = False
        
        # タイマーの初期化
        self.simulation_speed = 100  # メートル/秒
        self.simulation_interval = 200  # ミリ秒
        self.single_timer = QTimer(self)  # タイマーオブジェクトを作成
        self.single_timer.setSingleShot(True)  # 単発実行モード
        self.single_timer.timeout.connect(self.moveToNextPosition)  # タイムアウト時に実行する関数
        
        # 音声合成エンジンの初期化
        self.speech_engine = pyttsx3.init()
        try:
            voices = self.speech_engine.getProperty('voices')
            for voice in voices:
                if 'japanese' in voice.name.lower() or 'ja' in voice.id.lower():
                    self.speech_engine.setProperty('voice', voice.id)
                    break
        except:
            pass
        self.speech_engine.setProperty('rate', 150)
        
        # デバッグ用
        print("NavigationControllerが初期化されました")
    
    # デモ走行のリセット用関数
    def reInitializeTimer(self):
        """タイマーを再初期化する（問題解決用）"""
        if hasattr(self, 'single_timer') and self.single_timer is not None:
            if self.single_timer.isActive():
                self.single_timer.stop()
        
        # 新しいタイマーを作成
        self.single_timer = QTimer(self)
        self.single_timer.setSingleShot(True)
        self.single_timer.timeout.connect(self.moveToNextPosition)
        print("タイマーが再初期化されました")
    
    @pyqtSlot(QGeoCoordinate, QGeoCoordinate)
    def calculateRoute(self, start, end):
        """OpenRouteService APIを使用して、開始点から目的地までのルートを計算"""
        try:
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml',
                'Authorization': ORS_API_KEY,
                'Content-Type': 'application/json; charset=utf-8'
            }
            
            body = {
                "coordinates": [
                    [start.longitude(), start.latitude()],
                    [end.longitude(), end.latitude()]
                ],
                "instructions": "true",
                "language": "ja",
                # 道路に沿ったルート検索を確実にするための追加パラメータ
                "preference": "recommended",  # 推奨ルート
                "units": "m",  # メートル単位
                "geometry": "true",  # 道路の形状を含む
                "continue_straight": "true"  # 可能な限り直進
            }
            
            response = requests.post(url, json=body, headers=headers)
            
            if response.status_code != 200:
                print(f"ルート取得エラー: {response.status_code}, {response.text}")
                # APIエラー時のフォールバックルートを生成
                self.createFallbackRoute(start, end)
                return
                
            route_data = response.json()
            
            # 座標データの抽出
            geometry = route_data['routes'][0]['geometry']
            if isinstance(geometry, str):  # エンコードされたpolylineの場合
                # polylineをデコードする必要がある
                coordinates = self.decodePolyline(geometry)
            elif isinstance(geometry, dict) and 'coordinates' in geometry:  # GeoJSON形式の場合
                coordinates = geometry['coordinates']
            else:
                print("不明なジオメトリ形式です。フォールバックルートを使用します。")
                self.createFallbackRoute(start, end)
                return
            
            # QGeoCoordinate リストに変換
            coords_list = []
            for lon, lat in coordinates:
                coords_list.append(QGeoCoordinate(lat, lon))
            
            # 経路案内指示の抽出
            steps = route_data['routes'][0]['segments'][0]['steps']
            instructions_list = []
            for step in steps:
                instruction = {
                    'text': step['instruction'],
                    'distance': step['distance'],
                    'index': step['way_points'][0]  # この指示が適用される座標のインデックス
                }
                instructions_list.append(instruction)
            
            # 結果を保存してシグナル発信（デバッグ情報を追加）
            self.route_coordinates = coords_list
            self.route_instructions = instructions_list
            
            # 経由ポイントのデバッグ情報を追加
            debug_info = []
            # 重要ポイントのみ表示（全点だと多すぎるため間引く）
            sampling_interval = max(1, len(coords_list) // 20)  # 最大20点になるよう間引く
            for i in range(0, len(coords_list), sampling_interval):
                coord = coords_list[i]
                # このポイントに関連する指示があるかチェック
                instruction_text = ""
                for instr in instructions_list:
                    if instr['index'] == i:
                        instruction_text = instr['text']
                        break
                
                debug_info.append({
                    'index': i,
                    'coord': coord,
                    'instruction': instruction_text
                })
            
            # 指示ポイントは必ず含める
            for instr in instructions_list:
                idx = instr['index']
                if idx % sampling_interval != 0:  # 既に追加済みでない場合
                    found = False
                    for info in debug_info:
                        if info['index'] == idx:
                            found = True
                            break
                    
                    if not found:
                        debug_info.append({
                            'index': idx,
                            'coord': coords_list[idx],
                            'instruction': instr['text']
                        })
            
            # デバッグ情報をインデックス順にソート
            debug_info.sort(key=lambda x: x['index'])
            
            # ルート情報とデバッグ情報を送信
            self.routeFound.emit(coords_list, instructions_list)
            self.routeDebugInfo.emit(debug_info)
            
            print(f"道路に沿ったルートが見つかりました: {len(coords_list)}ポイント, {len(instructions_list)}指示")
            
            # デモ用：APIキーが設定されていない場合や座標リストが空の場合にフォールバック
            if len(coords_list) == 0:
                self.createFallbackRoute(start, end)
            
        except Exception as e:
            print(f"ルート計算エラー: {str(e)}")
            # エラーが発生した場合でもデモ用のサンプルルートを生成
            self.createFallbackRoute(start, end)
    
    def decodePolyline(self, encoded):
        """エンコードされたポリラインをデコードする関数
        （OpenRouteServiceのポリラインはGoogle形式）"""
        try:
            # ポリラインデコードの実装
            coords = []
            index = 0
            lat = 0
            lng = 0
            
            while index < len(encoded):
                # 緯度のデコード
                shift, result = 0, 0
                while True:
                    b = ord(encoded[index]) - 63
                    index += 1
                    result |= (b & 0x1f) << shift
                    shift += 5
                    if b < 0x20:
                        break
                dlat = ~(result >> 1) if result & 1 else result >> 1
                lat += dlat
                
                # 経度のデコード
                shift, result = 0, 0
                while True:
                    b = ord(encoded[index]) - 63
                    index += 1
                    result |= (b & 0x1f) << shift
                    shift += 5
                    if b < 0x20:
                        break
                dlng = ~(result >> 1) if result & 1 else result >> 1
                lng += dlng
                
                # 座標リストに追加
                coords.append([lng * 1e-5, lat * 1e-5])
            
            return coords
        except Exception as e:
            print(f"ポリラインデコードエラー: {str(e)}")
            return []
    
    def createFallbackRoute(self, start, end):
        """APIが利用できない場合のための道路に沿ったフォールバックルートを生成"""
        print("道路に沿ったフォールバックルートを生成します")
        # 直線ではなく、いくつかの中間点を追加して道路風に見せる
        coords_list = []
        
        # 出発点
        coords_list.append(start)
        
        # 中間点をいくつか追加して曲がりくねった道のように見せる
        s_lat = start.latitude()
        s_lon = start.longitude()
        e_lat = end.latitude()
        e_lon = end.longitude()
        
        # 中間点の数
        midpoints = 4
        
        for i in range(1, midpoints + 1):
            # 基本的な直線補間
            frac = i / (midpoints + 1)
            mid_lat = s_lat + (e_lat - s_lat) * frac
            mid_lon = s_lon + (e_lon - s_lon) * frac
            
            # ランダム性を加えて道路のような曲がりを表現
            # Pythonの組み込みモジュールmathを使用
            variation = 0.0005 * math.sin(i * math.pi)  # 小さな変動
            
            if i % 2 == 0:  # 偶数番目は緯度を変動
                mid_lat += variation
            else:  # 奇数番目は経度を変動
                mid_lon += variation
            
            coords_list.append(QGeoCoordinate(mid_lat, mid_lon))
        
        # 目的地
        coords_list.append(end)
        
        # フォールバック指示を作成
        instructions_list = [
            {
                'text': '出発地点から前方へ進みます',
                'distance': 0,
                'index': 0
            }
        ]
        
        # 中間指示を追加
        total_distance = 0
        for i in range(len(coords_list) - 1):
            distance = coords_list[i].distanceTo(coords_list[i + 1])
            total_distance += distance
            
            if i + 1 < len(coords_list) - 1:  # 最後の指示の前
                direction = self.getDirection(coords_list[i], coords_list[i + 1], coords_list[i + 2])
                instructions_list.append({
                    'text': f'{direction}に進みます',
                    'distance': distance,
                    'index': i + 1
                })
        
        # 最後の指示
        instructions_list.append({
            'text': '目的地に到着します',
            'distance': 0,
            'index': len(coords_list) - 1
        })
        
        # 結果を設定
        self.route_coordinates = coords_list
        self.route_instructions = instructions_list
        self.routeFound.emit(coords_list, instructions_list)
        
        # デバッグ情報も送信
        debug_info = []
        for i, coord in enumerate(coords_list):
            # このポイントに関連する指示があるかチェック
            instruction_text = ""
            for instr in instructions_list:
                if instr['index'] == i:
                    instruction_text = instr['text']
                    break
            
            debug_info.append({
                'index': i,
                'coord': coord,
                'instruction': instruction_text
            })
        
        self.routeDebugInfo.emit(debug_info)
    
    def getDirection(self, p1, p2, p3):
        """3点から方向を計算"""
        # p1->p2方向とp2->p3方向の角度変化から方向を判定
        bearing1 = self.calculateBearing(p1, p2)
        bearing2 = self.calculateBearing(p2, p3)
        
        # 角度の差を計算（-180〜180度の範囲）
        angle_diff = ((bearing2 - bearing1 + 180) % 360) - 180
        
        if -30 <= angle_diff <= 30:
            return "そのまま直進"
        elif 30 < angle_diff <= 120:
            return "右"
        elif -120 <= angle_diff < -30:
            return "左"
        else:
            return "Uターン"
    
    def calculateBearing(self, start, end):
        """2点間の方位角を計算"""
        # 緯度経度をラジアンに変換
        lat1 = math.radians(start.latitude())
        lon1 = math.radians(start.longitude())
        lat2 = math.radians(end.latitude())
        lon2 = math.radians(end.longitude())
        
        # 方位角の計算
        y = math.sin(lon2 - lon1) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        bearing = math.atan2(y, x)
        
        # ラジアンから度に変換（0〜360度）
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    @pyqtSlot()
    def startSimulation(self):
        """デモ走行を開始"""
        try:
            print("\n===== デモ走行の開始 =====")
            
            # 初期化を確認
            self.reInitializeTimer()
            
            if not self.route_coordinates:
                print("ルートが計算されていません")
                return
            
            # ルートの妥当性をチェック
            if len(self.route_coordinates) < 2:
                print("エラー: ルートポイントが不足しています")
                return
                
            # 極端に近いポイントを事前に除去（前処理）
            cleaned_route = [self.route_coordinates[0]]  # 最初のポイントは必ず含める
            for i in range(1, len(self.route_coordinates)):
                # 前のポイントとの距離を計算
                prev = cleaned_route[-1]
                curr = self.route_coordinates[i]
                dist = prev.distanceTo(curr)
                
                # 距離が閾値以上、または最後のポイントなら追加
                if dist >= 0.01 or i == len(self.route_coordinates) - 1:
                    cleaned_route.append(curr)
            
            # クリーニングの結果を表示
            removed = len(self.route_coordinates) - len(cleaned_route)
            if removed > 0:
                print(f"前処理: {removed}個の近接ポイントを除去しました（{len(self.route_coordinates)}→{len(cleaned_route)}）")
                self.route_coordinates = cleaned_route
            
            # シミュレーションが確実に動くように状態をリセット
            self.current_route_index = 0
            self.current_instruction_index = 0
            self.update_count = 0
            self.simulation_active = True
            
            # 最初の位置を更新
            if self.route_coordinates:
                self.positionUpdated.emit(self.route_coordinates[0])
            
            # 出発のアナウンス
            departure_message = "案内を開始します。ルートに従って走行してください。"
            self.nextInstruction.emit(departure_message)
            self.speakInstruction(departure_message)
            
            # 最初の指示も発声
            if len(self.route_instructions) > 0:
                first_instruction = self.route_instructions[0]['text']
                distance = self.route_instructions[0]['distance']
                
                # 距離を丸めて音声案内テキストを作成
                if distance > 1000:
                    distance_text = f"{round(distance / 1000, 1)}キロメートル先、{first_instruction}"
                else:
                    distance_text = f"{round(distance)}メートル先、{first_instruction}"
                    
                # 0.5秒後に指示を発声（初期アナウンスと重ならないよう少し遅延）
                QTimer.singleShot(500, lambda: self.speakInstruction(distance_text))
            
            # 残り距離の計算と通知
            if len(self.route_coordinates) > 1:
                total_distance = 0
                for i in range(len(self.route_coordinates) - 1):
                    total_distance += self.route_coordinates[i].distanceTo(self.route_coordinates[i + 1])
                
                # 確実に初期距離を送信（複数回、複数の方法で）
                print(f"初期総距離を送信: {total_distance:.1f}m")
                self.remainingDistance.emit(float(total_distance))
                self.updateDistance.emit(float(total_distance))
                
                # 少し遅れてもう一度送信（UIの準備ができていない可能性に対応）
                QTimer.singleShot(100, lambda d=total_distance: self.remainingDistance.emit(float(d)))
                QTimer.singleShot(300, lambda d=total_distance: self.updateDistance.emit(float(d)))
                QTimer.singleShot(500, lambda d=total_distance: self.remainingDistance.emit(float(d)))
                print(f"総距離: {total_distance:.1f}m")
            
            # シングルショットタイマーを開始
            print(f"位置更新タイマーを開始します (間隔 {self.simulation_interval}ms)")
            self.single_timer.start(100)  # 最初は少し早く開始
            
            print(f"シミュレーション開始: ルートポイント数 = {len(self.route_coordinates)}, 指示数 = {len(self.route_instructions)}")
        
        except Exception as e:
            print(f"シミュレーション開始中にエラーが発生: {str(e)}")
            import traceback
            traceback.print_exc()  # スタックトレースを出力
    
    @pyqtSlot()
    def manualStartDemo(self):
        """QMLから直接呼び出すための代替デモ開始関数"""
        print("manualStartDemoが呼び出されました")
        try:
            # タイマーを使わずに直接更新を開始
            self.current_route_index = 0
            self.current_instruction_index = 0
            self.update_count = 0
            self.simulation_active = True
            
            if self.route_coordinates:
                # 最初の位置を設定
                self.positionUpdated.emit(self.route_coordinates[0])
                
                # 残り距離の初期値を計算して送信
                if len(self.route_coordinates) > 1:
                    total_distance = 0
                    for i in range(len(self.route_coordinates) - 1):
                        total_distance += self.route_coordinates[i].distanceTo(self.route_coordinates[i + 1])
                    
                    # 両方の方法で送信
                    print(f"代替方法: 初期距離を送信 {total_distance:.1f}m")
                    self.remainingDistance.emit(float(total_distance))
                    self.updateDistance.emit(float(total_distance))
                
                # 代替方法: QTimerの代わりにQtのシングルショットを使用
                QTimer.singleShot(100, self.moveToNextPosition)
                
                print("代替方法でデモ開始しました")
                return True
            else:
                print("代替方法でもルートがありません")
                return False
        except Exception as e:
            print(f"代替デモ開始でエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @pyqtSlot()
    def stopSimulation(self):
        """デモ走行を停止"""
        print(f"\n===== デモ走行の停止 =====")
        self.simulation_active = False
        
        if self.single_timer.isActive():
            print("実行中のタイマーを停止します")
            self.single_timer.stop()
        
        print(f"シミュレーション停止: 合計更新回数 = {self.update_count}")
        
        # 走行中に停止された場合、最終的な状態を通知
        if self.current_route_index < len(self.route_coordinates) - 1:
            print(f"途中で停止: 現在位置 = {self.current_route_index}/{len(self.route_coordinates)-1}")
        else:
            print("正常に終了: 目的地に到着しました")
    
    def moveToNextPosition(self):
        """位置を次に移動し、シングルショットタイマーで次の更新をスケジュール"""
        try:
            if not self.simulation_active:
                print("シミュレーションが停止されています")
                return
                
            # 更新カウントを増加
            self.update_count += 1
            
            # 経過時間から最大更新回数を計算し、無限ループ防止
            if self.update_count > 5000:  # 経験的な上限値
                print("警告: 更新回数が上限に達しました。シミュレーションを停止します。")
                self.stopSimulation()
                return
            
            # ルートが存在し、終点に達していないことを確認
            if not self.route_coordinates:
                print("ルートが設定されていません")
                self.stopSimulation()
                return
                
            # 目的地に到達したかどうかをチェック
            if self.current_route_index >= len(self.route_coordinates) - 1:
                # 最後のポイントに移動
                self.positionUpdated.emit(self.route_coordinates[-1])
                
                # 目的地到着のアナウンス
                arrival_message = "目的地に到着しました"
                self.nextInstruction.emit(arrival_message)
                self.speakInstruction(arrival_message)
                
                print(f"シミュレーション完了: 更新回数 = {self.update_count}")
                self.stopSimulation()
                return
            
            # 現在位置と次の位置
            current_pos = self.route_coordinates[self.current_route_index]
            next_pos = self.route_coordinates[self.current_route_index + 1]
            
            # 二点間の距離を計算
            distance = current_pos.distanceTo(next_pos)
            
            # 1回の更新で移動する距離を計算
            distance_to_move = self.simulation_speed * (self.simulation_interval / 10000.0)
            
            print("distance:",distance, "distance_to_move",distance_to_move)
            # 距離がゼロまたは非常に小さい場合の対策
            if distance < 0.01:  # 1cm未満の場合
                print(f"警告: ポイント間の距離が極端に小さい ({distance:.6f}m) - インデックス {self.current_route_index}")
                # 次のポイントに強制的に進む
                self.current_route_index += 1
                
                # 次のポイントが存在する場合はそこへ移動
                if self.current_route_index < len(self.route_coordinates):
                    self.positionUpdated.emit(self.route_coordinates[self.current_route_index])
                    # 次の更新をスケジュール
                    if self.simulation_active:
                        self.single_timer.start(self.simulation_interval)
                    return
                else:
                    # 最後のポイントだった場合は終了
                    self.current_route_index = len(self.route_coordinates) - 1
                    self.positionUpdated.emit(self.route_coordinates[-1])
                    self.stopSimulation()
                    return
            
            # 次の位置を計算
#            if distance <= distance_to_move:
            if True:
                # 次のポイントまで到達する距離なので、次のポイントへ進む
                self.current_route_index += 1
                
                # 残りの距離が大きい場合は複数ポイント進む
                remaining_distance = distance_to_move - distance
                loop_count = 0  # 安全のためのループカウンター
                
                while remaining_distance > 0 and self.current_route_index < len(self.route_coordinates) - 1 and loop_count < 100:
                    loop_count += 1  # 無限ループ防止
                    
                    current_pos = self.route_coordinates[self.current_route_index]
                    next_pos = self.route_coordinates[self.current_route_index + 1]
                    
                    distance = current_pos.distanceTo(next_pos)
                    
                    # 距離がゼロまたは非常に小さい場合
                    if distance < 0.01:  # 1cm未満
                        print(f"警告: ループ内でポイント間の距離が極端に小さい ({distance:.6f}m)")
                        self.current_route_index += 1
                        continue
                    
                    if distance <= remaining_distance:
                        self.current_route_index += 1
                        remaining_distance -= distance
                    else:
                        # 次のポイントより手前で止まる
                        if distance > 0:  # ゼロ除算防止
                            fraction = remaining_distance / distance
                            delta_lat = next_pos.latitude() - current_pos.latitude()
                            delta_lon = next_pos.longitude() - current_pos.longitude()
                            
                            next_lat = current_pos.latitude() + (delta_lat * fraction)
                            next_lon = current_pos.longitude() + (delta_lon * fraction)
                            
                            # 補間された位置を報告
                            intermediate_position = QGeoCoordinate(next_lat, next_lon)
                            self.positionUpdated.emit(intermediate_position)
                        break
                
                if loop_count >= 100:
                    print("警告: ルートポイント処理でループ回数の上限に達しました")
                
                # インデックス境界チェック
                if self.current_route_index >= len(self.route_coordinates):
                    self.current_route_index = len(self.route_coordinates) - 1
                
                # 現在位置の更新（抜けていたコード）
                current_position = self.route_coordinates[self.current_route_index]
                self.positionUpdated.emit(current_position)
            else:

                print("distance_to_move",distance_to_move)
                # 次のポイントまで届かないので、途中の位置を計算
                if distance > 0:  # ゼロ除算防止
                    fraction = distance_to_move / distance
                    delta_lat = next_pos.latitude() - current_pos.latitude()
                    delta_lon = next_pos.longitude() - current_pos.longitude()
                    next_lat = current_pos.latitude() + (delta_lat * fraction)
                    next_lon = current_pos.longitude() + (delta_lon * fraction)
                    
                    # 補間された位置を報告
                    intermediate_position = QGeoCoordinate(next_lat, next_lon)
                    print(f"中間位置に移動: {intermediate_position.latitude()}, {intermediate_position.longitude()}")
                    self.positionUpdated.emit(intermediate_position)
                else:
                    # 距離がゼロの場合は次のポイントに進む
                    print("警告: 距離がゼロのため次のポイントに強制移動します")
                    self.current_route_index += 1
                    if self.current_route_index < len(self.route_coordinates):
                        self.positionUpdated.emit(self.route_coordinates[self.current_route_index])
                    else:
                        # インデックス範囲外を防止
                        self.current_route_index = len(self.route_coordinates) - 1
                        self.positionUpdated.emit(self.route_coordinates[-1])
            
            # 指示チェック（次の曲がり角など）
            self.checkNextInstruction()
            
            # 残り距離計算
            remaining_distance = 0
            for i in range(self.current_route_index, len(self.route_coordinates) - 1):
                pos1 = self.route_coordinates[i]
                pos2 = self.route_coordinates[i + 1]
                remaining_distance += pos1.distanceTo(pos2)
            
            # 残り距離をシグナルで通知（確実に送信するために明示的に float に変換）
            self.remainingDistance.emit(float(remaining_distance))
            # バックアップとして両方のシグナルを送信
            self.updateDistance.emit(float(remaining_distance))
            
            # デバッグ出力
            if self.update_count % 5 == 0 or self.update_count < 5:
                print(f"残り距離シグナル発信: {remaining_distance:.1f}m")
            
            # 進捗を定期的に報告
            if self.update_count % 5 == 0 or self.update_count < 5:
                print(f"更新 {self.update_count}: 位置 {self.current_route_index}/{len(self.route_coordinates)-1}, 残り距離: {remaining_distance:.1f}m")
            
            # 次の更新をスケジュール
            if self.simulation_active:
                print(f"次の位置更新をスケジュール: カウント {self.update_count + 1}")
                self.single_timer.start(self.simulation_interval)
            else:
                print("シミュレーションが非アクティブなため、次の更新はスケジュールされません")
        
        except Exception as e:
            print(f"位置更新中にエラーが発生しました: {str(e)}")
            # エラーが発生しても次の更新をスケジュール
            if self.simulation_active:
                print("エラー後も次の更新をスケジュール")
                self.single_timer.start(self.simulation_interval)
    
    def checkNextInstruction(self):
        """次の指示があるかをチェックして、必要なら通知"""
        if not self.route_instructions or self.current_instruction_index >= len(self.route_instructions) - 1:
            return
        
        next_instruction = self.route_instructions[self.current_instruction_index + 1]
        instruction_point_index = next_instruction['index']
        
        # 事前通知ポイント数（値を大きくすると早めに通知）
        advance_notice_points = 5
        
        # 現在のルートインデックスが次の指示のポイントに近づいたら
        if self.current_route_index >= instruction_point_index - advance_notice_points:
            self.current_instruction_index += 1
            instruction_text = next_instruction['text']
            distance = next_instruction['distance']
            
            # 距離を丸めて音声案内テキストを作成
            if distance > 1000:
                distance_text = f"{round(distance / 1000, 1)}キロメートル先、{instruction_text}"
            else:
                distance_text = f"{round(distance)}メートル先、{instruction_text}"
            
            # 指示を通知して音声案内
            self.nextInstruction.emit(distance_text)
            self.speakInstruction(distance_text)
    
    def speakInstruction(self, text):
        """音声案内を行う"""
#        return
        try:
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
        except Exception as e:
            print(f"音声案内エラー: {str(e)}")
            # エラーが発生した場合でもアプリは継続

def main():
    app = QGuiApplication(sys.argv)
    
    # NavigationController インスタンスを作成
    nav_controller = NavigationController()
    
    # QML エンジンを設定
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("navController", nav_controller)
    
    # QML ファイルをロード
    engine.load(QUrl.fromLocalFile("navigation.qml"))
    
    if not engine.rootObjects():
        return -1
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())