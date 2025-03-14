# Qt Navigation App

## 概要

QtNavigation Appは、PyQt5を使用して開発されたオープンソースのナビゲーションアプリケーションです。このアプリケーションは、OpenRouteServiceのAPIを活用して、選択した出発地点から目的地までの最適なルートを計算・表示し、ターンバイターン方式で音声ガイダンスを提供します。

アプリケーションはデスクトップ環境で動作し、カリフォルニア（アメリカ）と日本のプリセットされた場所の間のルート案内をサポートします。また、言語設定を英語と日本語の間で切り替えることが可能です。

![アプリケーションのスクリーンショット（イメージ）]()

## 特徴

- OpenStreetMapを使用した地図表示
- OpenRouteService APIを利用したルート計算
- ターンバイターン音声ガイダンス
- 英語・日本語のマルチ言語対応
- プリセットされた人気のルート選択
- カスタム目的地の設定（地図上の長押し操作）
- リアルタイムの距離表示
- ルート上の分岐点の視覚表示

## システム構成図

```mermaid
graph TD
    User[ユーザー] --> |操作| UI[QML UI]
    UI <--> |データ連携| Controller[NavigationController]
    Controller --> |API呼び出し| ORS[OpenRouteService API]
    ORS --> |ルート情報| Controller
    Controller --> |音声案内| TTS[Text-to-Speech エンジン]
    UI --> |表示| Map[OpenStreetMap]
    Controller --> |更新通知| UI
    
    subgraph QML UI Components
        MapView[地図表示]
        RouteView[ルート表示]
        Controls[コントロールボタン]
        LanguageSelector[言語選択]
        LocationPresets[プリセット位置]
    end
    
    UI --- QML UI Components
```

## アプリケーション構造

```mermaid
classDiagram
    class QObject {
        <<Parent Class>>
    }
    
    class NavigationController {
        -route_coordinates: list
        -route_instructions: list
        -language: str
        -simulation_active: bool
        -speech_engine: TTS engine
        +calculateRoute()
        +startSimulation()
        +stopSimulation()
        +setLanguage()
        +moveToNextPosition()
        +checkNextInstruction()
        +speakInstruction()
    }
    
    class QML_UI {
        -startCoordinate: QGeoCoordinate
        -destinationCoordinate: QGeoCoordinate
        -currentLanguage: str
        -navigationActive: bool
        +changeLanguage()
        +updateDistanceDisplay()
        +updateModel()
    }
    
    QObject <|-- NavigationController
    NavigationController --> QML_UI: Signals
    QML_UI --> NavigationController: Slots
```

## アプリケーションフロー

```mermaid
flowchart TD
    subgraph Initialization
        A[アプリケーション起動] --> B[NavigationControllerの初期化]
        B --> C[QMLエンジン起動]
        C --> D[デフォルトルート計算]
    end
    
    subgraph RouteCalculation
        E[ルート選択/計算] --> F{API呼び出し成功?}
        F -->|Yes| G[ルートデータ処理]
        F -->|No| H[フォールバックルート生成]
        G --> I[ルート表示]
        H --> I
    end
    
    subgraph Navigation
        J[ナビゲーション開始] --> K[出発アナウンス]
        K --> L[位置更新ループ]
        L --> M{目的地到着?}
        M -->|No| N[次の指示確認]
        N --> O[残り距離計算]
        O --> L
        M -->|Yes| P[到着アナウンス]
        P --> Q[ナビゲーション停止]
    end
    
    subgraph LanguageChange
        R[言語選択] --> S[UI言語変更]
        S --> T[音声言語変更]
        T --> U[再計算が必要ならルート更新]
    end
    
    D --> E
    I --> J
    Q --> E
    U --> E
```

## シーケンス図

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UI as QML UI
    participant NC as NavigationController
    participant ORS as OpenRouteService API
    participant TTS as 音声エンジン
    
    User->>UI: アプリケーション起動
    UI->>NC: 初期化
    NC->>NC: 音声エンジン初期化
    UI->>NC: calculateRoute(DEFAULT_START, DEFAULT_END)
    NC->>ORS: ルート計算リクエスト
    ORS-->>NC: ルートデータ
    NC-->>UI: routeFound シグナル
    UI->>UI: ルート表示
    
    User->>UI: ルートプリセット選択
    UI->>UI: QGeoCoordinate生成
    UI->>NC: calculateRoute(new_start, new_end)
    NC->>ORS: ルート計算リクエスト
    ORS-->>NC: ルートデータ
    NC-->>UI: routeFound シグナル
    UI->>UI: ルート表示更新
    
    User->>UI: デモ開始ボタン押下
    UI->>NC: startSimulation()
    NC->>TTS: 出発案内読み上げ
    NC->>NC: タイマー開始
