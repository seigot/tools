import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtPositioning 5.12
import QtLocation 5.12

ApplicationWindow {
    id: window
    visible: true
    width: 800
    height: 600
    title: "Qt ナビゲーションアプリ"
    
    property var startCoordinate: QtPositioning.coordinate(35.6812, 139.7671) // 東京駅
    property var destinationCoordinate: QtPositioning.coordinate(35.6585, 139.7454) // 東京タワー
    property bool navigationActive: false
    
    Plugin {
        id: osmPlugin
        name: "osm"
        
        PluginParameter {
            name: "osm.mapping.highdpi_tiles"
            value: true
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // ナビゲーションヘッダー
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: "#2c3e50"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    
                    Label {
                        text: "次の指示:"
                        color: "white"
                        font.pixelSize: 14
                    }
                    
                    Label {
                        id: instructionLabel
                        text: "ルートを計算してください"
                        color: "white"
                        font.pixelSize: 18
                        font.bold: true
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
                
                ColumnLayout {
                    spacing: 5
                    
                    Label {
                        text: "残り距離:"
                        color: "white"
                        font.pixelSize: 14
                    }
                    
                    Label {
                        id: distanceLabel
                        text: "0 km"
                        color: "white"
                        font.pixelSize: 18
                        font.bold: true
                    }
                }
            }
        }
        
        // マップ
        Map {
            id: map
            Layout.fillWidth: true
            Layout.fillHeight: true
            plugin: osmPlugin
            center: startCoordinate
            zoomLevel: 14
            
            // 現在位置を示すマーカー
            MapQuickItem {
                id: currentLocationMarker
                coordinate: startCoordinate
                anchorPoint.x: currentLocationIcon.width / 2
                anchorPoint.y: currentLocationIcon.height / 2
                sourceItem: Rectangle {
                    id: currentLocationIcon
                    width: 24
                    height: 24
                    radius: 12
                    color: "#3498db"
                    border.width: 2
                    border.color: "white"
                }
            }
            
            // 出発点のマーカー
            MapQuickItem {
                id: startMarker
                coordinate: startCoordinate
                anchorPoint.x: startIcon.width / 2
                anchorPoint.y: startIcon.height
                sourceItem: Column {
                    Image {
                        id: startIcon
                        source: "qrc:///marker-green.png"
                        width: 32
                        height: 32
                        visible: false // 画像がない場合
                    }
                    Rectangle {
                        width: 20
                        height: 20
                        radius: 10
                        color: "green"
                        border.width: 2
                        border.color: "white"
                        visible: !startIcon.visible
                    }
                    Text {
                        text: "出発"
                        font.pixelSize: 12
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
            
            // 目的地のマーカー
            MapQuickItem {
                id: destinationMarker
                coordinate: destinationCoordinate
                anchorPoint.x: destIcon.width / 2
                anchorPoint.y: destIcon.height
                sourceItem: Column {
                    Image {
                        id: destIcon
                        source: "qrc:///marker-red.png"
                        width: 32
                        height: 32
                        visible: false // 画像がない場合
                    }
                    Rectangle {
                        width: 20
                        height: 20
                        radius: 10
                        color: "red"
                        border.width: 2
                        border.color: "white"
                        visible: !destIcon.visible
                    }
                    Text {
                        text: "目的地"
                        font.pixelSize: 12
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
            
            // ルートを表示するポリライン
            MapPolyline {
                id: routeLine
                line.width: 5
                line.color: "#3498db"
            }
            
            // ルートポイントをマーカーとして表示（デバッグ用）
            ListModel {
                id: routePointsModel
            }
            
            // ルートポイントマーカーのコンポーネント
            Component {
                id: routePointDelegate
                MapQuickItem {
                    coordinate: QtPositioning.coordinate(latitude, longitude)
                    anchorPoint.x: pointRect.width / 2
                    anchorPoint.y: pointRect.height / 2
                    
                    sourceItem: Column {
                        spacing: 2
                        
                        // ポイント番号と指示
                        Rectangle {
                            id: pointRect
                            width: pointNumberText.width > 20 ? pointNumberText.width + 10 : 30
                            height: 20
                            radius: 10
                            color: hasInstruction ? "#ff6600" : "#3498db"
                            border.width: 1
                            border.color: "white"
                            
                            Text {
                                id: pointNumberText
                                anchors.centerIn: parent
                                text: pointIndex
                                color: "white"
                                font.pixelSize: 10
                                font.bold: true
                            }
                        }
                        
                        // 指示テキスト（ある場合のみ表示）
                        Rectangle {
                            id: instructionRect
                            visible: instruction !== ""
                            width: instructionText.width + 10
                            height: instructionText.height + 6
                            radius: 5
                            color: "white"
                            border.width: 1
                            border.color: "#ff6600"
                            
                            Text {
                                id: instructionText
                                anchors.centerIn: parent
                                text: instruction
                                color: "#333333"
                                font.pixelSize: 10
                                width: 120
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
            
            // 地図に表示されるルートポイントのマーカー群
            MapItemView {
                id: routePointsView
                model: routePointsModel
                delegate: routePointDelegate
            }
            
            // 地図を長押しで目的地を変更
            MouseArea {
                anchors.fill: parent
                onPressAndHold: {
                    var coord = map.toCoordinate(Qt.point(mouseX, mouseY))
                    destinationCoordinate = coord
                    destinationMarker.coordinate = coord
                }
            }
        }
        
        // コントロールパネル
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "#ecf0f1"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                Button {
                    text: "ルート計算"
                    Layout.preferredWidth: 120
                    onClicked: {
                        navController.calculateRoute(startCoordinate, destinationCoordinate)
                    }
                }
                
                Button {
                    id: demoButton
                    text: "デモ開始"
                    Layout.preferredWidth: 120
                    enabled: true  // 常に有効にして、ルートがない場合はコントローラー側で対応
                    onClicked: {
                        if (!navigationActive) {
                            // ルートがない場合は計算を試みる
                            if (routeLine.path.length === 0) {
                                console.log("ルートがないのでまず計算します")
                                navController.calculateRoute(startCoordinate, destinationCoordinate)
                                // 少し待ってからシミュレーション開始
                                demoStartTimer.restart()
                            } else {
                                console.log("直接デモを開始します（ルートあり）")
                                try {
                                    // 標準方法を試す
                                    navController.startSimulation()
                                } catch (e) {
                                    console.log("標準方法で失敗、代替方法を試みます: " + e)
                                    // 失敗したら代替方法を試す
                                    navController.manualStartDemo()
                                }
                                navigationActive = true
                                text = "デモ停止"
                            }
                        } else {
                            navController.stopSimulation()
                            navigationActive = false
                            text = "デモ開始"
                        }
                    }
                }
                
                Button {
                    text: "位置リセット"
                    Layout.preferredWidth: 120
                    onClicked: {
                        if (navigationActive) {
                            navController.stopSimulation()
                            navigationActive = false
                        }
                        currentLocationMarker.coordinate = startCoordinate
                        map.center = startCoordinate
                    }
                }
                
                CheckBox {
                    id: showPointsCheckbox
                    text: "ポイント表示"
                    checked: true
                    onCheckedChanged: {
                        routePointsView.visible = checked
                    }
                }
                
                Item {
                    Layout.fillWidth: true
                }
                
                ComboBox {
                    id: locationPresets
                    Layout.preferredWidth: 150
                    model: ["東京駅 → 東京タワー", "渋谷 → 原宿", "新宿 → 池袋"]
                    onCurrentIndexChanged: {
                        if (currentIndex === 0) {
                            startCoordinate = QtPositioning.coordinate(35.6812, 139.7671)
                            destinationCoordinate = QtPositioning.coordinate(35.6585, 139.7454)
                        } else if (currentIndex === 1) {
                            startCoordinate = QtPositioning.coordinate(35.6580, 139.7016)
                            destinationCoordinate = QtPositioning.coordinate(35.6702, 139.7027)
                        } else if (currentIndex === 2) {
                            startCoordinate = QtPositioning.coordinate(35.6938, 139.7034)
                            destinationCoordinate = QtPositioning.coordinate(35.7295, 139.7109)
                        }
                        
                        startMarker.coordinate = startCoordinate
                        destinationMarker.coordinate = destinationCoordinate
                        currentLocationMarker.coordinate = startCoordinate
                        map.center = startCoordinate
                    }
                }
            }
        }
    }
    
    // 距離表示を更新する関数
    function updateDistanceDisplay(distance) {
        // 数値を適切に処理
        var dist = Number(distance);
        
        if (dist > 1000) {
            distanceLabel.text = (dist / 1000).toFixed(1) + " km";
        } else {
            distanceLabel.text = Math.round(dist) + " m";
        }
        
        // 値の変更を視覚的に示すため、簡単なアニメーション効果を追加
        distanceLabel.color = "#ffcc00";  // 一時的に色を変更
        distanceResetTimer.restart();
    }
    
    // 距離表示のリセットタイマー
    Timer {
        id: distanceResetTimer
        interval: 300  // 300ms後に元の色に戻す
        repeat: false
        onTriggered: {
            distanceLabel.color = "white"  // 元の色に戻す
        }
    }
    
    // ルート計算後にデモを開始するためのタイマー
    Timer {
        id: demoStartTimer
        interval: 1000  // 1秒後に開始
        repeat: false
        onTriggered: {
            console.log("デモ開始タイマー終了: ルートポイント数=" + routeLine.path.length)
            if (routeLine.path.length > 0) {
                try {
                    // 標準方法を試す
                    navController.startSimulation()
                } catch (e) {
                    console.log("タイマーでの開始に失敗、代替方法を試みます: " + e)
                    // 失敗したら代替方法を試す
                    navController.manualStartDemo()
                }
                navigationActive = true
                demoButton.text = "デモ停止"
            } else {
                // ルートが計算されなかった場合は再試行する
                console.log("ルートがありません。フォールバックルートを使用")
                navController.calculateRoute(startCoordinate, destinationCoordinate)
                // さらに少し待ってから再試行
                demoRetryTimer.restart()
            }
        }
    }
    
    // ルート計算失敗時の再試行タイマー
    Timer {
        id: demoRetryTimer
        interval: 1500  // 1.5秒後に再試行
        repeat: false
        onTriggered: {
            // 強制的にフォールバックルートで開始
            console.log("デモを強制開始: ルートポイント数=" + routeLine.path.length)
            try {
                // 標準方法を試す
                navController.startSimulation()
            } catch (e) {
                console.log("強制開始に失敗、代替方法を試みます: " + e)
                // 失敗したら代替方法を試す
                navController.manualStartDemo()
            }
            navigationActive = true
            demoButton.text = "デモ停止"
        }
    }
    
    // ルートが見つかった時に呼び出される
    Connections {
        target: navController
        
        function onRouteFound(coordinates, instructions) {
            var path = []
            for (var i = 0; i < coordinates.length; i++) {
                path.push(coordinates[i])
            }
            routeLine.path = path
            
            // 地図を適切にズームして表示
            map.fitViewportToMapItems()
            
            // 最初の指示を表示
            if (instructions.length > 0) {
                instructionLabel.text = instructions[0].text
            }
            
            // ルートポイントのマーカーモデルはデバッグ情報が届いたら表示
        }
        
        function onRouteDebugInfo(debugInfo) {
            console.log("ルートデバッグ情報を受信: " + debugInfo.length + "ポイント");
            
            // 既存のマーカーをクリア
            routePointsModel.clear();
            
            // 新しいデバッグポイントを追加
            for (var i = 0; i < debugInfo.length; i++) {
                var point = debugInfo[i];
                routePointsModel.append({
                    "latitude": point.coord.latitude,
                    "longitude": point.coord.longitude,
                    "pointIndex": point.index,
                    "instruction": point.instruction,
                    "hasInstruction": point.instruction !== ""
                });
            }
            
            console.log("マーカーモデルに " + routePointsModel.count + " 個のポイントを追加しました");
        }
        
        function onPositionUpdated(coordinate) {
            currentLocationMarker.coordinate = coordinate
            map.center = coordinate
        }
        
        function onNextInstruction(instruction) {
            instructionLabel.text = instruction
        }
        
        function onRemainingDistance(distance) {
            console.log("残り距離を受信: " + distance + "m");
            updateDistanceDisplay(distance);
        }
        
        function onUpdateDistance(meters) {
            console.log("代替距離を受信: " + meters + "m");
            updateDistanceDisplay(meters);
        }
    }
}