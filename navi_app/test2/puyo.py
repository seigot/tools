import pygame
import random
import sys
import time
import math
import os
import threading
import pyttsx3
from pygame.locals import *

# 色の定義
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (32, 0, 64)  # ぷよぷよ通の背景色に近い暗い青紫色

# 音声ファイルのパスを設定
SOUND_DIR = 'sounds'
# フォルダが存在しない場合は作成
if not os.path.exists(SOUND_DIR):
    os.makedirs(SOUND_DIR)

# 効果音のファイル名
ROTATE_SOUND = os.path.join(SOUND_DIR, 'rotate.wav')
MOVE_SOUND = os.path.join(SOUND_DIR, 'move.wav')
DROP_SOUND = os.path.join(SOUND_DIR, 'drop.wav')
POP_SOUND = os.path.join(SOUND_DIR, 'pop.wav')
GAMEOVER_SOUND = os.path.join(SOUND_DIR, 'gameover.wav')

# 連鎖ボイステキスト
VOICE_2_CHAIN_TEXT = "ファイヤー"
VOICE_3_CHAIN_TEXT = "アイスストーム"
VOICE_4_CHAIN_TEXT = "ダイアキュート"
VOICE_5_CHAIN_TEXT = "ばよえーん"

# ゲームの設定
FPS = 60
CELL_SIZE = 40  # 各ぷよのサイズ
COLS = 6  # 列数
ROWS = 12  # 行数
WINDOW_WIDTH = CELL_SIZE * (COLS + 6)  # 盤面 + 次のぷよを表示するスペース
WINDOW_HEIGHT = CELL_SIZE * ROWS
PUYO_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