```

## アーキテクチャ構成

```mermaid
graph TB
    subgraph UI Layer
        QML["QML UI (navigation.qml)"]
        Map["OpenStreetMap"]
        UI_Controls["UI Controls"]
    end
    
    subgraph Controller Layer
        NC["NavigationController"]
        SignalHandler["Signal Handling"]
        EventProcessing["Event Processing"]
    end
    
    subgraph Service Layer
        RouteSvc["Route Services"]
        TTS["Text-to-Speech"]
        Lang["Localization"]
    end
    
    subgraph External Services
        ORS["OpenRouteService API"]
        OSM["OpenStreetMap Tiles"]
    end
    
    QML --> Map
    QML --> UI_Controls
    QML <--> NC
    
    NC --> SignalHandler
    NC --> EventProcessing
    
    NC --> RouteSvc
    NC --> TTS
    NC --> Lang
    
    RouteSvc --> ORS
    Map --> OSM
    
    classDef ui fill:#d4f0f0,stroke:#333,stroke-width:1px;
    classDef controller fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef service fill:#eeeeee,stroke:#333,stroke-width:1px;
    classDef external fill:#e7f9d5,stroke:#333,stroke-width:1px;
    
    class QML,Map,UI_Controls ui;
    class NC,SignalHandler,EventProcessing controller;
    class RouteSvc,TTS,Lang service;
    class ORS,OSM external;
```

## 主要コンポーネント

### NavigationController (Python)

NavigationControllerは、アプリケーションのバックエンドロジックを担当するPythonクラスです。このコントローラは以下の主要な機能を提供します：

- OpenRouteService APIを使用したルート計算
- ナビゲーションシミュレーションの管理
- 現在位置の更新と進捗追跡
- 次の指示のタイミング計算
- 音声ガイダンスの提供
- 多言語サポート

### QML UI

QMLで記述されたユーザーインターフェースは、以下のコンポーネントで構成されています：

- 地図表示（OpenStreetMap）
- 現在位置とルートの視覚表示
- ルート選択ドロップダウン
- ナビゲーションコントロール（開始・停止・リセット）
- 言語選択
- 指示表示と距離表示

## 機能一覧

### コア機能

| 機能 | 説明 | 主要実装クラス/メソッド | 
|------|------|------------------------|
| ルート計算 | OpenRouteService APIを使用して経路を計算 | `NavigationController.calculateRoute()` |
| 経路案内 | ターンバイターン方式のナビゲーション | `NavigationController.moveToNextPosition(), checkNextInstruction()` |
| 音声ガイダンス | 指示と方向を音声で案内 | `NavigationController.speakInstruction()` |
| マルチ言語対応 | 英語・日本語UIと音声案内 | `NavigationController.setLanguage()`, `QML getText()` |
| 地図表示 | OpenStreetMapを利用した地図表示 | `QML Map` コンポーネント |
| ルートシミュレーション | デモモードでルート上を移動 | `NavigationController.startSimulation()` |

### ユーザーインターフェース機能

| 機能 | 説明 | 主要実装 |
|------|------|---------|
| ルート選択 | プリセットされたルートから選択 | `QML ComboBox` と `updateModel()` |
| 言語切替 | 英語と日本語の切替 | `changeLanguage()` と `languageSelector` |
| 音声切替 | 言語に応じた音声選択 | `setLanguage()` 内の音声選択ロジック |
| 指示表示 | 次の指示をヘッダに表示 | `onNextInstruction()` と `instructionLabel` |
| 距離表示 | 残り距離をリアルタイム表示 | `onRemainingDistance()`, `updateDistanceDisplay()` |
| マーカー表示 | 現在位置とルートのマーカー表示 | `MapQuickItem` と `MapPolyline` |
| デモコントロール | シミュレーション開始/停止 | `startDemo`, `stopDemo` ボタン |
| 地図操作 | 拡大/縮小、移動、目的地変更 | `Map` と `MouseArea` |

## インストールと実行

### 必要条件

- Python 3.7以上
- PyQt5
- pyttsx3（音声合成）
- requests（API通信用）

### インストール

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

### 実行

```bash
python main.py
```

## カスタマイズ

### OpenRouteService APIキー

アプリケーションを利用するには、OpenRouteServiceのAPIキーを取得し、`main.py`ファイル内の`ORS_API_KEY`変数に設定する必要があります：

```python
ORS_API_KEY = "YOUR_OPENROUTESERVICE_API_KEY"
```

### 音声設定

各言語の音声は`setLanguage`メソッド内でカスタマイズできます。例えば英語ではMelina（またはFiona）の音声を優先的に使用しています：

```python
if 'melina' in voice.name.lower():
    print(f"Setting Melina voice: {voice.name} / {voice.id}")
    self.speech_engine.setProperty('voice', voice.id)
```

## ライセンス

このプロジェクトはオープンソースで、[MITライセンス](LICENSE)の下で公開されています。

## 謝辞

- OpenRouteService - ルート計算APIの提供
- OpenStreetMap - 地図データの提供
- PyQt5 - クロスプラットフォームGUIフレームワーク
- pyttsx3 - オープンソース音声合成ライブラリ
