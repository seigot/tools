import asyncio
import os
import base64
import tempfile
from datetime import datetime
from hume import AsyncHumeClient
from dotenv import load_dotenv
import itertools

# .envファイルから環境変数を読み込み
load_dotenv()
all_commands = []

# ヘルパー関数：音声データをカスタムファイル名で保存
def write_audio_to_custom_file(audio_data: bytes, description: str, suffix: str = ".wav") -> str:
    """音声データをカスタムファイル名で保存し、ファイルパスを返す"""
    # 現在時刻を取得（YYYYMMDD_HHMMSS形式）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 感情記述から安全なファイル名を作成（スペースをアンダースコアに置換）
    safe_description = description.replace(" ", "_").replace("and", "&")
    
    # カスタムファイル名を作成
    filename = f"hume_tts_{timestamp}_{safe_description}{suffix}"
    
    # 現在のディレクトリにファイルを保存
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    
    return filepath

async def main(tts_text, tts_description: str = "friendly and clear"):
    # Hume APIクライアントを初期化
    client = AsyncHumeClient(api_key=os.getenv("HUME_API_KEY"))
    
    try:
        # 変換開始時刻を記録
        start_time = datetime.now()
        
        # テキストを音声に変換
        response = await client.tts.synthesize_json(
            utterances=[
                {
                    "text": tts_text,
                    # description: 音声の特徴を指定（オプション）
                    "description": tts_description
                }
            ]
        )
        
        # 変換終了時刻を記録
        end_time = datetime.now()
        conversion_time = (end_time - start_time).total_seconds()
        
        # 生成された音声データを取得
        audio_base64 = response.generations[0].audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # カスタムファイル名で保存
        custom_file_path = write_audio_to_custom_file(audio_bytes, tts_description)
        
        print("---")
        print(f"音声ファイルが生成されました: {custom_file_path}")
        print(f"変換時間: {conversion_time:.2f}秒")
        print(f"感情設定: {tts_description}")
        print(f"Generation ID: {response.generations[0].generation_id}")
        
        # macOSの場合は以下のコマンドで再生可能
        print(f"再生するには以下を実行:") 
        print(f"afplay '{custom_file_path}'")
        all_commands.append(f"afplay '{custom_file_path}'")

        return custom_file_path
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def generate_combinations(primary_emotions, secondary_emotions, max_combinations=None):
    """感情の組み合わせを生成する"""
    combinations = []
    
    for primary in primary_emotions:
        for secondary in secondary_emotions:
            if primary != secondary:  # 同じ単語の重複を避ける
                combinations.append(f"{primary} and {secondary}")
    
    # 最大数の制限がある場合
    if max_combinations and len(combinations) > max_combinations:
        combinations = combinations[:max_combinations]
    
    return combinations

# 非同期関数を実行
if __name__ == "__main__":
    
    # 感情の要素を定義
    emotions_primary = [
        "excited", "warm", "authoritative", "calm", "professional", 
        "friendly", "dramatic", "soft", "happy", "serious"
    ]
    
    emotions_secondary = [
        "energetic", "inviting", "confident", "soothing", "clear", 
        "intense", "gentle", "upbeat", "focused", "resonant"
    ]
    
    tts_text = "こんにちは、Hume AIのText-to-Speech機能をテストしています。"

    # 設定: 生成する組み合わせ数を制限（テスト用）
    NN = 3
    MM = 4
    MAX_COMBINATIONS = NN*MM  # この数を変更して生成数を調整
    # 組み合わせを生成
    combinations = generate_combinations(
        emotions_primary[:NN],  # 最初の3つの主要感情
        emotions_secondary[:MM],  # 最初の4つの副次感情
        max_combinations=MAX_COMBINATIONS
    )
    
    print(f"生成する組み合わせ数: {len(combinations)}")
    print("\n組み合わせ一覧:")
    for i, combo in enumerate(combinations, 1):
        print(f"{i:2d}: {combo}")
    
    # ユーザー確認
    proceed = input(f"\n{len(combinations)}個の音声ファイルを生成しますか？ (y/n): ")    
    if proceed.lower() in ['y', 'yes', 'はい']:
        print("\n音声生成を開始...")
        
        # 各組み合わせで音声生成
        for i, description in enumerate(combinations):
            print(f"\n[{i+1}/{len(combinations)}] 処理中: {description}")
            result = asyncio.run(main(tts_text, description))
            
            if result is None:
                print(f"⚠️  エラーが発生しました: {description}")
            else:
                print(f"✅ 完了: {description}")
        
        print(f"\n🎉 全{len(combinations)}個の音声ファイル生成が完了しました！")
        for command in all_commands:
            print(command)
    else:
        print("処理をキャンセルしました。")
    
    # 手動で特定の組み合わせをテストしたい場合
    # asyncio.run(main(tts_text, "excited and gentle"))