class PuyoPuyo:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('ぷよぷよ')
        
        # テキスト・トゥ・スピーチエンジンの初期化
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # 速度設定
            
            # 日本語用の音声が利用可能な場合は設定
            try:
                voices = self.tts_engine.getProperty('voices')
                japanese_voice = None
                for voice in voices:
                    if 'japanese' in voice.name.lower() or 'ja' in voice.id.lower():
                        japanese_voice = voice.id
                        break
                
                if japanese_voice:
                    self.tts_engine.setProperty('voice', japanese_voice)
            except:
                pass  # 日本語音声が見つからない場合はデフォルトを使用
        except Exception as e:
            print(f"テキスト・トゥ・スピーチの初期化に失敗しました: {e}")
            self.tts_engine = None
        
        # フォント設定
        self.font = pygame.font.SysFont(None, 36)
        
        # 音楽と効果音の生成
        self.create_sounds()
        
        # ゲーム状態の初期化
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current_puyo = None
        self.next_puyo = None
        self.falling = False
        self.chain_count = 0
        self.score = 0
        self.game_over = False
        self.fall_speed = 0.5  # 落下速度（秒）
        self.last_fall_time = time.time()
        
        # 消去エフェクト用の変数
        self.pop_effects = []  # [(row, col, color, radius, lifetime), ...]
        self.is_popping = False
        
        # ボイス再生中フラグ
        self.is_voice_playing = False
        
        # 最初のぷよを生成
        self.generate_puyo()
        self.generate_puyo()
        
    def generate_puyo(self):
        """次のぷよのペアを生成する"""
        if self.next_puyo:
            self.current_puyo = self.next_puyo
        else:
            # 最初のぷよのペアを生成する
            color1 = random.choice(PUYO_COLORS)
            color2 = random.choice(PUYO_COLORS)
            self.current_puyo = {
                'positions': [(COLS // 2, 0), (COLS // 2, 1)],  # (列, 行)
                'colors': [color1, color2],
                'rotation': 0  # 0: 縦, 1: 右, 2: 下, 3: 左
            }
            
        # 次のぷよのペアを生成
        color1 = random.choice(PUYO_COLORS)
        color2 = random.choice(PUYO_COLORS)
        self.next_puyo = {
            'positions': [(COLS // 2, 0), (COLS // 2, 1)],
            'colors': [color1, color2],
            'rotation': 0
        }
        
        # ゲームオーバーチェック: 新しいぷよを置く場所がない場合
        for pos in self.current_puyo['positions']:
            if pos[1] < ROWS and pos[0] < COLS and self.board[pos[1]][pos[0]]:
                self.game_over = True
                # ゲームオーバー音を再生
                self.gameover_sound.play()
                # ゲームオーバーボイス (テキスト・トゥ・スピーチが初期化されている場合のみ)
                if self.tts_engine:
                    self.play_voice("ゲームオーバー")
                
    def create_sounds(self):
        """効果音を生成する"""
        # 効果音のダミーファイルを生成
        def create_dummy_sound(file_path, freq=440, duration=0.5):
            if not os.path.exists(file_path):
                sample_rate = 44100
                samples = int(duration * sample_rate)
                buffer = bytearray()
                
                for i in range(samples):
                    # 効果音のサイン波を生成
                    value = int(127 + 127 * math.sin(2 * math.pi * freq * i / sample_rate))
                    buffer.append(value)
                
                # WAVフォーマットのヘッダーを追加
                with open(file_path, 'wb') as f:
                    # チャンクサイズ (4バイト)
                    chunk_size = 36 + len(buffer)
                    # WAVヘッダー
                    f.write(b'RIFF')
                    f.write(chunk_size.to_bytes(4, byteorder='little'))
                    f.write(b'WAVE')
                    
                    # fmtチャンク
                    f.write(b'fmt ')
                    f.write((16).to_bytes(4, byteorder='little'))  # サブチャンクサイズ
                    f.write((1).to_bytes(2, byteorder='little'))   # フォーマットID (1: PCM)
                    f.write((1).to_bytes(2, byteorder='little'))   # チャンネル数 (1: モノラル)
                    f.write(sample_rate.to_bytes(4, byteorder='little'))  # サンプリングレート
                    f.write((sample_rate).to_bytes(4, byteorder='little'))  # バイトレート
                    f.write((1).to_bytes(2, byteorder='little'))   # ブロックサイズ
                    f.write((8).to_bytes(2, byteorder='little'))   # ビット深度
                    
                    # dataチャンク
                    f.write(b'data')
                    f.write(len(buffer).to_bytes(4, byteorder='little'))
                    f.write(buffer)
        
        # 効果音
        create_dummy_sound(ROTATE_SOUND, freq=880, duration=0.1)  # 高い音
        create_dummy_sound(MOVE_SOUND, freq=440, duration=0.1)    # 中くらいの音
        create_dummy_sound(DROP_SOUND, freq=330, duration=0.2)    # 少し低い音
        create_dummy_sound(POP_SOUND, freq=660, duration=0.3)     # 消える音
        create_dummy_sound(GAMEOVER_SOUND, freq=180, duration=1.0)  # ゲームオーバー音
        
        # 音声をロード
        try:
            self.rotate_sound = pygame.mixer.Sound(ROTATE_SOUND)
            self.move_sound = pygame.mixer.Sound(MOVE_SOUND)
            self.drop_sound = pygame.mixer.Sound(DROP_SOUND)
            self.pop_sound = pygame.mixer.Sound(POP_SOUND)
            self.gameover_sound = pygame.mixer.Sound(GAMEOVER_SOUND)
        except:
            print("音声ファイルの読み込みに失敗しました。")
    
    def play_voice(self, text):
        """テキスト・トゥ・スピーチでボイスを再生する（別スレッドで実行）"""
        if self.is_voice_playing:
            return
            
        self.is_voice_playing = True
        
        def speak_text():
            try:
                # 音声エンジンが既に使用中の場合に備えてtry-except内で実行
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"音声再生エラー: {e}")
            finally:
                self.is_voice_playing = False
                
        # 別スレッドで音声を再生（ゲームの処理をブロックしないため）
        thread = threading.Thread(target=speak_text)
        thread.daemon = True  # メインスレッドが終了したら強制終了
        thread.start()
    
    def rotate_puyo(self, direction):
        """ぷよを回転させる"""
        if not self.current_puyo:
            return
            
        # 元の位置を保存
        old_positions = self.current_puyo['positions'][:]
        old_rotation = self.current_puyo['rotation']
        
        # 回転方向を計算 (1: 時計回り, -1: 反時計回り)
        new_rotation = (old_rotation + direction) % 4
        self.current_puyo['rotation'] = new_rotation
        
        # 軸ぷよの位置
        axis_x, axis_y = old_positions[0]
        
        # 2つ目のぷよの位置を回転に応じて計算
        if new_rotation == 0:  # 上
            new_pos = (axis_x, axis_y - 1)
        elif new_rotation == 1:  # 右
            new_pos = (axis_x + 1, axis_y)
        elif new_rotation == 2:  # 下
            new_pos = (axis_x, axis_y + 1)
        else:  # 左
            new_pos = (axis_x - 1, axis_y)
            
        # 新しい位置が有効かチェック
        if not self.is_valid_position(new_pos):
            # 回転できない場合、元に戻す
            self.current_puyo['positions'] = old_positions
            self.current_puyo['rotation'] = old_rotation
            return
            
        # 位置を更新
        self.current_puyo['positions'] = [old_positions[0], new_pos]
        
        # 回転音を再生
        self.rotate_sound.play()
        
    def is_valid_position(self, position):
        """指定した位置が有効かチェックする"""
        x, y = position
        
        # 画面外チェック
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return False
            
        # 他のぷよとの衝突チェック
        if y >= 0 and x >= 0 and x < COLS and y < ROWS and self.board[y][x]:
            return False
            
        return True
        
    def move_puyo(self, dx):
        """ぷよを左右に移動させる"""
        if not self.current_puyo or self.falling:
            return
            
        # 元の位置を保存
        old_positions = self.current_puyo['positions'][:]
        
        # 新しい位置を計算
        new_positions = [(pos[0] + dx, pos[1]) for pos in old_positions]
        
        # 新しい位置が有効かチェック
        if all(self.is_valid_position(pos) for pos in new_positions):
            self.current_puyo['positions'] = new_positions
            # 移動音を再生
            self.move_sound.play()
        
    def drop_puyo(self):
        """ぷよをすぐに落下させる"""
        if not self.current_puyo or self.falling:
            return
            
        while self.move_puyo_down(force=True):
            pass
            
        # 落下音を再生
        self.drop_sound.play()
            
    def move_puyo_down(self, force=False):
        """ぷよを1ステップ下に移動させる"""
        if not self.current_puyo:
            return False
            
        # 通常の落下なら時間チェック
        if not force and time.time() - self.last_fall_time < self.fall_speed:
            return False
            
        self.last_fall_time = time.time()
        
        # 元の位置を保存
        old_positions = self.current_puyo['positions'][:]
        
        # 新しい位置を計算
        new_positions = [(pos[0], pos[1] + 1) for pos in old_positions]
        
        # 新しい位置が有効かチェック
        if all(self.is_valid_position(pos) for pos in new_positions):
            self.current_puyo['positions'] = new_positions
            return True
        else:
            # ぷよを固定する
            for i, pos in enumerate(old_positions):
                if 0 <= pos[1] < ROWS and 0 <= pos[0] < COLS:
                    self.board[pos[1]][pos[0]] = self.current_puyo['colors'][i]
            
            # 落下プロセスを開始
            self.falling = True
            self.current_puyo = None
            return False
            
    def drop_floating_puyos(self):
        """宙に浮いているぷよを落とす"""
        dropped = False
        
        for col in range(COLS):
            # 各列を下から上に走査
            for row in range(ROWS-2, -1, -1):
                if self.board[row][col] and not self.board[row+1][col]:
                    # 下が空いているぷよを見つけた
                    color = self.board[row][col]
                    self.board[row][col] = None
                    
                    # 落下先を探す
                    drop_row = row + 1
                    while drop_row + 1 < ROWS and not self.board[drop_row+1][col]:
                        drop_row += 1
                        
                    self.board[drop_row][col] = color
                    dropped = True
                    
        return dropped
        
    def check_connections(self):
        """4つ以上つながっているぷよを探し、消去する"""
        visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
        to_remove = []
        
        # 各セルを調べる
        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col] and not visited[row][col]:
                    # まだチェックしていないぷよを見つけた
                    color = self.board[row][col]
                    group = []
                    self._dfs(row, col, color, visited, group)
                    
                    # 4つ以上連結していれば削除リストに追加
                    if len(group) >= 4:
                        to_remove.extend(group)
                        
        # ぷよを消去
        if to_remove:
            self.chain_count += 1
            combo_bonus = min(999, len(to_remove) * self.chain_count * 10)
            self.score += combo_bonus
            
            # 消去エフェクトを追加
            for row, col in to_remove:
                color = self.board[row][col]
                # エフェクトを追加 (位置、色、初期半径、寿命)
                self.pop_effects.append([
                    col * CELL_SIZE + CELL_SIZE // 2,  # x
                    row * CELL_SIZE + CELL_SIZE // 2,  # y
                    color,  # 色
                    CELL_SIZE // 2,  # 初期半径
                    60  # 寿命 (フレーム数) - より長く表示
                ])
                self.board[row][col] = None
            
            # 連鎖ボイスを再生（テキスト・トゥ・スピーチが初期化されている場合のみ）
            if self.tts_engine:
                if self.chain_count == 1:
                    self.pop_sound.play()
                elif self.chain_count == 2:
                    # ファイヤー
                    self.play_voice(VOICE_2_CHAIN_TEXT)
                elif self.chain_count == 3:
                    # アイスストーム
                    self.play_voice(VOICE_3_CHAIN_TEXT)
                elif self.chain_count == 4:
                    # ダイアキュート
                    self.play_voice(VOICE_4_CHAIN_TEXT)
                elif self.chain_count >= 5:
                    # ばよえーん
                    self.play_voice(VOICE_5_CHAIN_TEXT)
            else:
                # テキスト・トゥ・スピーチが使えない場合は効果音だけ再生
                self.pop_sound.play()
                
            # 消去エフェクト中フラグを設定
            self.is_popping = True
                
            return True
        else:
            # 連鎖が途切れたのでカウンタをリセット
            self.chain_count = 0
            return False
            
    def _dfs(self, row, col, color, visited, group):
        """深さ優先探索で同じ色のぷよを探す"""
        # 範囲外チェック
        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            return
            
        # 既に訪問済みか、色が違う場合はスキップ
        if visited[row][col] or self.board[row][col] != color:
            return
            
        # 訪問済みにして、グループに追加
        visited[row][col] = True
        group.append((row, col))
        
        # 4方向を探索
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            self._dfs(row + dr, col + dc, color, visited, group)
            
    def update_pop_effects(self):
        """消去エフェクトを更新する"""
        # 残っているエフェクトがなければ、エフェクト終了
        if not self.pop_effects:
            self.is_popping = False
            return
            
        # 各エフェクトを更新
        for i in range(len(self.pop_effects) - 1, -1, -1):
            # エフェクトの寿命を減らす
            self.pop_effects[i][4] -= 1
            
            # 寿命が尽きたらエフェクトを削除
            if self.pop_effects[i][4] <= 0:
                self.pop_effects.pop(i)
    
    def update(self):
        """ゲームの状態を更新する"""
        if self.game_over:
            return
            
        # 消去エフェクト中なら、エフェクトのみ更新
        if self.is_popping:
            self.update_pop_effects()
            return
            
        if self.falling:
            # 浮いているぷよを落とす
            if not self.drop_floating_puyos():
                # もう落ちるぷよがなければ連結チェック
                if not self.check_connections():
                    # 消せるぷよがなければ次のぷよを生成
                    self.falling = False
                    self.generate_puyo()
        else:
            # 現在のぷよを下に移動
            self.move_puyo_down()
            
    def draw(self):
        """ゲーム画面を描画する"""
        self.screen.fill(BACKGROUND)
        
        # 盤面を描画
        for row in range(ROWS):
            for col in range(COLS):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                
                # グリッド線
                pygame.draw.rect(self.screen, (50, 50, 50), (x, y, CELL_SIZE, CELL_SIZE), 1)
                
                # ぷよを描画
                if self.board[row][col]:
                    self.draw_puyo(x, y, self.board[row][col])
                    
        # 現在のぷよを描画
        if self.current_puyo:
            for i, pos in enumerate(self.current_puyo['positions']):
                x = pos[0] * CELL_SIZE
                y = pos[1] * CELL_SIZE
                self.draw_puyo(x, y, self.current_puyo['colors'][i])
                
        # 次のぷよを描画
        if self.next_puyo:
            next_x = (COLS + 2) * CELL_SIZE
            self.screen.blit(self.font.render('NEXT', True, WHITE), (next_x, 20))
            
            for i, pos in enumerate([(0, 0), (0, 1)]):
                x = next_x + pos[0] * CELL_SIZE
                y = 60 + pos[1] * CELL_SIZE
                self.draw_puyo(x, y, self.next_puyo['colors'][i])
                
        # 消去エフェクトを描画
        for x, y, color, radius, lifetime in self.pop_effects:
            # エフェクトの透明度を計算（寿命に応じて徐々に透明になる）
            alpha = int(255 * (lifetime / 60))
            # エフェクトの色（元の色に透明度を追加）
            effect_color = (*color[:3], alpha)
            
            # 膨張する円を描画（より緩やかに拡大）
            expanded_radius = CELL_SIZE // 2 + (60 - lifetime) * 1.0  # 拡大速度を遅く
            
            # 透明な円を描画するためのサーフェス
            surf = pygame.Surface((expanded_radius * 2, expanded_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, effect_color, (expanded_radius, expanded_radius), expanded_radius)
            self.screen.blit(surf, (x - expanded_radius, y - expanded_radius))
                
        # スコアを描画
        score_text = self.font.render(f'SCORE: {self.score}', True, WHITE)
        self.screen.blit(score_text, (COLS * CELL_SIZE + 10, 160))
        
        # チェーン数を表示
        if self.chain_count > 0:
            chain_text = self.font.render(f'{self.chain_count} CHAIN!', True, WHITE)
            self.screen.blit(chain_text, (COLS * CELL_SIZE + 10, 200))
            
        # ゲームオーバー表示
        if self.game_over:
            game_over_text = self.font.render('GAME OVER', True, RED)
            self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 18))
            
            restart_text = self.font.render('Press R to restart', True, WHITE)
            self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 30))
            
        pygame.display.update()
        
    def draw_puyo(self, x, y, color):
        """ぷよを描画する"""
        # ぷよの円
        pygame.draw.circle(self.screen, color, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 2 - 2)
        
        # ハイライト（光沢）
        highlight_radius = CELL_SIZE // 4
        pygame.draw.circle(self.screen, WHITE, (x + CELL_SIZE // 2 - highlight_radius // 2, 
                                              y + CELL_SIZE // 2 - highlight_radius // 2), 
                          highlight_radius)
                          
        # 輪郭
        pygame.draw.circle(self.screen, BLACK, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 
                          CELL_SIZE // 2 - 2, 2)
        
    def reset_game(self):
        """ゲームをリセットする"""
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current_puyo = None
        self.next_puyo = None
        self.falling = False
        self.chain_count = 0
        self.score = 0
        self.game_over = False
        self.pop_effects = []
        self.is_popping = False
        self.is_voice_playing = False
        
        # 最初のぷよを生成
        self.generate_puyo()
        self.generate_puyo()
        
    def run(self):
        """メインゲームループ"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    # クリーンアップ - 終了前にTTSエンジンを適切に停止
                    if self.tts_engine:
                        try:
                            self.tts_engine.stop()
                        except:
                            pass
                    sys.exit()
                    
                elif event.type == KEYDOWN:
                    if not self.game_over and not self.is_popping:
                        if event.key == K_LEFT:
                            self.move_puyo(-1)
                        elif event.key == K_RIGHT:
                            self.move_puyo(1)
                        elif event.key == K_UP:
                            self.rotate_puyo(1)  # 時計回り
                        elif event.key == K_z:
                            self.rotate_puyo(-1)  # 反時計回り
                        elif event.key == K_DOWN:
                            self.move_puyo_down(force=True)
                        elif event.key == K_SPACE:
                            self.drop_puyo()
                    
                    if event.key == K_r:  # Rキーでリスタート
                        self.reset_game()
                    elif event.key == K_ESCAPE:  # ESCキーで終了
                        running = False
                        
            # ゲーム状態の更新
            self.update()
            
            # 描画
            self.draw()
            
            self.clock.tick(FPS)
            
        # ゲーム終了時のクリーンアップ
        pygame.quit()
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass

def main():
    try:
        # pyttsx3ライブラリがインストールされているか確認
        import pyttsx3
    except ImportError:
        print("pyttsx3ライブラリがインストールされていません。")
        print("以下のコマンドでインストールしてください：")
        print("pip install pyttsx3")
        print("")
        input("Enterキーを押すと終了します...")
        sys.exit(1)
        
    game = PuyoPuyo()
    game.run()

if __name__ == '__main__':
    main()