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
    title: "Qt Navigation App"
    
    // Language setting (ja:Japanese, en:English) - default to English
    property string currentLanguage: "en"
    
    // Language-specific texts
    property var texts: {
        "ja": {
            "windowTitle": "Qt ナビゲーションアプリ",
            "nextInstruction": "次の指示:",
            "calculateRoute": "ルート計算",
            "startDemo": "デモ開始",
            "stopDemo": "デモ停止",
            "resetPosition": "位置リセット",
            "showPoints": "ポイント表示",
            "remaining": "残り距離:",
            "language": "言語",
            "start": "出発",
            "destination": "目的地",
            "defaultInstruction": "ルートを計算してください",
            "locationPresetTitle": "ルート選択",
            "japanGroup": "日本",
            "tokyoRoute": "東京駅 → 東京タワー",
            "shibuyaRoute": "渋谷 → 原宿",
            "shinjukuRoute": "新宿 → 池袋",
            "californiaGroup": "カリフォルニア",
            "mvRoute": "マウンテンビュー → パロアルト",
            "mv_sjRoute": "マウンテンビュー → サンノゼ",
            "mv_sfRoute": "マウンテンビュー → サンフランシスコ"
        },
        "en": {
            "windowTitle": "Qt Navigation App",
            "nextInstruction": "Next instruction:",
            "calculateRoute": "Calculate Route",
            "startDemo": "Start Demo",
            "stopDemo": "Stop Demo",
            "resetPosition": "Reset Position",
            "showPoints": "Show Points",
            "remaining": "Distance remaining:",
            "language": "Language",
            "start": "Start",
            "destination": "Destination",
            "defaultInstruction": "Please calculate a route",
            "locationPresetTitle": "Select Route",
            "japanGroup": "Japan",
            "tokyoRoute": "Tokyo Station → Tokyo Tower",
            "shibuyaRoute": "Shibuya → Harajuku",
            "shinjukuRoute": "Shinjuku → Ikebukuro",
            "californiaGroup": "California",
            "mvRoute": "Mountain View → Palo Alto",
            "mv_sjRoute": "Mountain View → San Jose",
            "mv_sfRoute": "Mountain View → San Francisco"
        }
    }

    // Japan coordinates
    property var japanCoordinates: {
        "tokyo_station": QtPositioning.coordinate(35.6812, 139.7671),
        "tokyo_tower": QtPositioning.coordinate(35.6585, 139.7454),
        "shibuya": QtPositioning.coordinate(35.6580, 139.7016),
        "harajuku": QtPositioning.coordinate(35.6702, 139.7027),
        "shinjuku": QtPositioning.coordinate(35.6938, 139.7034),
        "ikebukuro": QtPositioning.coordinate(35.7295, 139.7109)
    }
    
    // California coordinates
    property var californiaCoordinates: {
        "san_francisco": QtPositioning.coordinate(37.7749, -122.4194),
        "pier39": QtPositioning.coordinate(37.8087, -122.4098),
        "mountain_view": QtPositioning.coordinate(37.3861, -122.0839),
        "palo_alto": QtPositioning.coordinate(37.4419, -122.1430),
        "san_jose": QtPositioning.coordinate(37.3382, -121.8863),
        "santa_clara": QtPositioning.coordinate(37.3541, -121.9552)
    }
    
    // Default to Mountain View coordinates
    property var startCoordinate: californiaCoordinates.mountain_view
    property var destinationCoordinate: californiaCoordinates.palo_alto
    property bool navigationActive: false
    
    // Get text for the current language
    function getText(key) {
        return texts[currentLanguage][key];
    }
    
    // Change language function
    function changeLanguage(lang) {
        if (lang === "ja" || lang === "en") {
            currentLanguage = lang;
            navController.setLanguage(lang);
            window.title = getText("windowTitle");
        }
    }
    
    // Set default language to English on initialization
    Component.onCompleted: {
        changeLanguage("en");
        
        // Set initial index for location presets to Mountain View -> Palo Alto
        // Use a slight delay to ensure the model is loaded
        presetInitTimer.start();
    }
    
    // Timer to initialize the preset selection
    Timer {
        id: presetInitTimer
        interval: 100
        repeat: false
        onTriggered: {
            // Find the index for the Mountain View -> Palo Alto option
            for (let i = 0; i < routeModel.count; i++) {
                if (routeModel.get(i).value === "mv") {
                    locationPresets.currentIndex = i;
                    break;
                }
            }
        }
    }
    
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
        
        // Navigation header
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
                        text: getText("nextInstruction")
                        color: "white"
                        font.pixelSize: 14
                    }
                    
                    Label {
                        id: instructionLabel
                        text: getText("defaultInstruction")
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
                        text: getText("remaining")
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
        
        // Map
        Map {
            id: map
            Layout.fillWidth: true
            Layout.fillHeight: true
            plugin: osmPlugin
            center: startCoordinate
            zoomLevel: 13  // Adjusted for Mountain View
            
            // Current position marker
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
            
            // Start point marker
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
                        visible: false // If no image
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
                        text: getText("start")
                        font.pixelSize: 12
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
            
            // Destination marker
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
                        visible: false // If no image
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
                        text: getText("destination")
                        font.pixelSize: 12
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
            
            // Route polyline
            MapPolyline {
                id: routeLine
                line.width: 5
                line.color: "#3498db"
            }
            
            // Route points list model
            ListModel {
                id: routePointsModel
            }
            
            // Route point marker component
            Component {
                id: routePointDelegate
                MapQuickItem {
                    coordinate: QtPositioning.coordinate(latitude, longitude)
                    anchorPoint.x: pointRect.width / 2
                    anchorPoint.y: pointRect.height / 2
                    
                    sourceItem: Column {
                        spacing: 2
                        
                        // Point number and instruction
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
                        
                        // Instruction text (only if present)
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
            
            // Map view for route points markers
            MapItemView {
                id: routePointsView
                model: routePointsModel
                delegate: routePointDelegate
            }
            
            // Long press to change destination
            MouseArea {
                anchors.fill: parent
                onPressAndHold: {
                    var coord = map.toCoordinate(Qt.point(mouseX, mouseY))
                    destinationCoordinate = coord
                    destinationMarker.coordinate = coord
                }
            }
        }
        
        // Control panel
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "#ecf0f1"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                Button {
                    text: getText("calculateRoute")
                    Layout.preferredWidth: 120
                    onClicked: {
                        // Calculate route based on current start and destination
                        navController.calculateRoute(startCoordinate, destinationCoordinate)
                    }
                }
                
                Button {
                    id: demoButton
                    text: getText("startDemo")
                    Layout.preferredWidth: 120
                    enabled: true  // Always enabled, controller handles missing routes
                    onClicked: {
                        if (!navigationActive) {
                            // Try to calculate route if none exists
                            if (routeLine.path.length === 0) {
                                console.log("No route yet, calculating first...")
                                navController.calculateRoute(startCoordinate, destinationCoordinate)
                                // Wait a bit then start simulation
                                demoStartTimer.restart()
                            } else {
                                console.log("Starting demo directly (route exists)")
                                try {
                                    // Try standard method
                                    navController.startSimulation()
                                } catch (e) {
                                    console.log("Failed with standard method, trying alternative: " + e)
                                    // Try fallback method
                                    navController.manualStartDemo()
                                }
                                navigationActive = true
                                text = getText("stopDemo")
                            }
                        } else {
                            navController.stopSimulation()
                            navigationActive = false
                            text = getText("startDemo")
                        }
                    }
                }
                
                Button {
                    text: getText("resetPosition")
                    Layout.preferredWidth: 120
                    onClicked: {
                        if (navigationActive) {
                            navController.stopSimulation()
                            navigationActive = false
                            demoButton.text = getText("startDemo")
                        }
                        currentLocationMarker.coordinate = startCoordinate
                        map.center = startCoordinate
                    }
                }
                
                CheckBox {
                    id: showPointsCheckbox
                    text: getText("showPoints")
                    checked: true
                    onCheckedChanged: {
                        routePointsView.visible = checked
                    }
                }
                
                ComboBox {
                    id: languageSelector
                    Layout.preferredWidth: 100
                    model: ListModel {
                        id: langModel
                        ListElement { text: "English"; value: "en" }
                        ListElement { text: "日本語"; value: "ja" }
                    }
                    textRole: "text"
                    currentIndex: currentLanguage === "en" ? 0 : 1
                    onActivated: {
                        let lang = langModel.get(currentIndex).value;
                        changeLanguage(lang);
                    }
                }
                
                Item {
                    Layout.fillWidth: true
                }
                
                ComboBox {
                    id: locationPresets
                    Layout.preferredWidth: 180
                    textRole: "text"
                    
                    // Model creation function
                    function updateModel() {
                        let presetModel = [
                            // Header: California (moved to top since it's the default region)
                            {text: "--- " + getText("californiaGroup") + " ---", value: "header2", isHeader: true},
                            {text: getText("mvRoute"), value: "mv", 
                                startLat: californiaCoordinates.mountain_view.latitude, 
                                startLng: californiaCoordinates.mountain_view.longitude,
                                endLat: californiaCoordinates.palo_alto.latitude, 
                                endLng: californiaCoordinates.palo_alto.longitude},
                            {text: getText("mv_sjRoute"), value: "mv_sj", 
                                startLat: californiaCoordinates.mountain_view.latitude, 
                                startLng: californiaCoordinates.mountain_view.longitude,
                                endLat: californiaCoordinates.san_jose.latitude, 
                                endLng: californiaCoordinates.san_jose.longitude},
                            {text: getText("mv_sfRoute"), value: "mv_sf", 
                                startLat: californiaCoordinates.mountain_view.latitude, 
                                startLng: californiaCoordinates.mountain_view.longitude,
                                endLat: californiaCoordinates.san_francisco.latitude, 
                                endLng: californiaCoordinates.san_francisco.longitude},
                                
                            // Header: Japan (moved below California)
                            {text: "--- " + getText("japanGroup") + " ---", value: "header1", isHeader: true},
                            {text: getText("tokyoRoute"), value: "tokyo", 
                                startLat: japanCoordinates.tokyo_station.latitude, 
                                startLng: japanCoordinates.tokyo_station.longitude,
                                endLat: japanCoordinates.tokyo_tower.latitude, 
                                endLng: japanCoordinates.tokyo_tower.longitude},
                            {text: getText("shibuyaRoute"), value: "shibuya", 
                                startLat: japanCoordinates.shibuya.latitude, 
                                startLng: japanCoordinates.shibuya.longitude,
                                endLat: japanCoordinates.harajuku.latitude, 
                                endLng: japanCoordinates.harajuku.longitude},
                            {text: getText("shinjukuRoute"), value: "shinjuku", 
                                startLat: japanCoordinates.shinjuku.latitude, 
                                startLng: japanCoordinates.shinjuku.longitude,
                                endLat: japanCoordinates.ikebukuro.latitude, 
                                endLng: japanCoordinates.ikebukuro.longitude}
                        ];
                        
                        // Clear and rebuild the model
                        routeModel.clear();
                        for (let i = 0; i < presetModel.length; i++) {
                            routeModel.append(presetModel[i]);
                        }
                    }
                    
                    // Use a ListModel for the routes
                    model: ListModel {
                        id: routeModel
                    }
                    
                    // Initialize the model
                    Component.onCompleted: {
                        locationPresets.updateModel();
                    }
                    
                    // Update on language change
                    Connections {
                        target: window
                        function onCurrentLanguageChanged() {
                            locationPresets.updateModel();
                        }
                    }
                    
                    // Handle route selection
                    onActivated: {
                        let item = routeModel.get(currentIndex);
                        if (!item.isHeader) {
                            // Create proper QGeoCoordinate objects from lat/lng values
                            let start = QtPositioning.coordinate(item.startLat, item.startLng);
                            let end = QtPositioning.coordinate(item.endLat, item.endLng);
                            
                            // Store current selection values
                            startCoordinate = start;
                            destinationCoordinate = end;
                            
                            // Update markers
                            startMarker.coordinate = startCoordinate;
                            destinationMarker.coordinate = destinationCoordinate;
                            currentLocationMarker.coordinate = startCoordinate;
                            
                            // Adjust zoom level and center map
                            if (item.value.startsWith("sf") || item.value.startsWith("mv") || item.value.startsWith("sj")) {
                                map.zoomLevel = 13;  // Wider view for California
                            } else {
                                map.zoomLevel = 14;  // Closer zoom for Japanese urban areas
                            }
                            map.center = startCoordinate;
                            
                            // Recalculate the route with new coordinates
                            navController.calculateRoute(startCoordinate, destinationCoordinate);
                            
                            // If navigation is active, stop it since we're changing route
                            if (navigationActive) {
                                navController.stopSimulation();
                                navigationActive = false;
                                demoButton.text = getText("startDemo");
                            }
                        }
                    }
                    
                    // Header items are not selectable
                    delegate: ItemDelegate {
                        id: routeDelegate
                        text: model.text
                        font.bold: model.isHeader
                        enabled: !model.isHeader  // Headers should be disabled but visible
                        width: locationPresets.width
                        height: 30
                        
                        background: Rectangle {
                            color: model.isHeader ? "#e0e0e0" : (routeDelegate.highlighted ? "#d0d0ff" : "white")
                        }
                    }
                }
            }
        }
    }
    
    // Distance display update function
    function updateDistanceDisplay(distance) {
        // Process the number properly
        var dist = Number(distance);
        
        if (dist > 1000) {
            distanceLabel.text = (dist / 1000).toFixed(1) + " km";
        } else {
            distanceLabel.text = Math.round(dist) + " m";
        }
        
        // Visual feedback for value change
        distanceLabel.color = "#ffcc00";  // Temporarily change color
        distanceResetTimer.restart();
    }
    
    // Distance label reset timer
    Timer {
        id: distanceResetTimer
        interval: 300  // Return to original color after 300ms
        repeat: false
        onTriggered: {
            distanceLabel.color = "white"  // Return to original color
        }
    }
    
    // Timer to start demo after route calculation
    Timer {
        id: demoStartTimer
        interval: 1000  // Start after 1 second
        repeat: false
        onTriggered: {
            console.log("Demo start timer finished: route points=" + routeLine.path.length)
            if (routeLine.path.length > 0) {
                try {
                    // Try standard method
                    navController.startSimulation()
                } catch (e) {
                    console.log("Failed to start with timer, trying alternative: " + e)
                    // Try fallback method
                    navController.manualStartDemo()
                }
                navigationActive = true
                demoButton.text = getText("stopDemo")
            } else {
                // Try again with fallback route if no route was calculated
                console.log("No route found. Using fallback route")
                navController.calculateRoute(startCoordinate, destinationCoordinate)
                // Wait a bit longer and retry
                demoRetryTimer.restart()
            }
        }
    }
    
    // Retry timer for route calculation failures
    Timer {
        id: demoRetryTimer
        interval: 1500  // Try again after 1.5 seconds
        repeat: false
        onTriggered: {
            // Force start with fallback route
            console.log("Force starting demo: route points=" + routeLine.path.length)
            try {
                // Try standard method
                navController.startSimulation()
            } catch (e) {
                console.log("Failed to force start, trying alternative: " + e)
                // Try fallback method
                navController.manualStartDemo()
            }
            navigationActive = true
            demoButton.text = getText("stopDemo")
        }
    }
    
    // Connections to the controller
    Connections {
        target: navController
        
        function onRouteFound(coordinates, instructions) {
            var path = []
            for (var i = 0; i < coordinates.length; i++) {
                path.push(coordinates[i])
            }
            routeLine.path = path
            
            // Zoom to fit the route
            map.fitViewportToMapItems()
            
            // Display the first instruction
            if (instructions.length > 0) {
                instructionLabel.text = instructions[0].text
            }
            
            // Route point markers will be added when debug info is received
        }
        
        function onRouteDebugInfo(debugInfo) {
            console.log("Received route debug info: " + debugInfo.length + " points");
            
            // Clear existing markers
            routePointsModel.clear();
            
            // Add new debug points
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
            
            console.log("Added " + routePointsModel.count + " points to marker model");
        }
        
        function onPositionUpdated(coordinate) {
            currentLocationMarker.coordinate = coordinate
            map.center = coordinate
        }
        
        function onNextInstruction(instruction) {
            instructionLabel.text = instruction
        }
        
        function onRemainingDistance(distance) {
            console.log("Received distance: " + distance + "m");
            updateDistanceDisplay(distance);
        }
        
        function onUpdateDistance(meters) {
            console.log("Received alternative distance: " + meters + "m");
            updateDistanceDisplay(meters);
        }
        
        function onLanguageChanged(language) {
            // Update UI when language changes
            currentLanguage = language;
            window.title = getText("windowTitle");
            
            // Update other UI text
            demoButton.text = navigationActive ? getText("stopDemo") : getText("startDemo");
            
            // Update route dropdown
            locationPresets.updateModel();
        }
    }
}