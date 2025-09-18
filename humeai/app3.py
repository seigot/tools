import asyncio
import os
import base64
import tempfile
from hume import AsyncHumeClient
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# ヘルパー関数：音声データを一時ファイルに書き込み
def write_audio_to_temp_file(audio_data: bytes, suffix: str = ".wav") -> str:
    """音声データを一時ファイルに書き込み、ファイルパスを返す"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(audio_data)
        return tmp_file.name

async def main():
    # Hume APIクライアントを初期化
    client = AsyncHumeClient(api_key=os.getenv("HUME_API_KEY"))
    
    try:
        # テキストを音声に変換
        response = await client.tts.synthesize_json(
            utterances=[
                {
                    "text": "こんにちは、Hume AIのText-to-Speech機能をテストしています。",
                    # description: 音声の特徴を指定（オプション）
                    "description": "friendly and clear"
                }
            ]
        )
        
        # 生成された音声データを取得
        audio_base64 = response.generations[0].audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # 一時ファイルに保存
        temp_file_path = write_audio_to_temp_file(audio_bytes)
        
        print(f"音声ファイルが生成されました: {temp_file_path}")
        print(f"Generation ID: {response.generations[0].generation_id}")
        
        # macOSの場合は以下のコマンドで再生可能
        print(f"再生するには以下を実行: afplay {temp_file_path}")
        
        return temp_file_path
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# 非同期関数を実行
if __name__ == "__main__":
    asyncio.run(main())