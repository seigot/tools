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

# OpenRouteService API key (replace with your own API key when using)
#ORS_API_KEY = "YOUR_OPENROUTESERVICE_API_KEY"
ORS_API_KEY = "5b3ce3597851110001cf6248598d70c197ae48ec92978dc2e778aab2"

# Set default coordinates to Mountain View area
DEFAULT_START_COORDINATE = QGeoCoordinate(37.3861, -122.0839)  # Mountain View
DEFAULT_END_COORDINATE = QGeoCoordinate(37.4419, -122.1430)    # Palo Alto

class NavigationController(QObject):
    # Signal definitions
    routeFound = pyqtSignal(list, list, arguments=['coordinates', 'instructions'])
    positionUpdated = pyqtSignal(QGeoCoordinate, arguments=['coordinate'])
    nextInstruction = pyqtSignal(str, arguments=['instruction'])
    remainingDistance = pyqtSignal(float, arguments=['distance'])
    
    # Special signal for distance updates (with explicit type information)
    updateDistance = pyqtSignal(float, arguments=['meters'])
    
    # Signal for route debug information
    routeDebugInfo = pyqtSignal(list, arguments=['debug_info'])
    
    # Language change notification
    languageChanged = pyqtSignal(str, arguments=['language'])
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize basic variables
        self.route_coordinates = []
        self.route_instructions = []
        self.current_route_index = 0
        self.current_instruction_index = 0
        self.update_count = 0
        self.simulation_active = False
        
        # Language setting (default to English)
        self.language = "en"
        
        # Language-specific messages
        self.messages = {
            "ja": {
                "start_guidance": "案内を開始します。ルートに従って走行してください。",
                "arrival": "目的地に到着しました",
                "straight": "そのまま直進",
                "right": "右",
                "left": "左",
                "u_turn": "Uターン",
                "forward": "前方へ進みます",
                "arrive": "目的地に到着します",
                "km_ahead": "{0}キロメートル先、{1}",
                "m_ahead": "{0}メートル先、{1}"
            },
            "en": {
                "start_guidance": "Starting navigation. Please follow the route.",
                "arrival": "You have arrived at your destination.",
                "straight": "continue straight ahead",
                "right": "turn right",
                "left": "turn left",
                "u_turn": "make a U-turn",
                "forward": "proceed forward",
                "arrive": "arrive at your destination",
                "km_ahead": "In {0} kilometers, {1}",
                "m_ahead": "In {0} meters, {1}"
            }
        }
        
        # Initialize timer
        self.simulation_speed = 100  # meters/second
        self.simulation_interval = 200  # milliseconds
        self.single_timer = QTimer(self)  # Create timer object
        self.single_timer.setSingleShot(True)  # Single-shot mode
        self.single_timer.timeout.connect(self.moveToNextPosition)  # Function to execute on timeout
        
        # Initialize text-to-speech engine
        self.speech_engine = pyttsx3.init()
        try:
            voices = self.speech_engine.getProperty('voices')
            # Default to English voice
            english_voice_found = False
            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                    self.speech_engine.setProperty('voice', voice.id)
                    english_voice_found = True
                    break
            # If no English voice was found, try any available voice
            if not english_voice_found and voices:
                self.speech_engine.setProperty('voice', voices[0].id)
        except:
            pass  # Continue even if voice setting fails
        self.speech_engine.setProperty('rate', 150)
        
        # Debug
        print("NavigationController initialized")
    
    # Change language setting
    @pyqtSlot(str)
    def setLanguage(self, language):
        """Change the language setting"""
        if language in ["ja", "en"]:
            self.language = language
            print(f"Changed language to {language}")
            
            # Also change text-to-speech language
            try:
                voices = self.speech_engine.getProperty('voices')
                print(f"Available voices: {len(voices)}")
                for i, voice in enumerate(voices):
                    print(f"Voice {i}: {voice.name} / {voice.id}")
                    
                voice_found = False
                # First try to find explicit voice match
                for voice in voices:
                    # For Japanese, look for Japanese voices
                    if language == "ja" and ('japanese' in voice.name.lower() or 'ja' in voice.id.lower()):
                        print(f"Setting Japanese voice: {voice.name} / {voice.id}")
                        self.speech_engine.setProperty('voice', voice.id)
                        voice_found = True
                        break
                    # For English, look for Melina voice first, then other English voices
                    elif language == "en":
                        melina_voice_found = False
                        # First try to find Melina voice specifically
                        for voice in voices:
                            if 'fiona' in voice.name.lower():
                                print(f"Setting Melina voice: {voice.name} / {voice.id}")
                                self.speech_engine.setProperty('voice', voice.id)
                                voice_found = True
                                melina_voice_found = True
                                break
                        
                        # If Melina voice not found, try any English voice
                        if not melina_voice_found:
                            for voice in voices:
                                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                                    print(f"Setting English voice: {voice.name} / {voice.id}")
                                    self.speech_engine.setProperty('voice', voice.id)
                                    voice_found = True
                                    break
                
                # If no specific language voice was found, try to find any voice that might work
                if not voice_found:
                    # For Japanese, try MS Voices that might support Japanese
                    if language == "ja":
                        for voice in voices:
                            if "microsoft" in voice.name.lower() and ("haruka" in voice.name.lower() or 
                                                                     "sayaka" in voice.name.lower() or 
                                                                     "japan" in voice.name.lower()):
                                print(f"Setting Japanese MS voice: {voice.name} / {voice.id}")
                                self.speech_engine.setProperty('voice', voice.id)
                                voice_found = True
                                break
                            
                    # If still no voice found and we have any voices, use the first one
                    if not voice_found and voices:
                        print(f"No language-specific voice found, using default: {voices[18].name}")
                        self.speech_engine.setProperty('voice', voices[18].id)
                
            except Exception as e:
                print(f"Error setting voice: {e}")
            
            self.languageChanged.emit(language)
            return True
        return False
    
    # Get message
    def getMessage(self, key, *args):
        """Get message for the current language"""
        if key in self.messages[self.language]:
            msg = self.messages[self.language][key]
            if args:
                return msg.format(*args)
            return msg
        return key  # Return the key if not found
    
    # Timer reset function
    def reInitializeTimer(self):
        """Reinitialize timer (for problem resolution)"""
        if hasattr(self, 'single_timer') and self.single_timer is not None:
            if self.single_timer.isActive():
                self.single_timer.stop()
        
        # Create a new timer
        self.single_timer = QTimer(self)
        self.single_timer.setSingleShot(True)
        self.single_timer.timeout.connect(self.moveToNextPosition)
        print("Timer reinitialized")
    
    @pyqtSlot(QGeoCoordinate, QGeoCoordinate)
    def calculateRoute(self, start, end):
        """Calculate a route from start to destination using OpenRouteService API"""
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
                "language": self.language,  # Use current language setting
                # Parameters to ensure route follows roads
                "preference": "recommended",  # Recommended route
                "units": "m",  # Meters
                "geometry": "true",  # Include road shape
                "continue_straight": "true"  # Prefer continuing straight when possible
            }
            
            response = requests.post(url, json=body, headers=headers)
            
            if response.status_code != 200:
                print(f"Route retrieval error: {response.status_code}, {response.text}")
                # Generate fallback route on API error
                # Generate fallback route on API error
                self.createFallbackRoute(start, end)
                return
                
            route_data = response.json()
            
            # Extract coordinate data
            geometry = route_data['routes'][0]['geometry']
            if isinstance(geometry, str):  # Encoded polyline format
                # Need to decode polyline
                coordinates = self.decodePolyline(geometry)
            elif isinstance(geometry, dict) and 'coordinates' in geometry:  # GeoJSON format
                coordinates = geometry['coordinates']
            else:
                print("Unknown geometry format. Using fallback route.")
                self.createFallbackRoute(start, end)
                return
            
            # Convert to QGeoCoordinate list
            coords_list = []
            for lon, lat in coordinates:
                coords_list.append(QGeoCoordinate(lat, lon))
            
            # Extract routing instructions
            steps = route_data['routes'][0]['segments'][0]['steps']
            instructions_list = []
            for step in steps:
                instruction = {
                    'text': step['instruction'],
                    'distance': step['distance'],
                    'index': step['way_points'][0]  # Index of the coordinate this instruction applies to
                }
                instructions_list.append(instruction)
            
            # Save results and emit signals (add debug info)
            self.route_coordinates = coords_list
            self.route_instructions = instructions_list
            
            # Add route waypoint debug info
            debug_info = []
            # Display only important points (downsample if too many)
            sampling_interval = max(1, len(coords_list) // 20)  # Maximum of about 20 points
            for i in range(0, len(coords_list), sampling_interval):
                coord = coords_list[i]
                # Check if this point has an associated instruction
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
            
            # Always include instruction points
            for instr in instructions_list:
                idx = instr['index']
                if idx % sampling_interval != 0:  # If not already added
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
            
            # Sort debug info by index
            debug_info.sort(key=lambda x: x['index'])
            
            # Send route and debug info
            self.routeFound.emit(coords_list, instructions_list)
            self.routeDebugInfo.emit(debug_info)
            
            print(f"Found road-following route: {len(coords_list)} points, {len(instructions_list)} instructions")
            
            # For demo: fallback if API key not set or empty coordinate list
            if len(coords_list) == 0:
                self.createFallbackRoute(start, end)
            
        except Exception as e:
            print(f"Route calculation error: {str(e)}")
            # Generate sample route even if error occurs
            self.createFallbackRoute(start, end)
    
    def decodePolyline(self, encoded):
        """Decode an encoded polyline
        (OpenRouteService polylines use Google format)"""
        try:
            # Polyline decoding implementation
            coords = []
            index = 0
            lat = 0
            lng = 0
            
            while index < len(encoded):
                # Decode latitude
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
                
                # Decode longitude
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
                
                # Add to coordinate list
                coords.append([lng * 1e-5, lat * 1e-5])
            
            return coords
        except Exception as e:
            print(f"Polyline decoding error: {str(e)}")
            return []
    
    def createFallbackRoute(self, start, end):
        """Generate a road-like fallback route when API is unavailable"""
        print("Generating road-like fallback route")
        # Add intermediate points to make it look like a road, not just a straight line
        coords_list = []
        
        # Starting point
        coords_list.append(start)
        
        # Add intermediate points that make it look like a winding road
        s_lat = start.latitude()
        s_lon = start.longitude()
        e_lat = end.latitude()
        e_lon = end.longitude()
        
        # Number of intermediate points
        midpoints = 4
        
        for i in range(1, midpoints + 1):
            # Basic linear interpolation
            frac = i / (midpoints + 1)
            mid_lat = s_lat + (e_lat - s_lat) * frac
            mid_lon = s_lon + (e_lon - s_lon) * frac
            
            # Add randomness to simulate road curves
            # Using Python's built-in math module
            variation = 0.0005 * math.sin(i * math.pi)  # Small variation
            
            if i % 2 == 0:  # Even numbers: vary latitude
                mid_lat += variation
            else:  # Odd numbers: vary longitude
                mid_lon += variation
            
            coords_list.append(QGeoCoordinate(mid_lat, mid_lon))
        
        # Destination
        coords_list.append(end)
        
        # Create fallback instructions (using current language)
        instructions_list = [
            {
                'text': self.getMessage('forward'),
                'distance': 0,
                'index': 0
            }
        ]
        
        # Add intermediate instructions
        total_distance = 0
        for i in range(len(coords_list) - 1):
            distance = coords_list[i].distanceTo(coords_list[i + 1])
            total_distance += distance
            
            if i + 1 < len(coords_list) - 1:  # Before the last instruction
                direction = self.getDirection(coords_list[i], coords_list[i + 1], coords_list[i + 2])
                instructions_list.append({
                    'text': direction,
                    'distance': distance,
                    'index': i + 1
                })
        
        # Final instruction
        instructions_list.append({
            'text': self.getMessage('arrive'),
            'distance': 0,
            'index': len(coords_list) - 1
        })
        
        # Set results
        self.route_coordinates = coords_list
        self.route_instructions = instructions_list
        self.routeFound.emit(coords_list, instructions_list)
        
        # Also send debug info
        debug_info = []
        for i, coord in enumerate(coords_list):
            # Check if this point has instructions
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
        """Calculate direction from 3 points"""
        # Determine direction based on angle change from p1->p2 to p2->p3
        bearing1 = self.calculateBearing(p1, p2)
        bearing2 = self.calculateBearing(p2, p3)
        
        # Calculate angle difference (-180 to 180 degrees range)
        angle_diff = ((bearing2 - bearing1 + 180) % 360) - 180
        
        if -30 <= angle_diff <= 30:
            return self.getMessage('straight')
        elif 30 < angle_diff <= 120:
            return self.getMessage('right')
        elif -120 <= angle_diff < -30:
            return self.getMessage('left')
        else:
            return self.getMessage('u_turn')
    
    def calculateBearing(self, start, end):
        """Calculate bearing angle between two points"""
        # Convert latitude and longitude to radians
        lat1 = math.radians(start.latitude())
        lon1 = math.radians(start.longitude())
        lat2 = math.radians(end.latitude())
        lon2 = math.radians(end.longitude())
        
        # Calculate bearing
        y = math.sin(lon2 - lon1) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        bearing = math.atan2(y, x)
        
        # Convert radians to degrees (0-360 degrees)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    @pyqtSlot()
    def startSimulation(self):
        """Start demo navigation"""
        try:
            print("\n===== Starting Demo Navigation =====")
            
            # Check initialization
            self.reInitializeTimer()
            
            if not self.route_coordinates:
                print("No route calculated")
                return
            
            # Check route validity
            if len(self.route_coordinates) < 2:
                print("Error: Insufficient route points")
                return
                
            # Pre-process: remove extremely close points
            cleaned_route = [self.route_coordinates[0]]  # Always include first point
            for i in range(1, len(self.route_coordinates)):
                # Calculate distance from previous point
                prev = cleaned_route[-1]
                curr = self.route_coordinates[i]
                dist = prev.distanceTo(curr)
                
                # Add if distance exceeds threshold or it's the final point
                if dist >= 0.01 or i == len(self.route_coordinates) - 1:
                    cleaned_route.append(curr)
            
            # Show cleaning results
            removed = len(self.route_coordinates) - len(cleaned_route)
            if removed > 0:
                print(f"Pre-processing: Removed {removed} close points ({len(self.route_coordinates)}→{len(cleaned_route)})")
                self.route_coordinates = cleaned_route
            
            # Reset simulation state for reliable operation
            self.current_route_index = 0
            self.current_instruction_index = 0
            self.update_count = 0
            self.simulation_active = True
            
            # Update initial position
            if self.route_coordinates:
                self.positionUpdated.emit(self.route_coordinates[0])
            
            # Departure announcement
            departure_message = self.getMessage('start_guidance')
            self.nextInstruction.emit(departure_message)
            self.speakInstruction(departure_message)
            
            # Also announce first instruction
            if len(self.route_instructions) > 0:
                first_instruction = self.route_instructions[0]['text']
                distance = self.route_instructions[0]['distance']
                
                # Format distance for voice guidance
                if distance > 1000:
                    distance_text = self.getMessage('km_ahead', round(distance / 1000, 1), first_instruction)
                else:
                    distance_text = self.getMessage('m_ahead', round(distance), first_instruction)
                    
                # Delay first instruction to avoid overlap with departure announcement
                QTimer.singleShot(500, lambda: self.speakInstruction(distance_text))
            
            # Calculate and notify total distance
            if len(self.route_coordinates) > 1:
                total_distance = 0
                for i in range(len(self.route_coordinates) - 1):
                    total_distance += self.route_coordinates[i].distanceTo(self.route_coordinates[i + 1])
                
                # Send initial distance reliably (multiple methods)
                print(f"Sending initial total distance: {total_distance:.1f}m")
                self.remainingDistance.emit(float(total_distance))
                self.updateDistance.emit(float(total_distance))
                
                # Send again with delay (UI might not be ready immediately)
                QTimer.singleShot(100, lambda d=total_distance: self.remainingDistance.emit(float(d)))
                QTimer.singleShot(300, lambda d=total_distance: self.updateDistance.emit(float(d)))
                QTimer.singleShot(500, lambda d=total_distance: self.remainingDistance.emit(float(d)))
                print(f"Total distance: {total_distance:.1f}m")
            
            # Start single-shot timer
            print(f"Starting position update timer (interval {self.simulation_interval}ms)")
            self.single_timer.start(100)  # Start a bit faster initially
            
            print(f"Simulation started: Route points = {len(self.route_coordinates)}, Instructions = {len(self.route_instructions)}")
        
        except Exception as e:
            print(f"Error during simulation start: {str(e)}")
            import traceback
            traceback.print_exc()  # Print stack trace
    
    @pyqtSlot()
    def manualStartDemo(self):
        """Alternative demo start method for direct QML calls"""
        print("manualStartDemo called")
        try:
            # Start update directly without timer
            self.current_route_index = 0
            self.current_instruction_index = 0
            self.update_count = 0
            self.simulation_active = True
            
            if self.route_coordinates:
                # Set initial position
                self.positionUpdated.emit(self.route_coordinates[0])
                
                # Calculate and send initial distance
                if len(self.route_coordinates) > 1:
                    total_distance = 0
                    for i in range(len(self.route_coordinates) - 1):
                        total_distance += self.route_coordinates[i].distanceTo(self.route_coordinates[i + 1])
                    
                    # Send using both methods
                    print(f"Alternative method: Sending initial distance {total_distance:.1f}m")
                    self.remainingDistance.emit(float(total_distance))
                    self.updateDistance.emit(float(total_distance))
                
                # Alternative: Use Qt's single-shot instead of QTimer
                QTimer.singleShot(100, self.moveToNextPosition)
                
                print("Demo started with alternative method")
                return True
            else:
                print("No route available for alternative method")
                return False
        except Exception as e:
            print(f"Error in alternative demo start: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @pyqtSlot()
    def stopSimulation(self):
        """Stop demo navigation"""
        print(f"\n===== Stopping Demo Navigation =====")
        self.simulation_active = False
        
        if self.single_timer.isActive():
            print("Stopping active timer")
            self.single_timer.stop()
        
        print(f"Simulation stopped: Total updates = {self.update_count}")
        
        # Report final state if stopped during navigation
        if self.current_route_index < len(self.route_coordinates) - 1:
            print(f"Stopped midway: Position = {self.current_route_index}/{len(self.route_coordinates)-1}")
        else:
            print("Normal completion: Destination reached")
    
    def moveToNextPosition(self):
        """Move to next position and schedule next update with single-shot timer"""
        try:
            if not self.simulation_active:
                print("Simulation is stopped")
                return
                
            # Increment update counter
            self.update_count += 1
            
            # Prevent infinite loops by checking elapsed time
            if self.update_count > 5000:  # Empirical upper limit
                print("Warning: Update count limit reached. Stopping simulation.")
                self.stopSimulation()
                return
            
            # Check route exists and destination not yet reached
            if not self.route_coordinates:
                print("No route set")
                self.stopSimulation()
                return
                
            # Check if destination reached
            if self.current_route_index >= len(self.route_coordinates) - 1:
                # Move to final point
                self.positionUpdated.emit(self.route_coordinates[-1])
                
                # Arrival announcement
                arrival_message = self.getMessage('arrival')
                self.nextInstruction.emit(arrival_message)
                self.speakInstruction(arrival_message)
                
                print(f"Simulation completed: Updates = {self.update_count}")
                self.stopSimulation()
                return
            
            # Current and next position
            current_pos = self.route_coordinates[self.current_route_index]
            next_pos = self.route_coordinates[self.current_route_index + 1]
            
            # Calculate distance between points
            distance = current_pos.distanceTo(next_pos)
            
            # Calculate distance to move in one update
            distance_to_move = self.simulation_speed * (self.simulation_interval / 1000.0)
            
            # Handle extremely small distances
            if distance < 0.01:  # Less than 1cm
                print(f"Warning: Extremely small distance between points ({distance:.6f}m) - Index {self.current_route_index}")
                # Force move to next point
                self.current_route_index += 1
                
                # Move to next point if it exists
                if self.current_route_index < len(self.route_coordinates):
                    self.positionUpdated.emit(self.route_coordinates[self.current_route_index])
                    # Schedule next update
                    if self.simulation_active:
                        self.single_timer.start(self.simulation_interval)
                    return
                else:
                    # End if it was the last point
                    self.current_route_index = len(self.route_coordinates) - 1
                    self.positionUpdated.emit(self.route_coordinates[-1])
                    self.stopSimulation()
                    return
            
            # Calculate next position
#            if distance <= distance_to_move:
            if True:
                # Can reach next point, so move there
                self.current_route_index += 1
                
                # If distance remaining is large, move through multiple points
                remaining_distance = distance_to_move - distance
                loop_count = 0  # Safety loop counter
                
                while remaining_distance > 0 and self.current_route_index < len(self.route_coordinates) - 1 and loop_count < 100:
                    loop_count += 1  # Prevent infinite loops
                    
                    current_pos = self.route_coordinates[self.current_route_index]
                    next_pos = self.route_coordinates[self.current_route_index + 1]
                    
                    distance = current_pos.distanceTo(next_pos)
                    
                    # Handle extremely small distances
                    if distance < 0.01:  # Less than 1cm
                        print(f"Warning: Extremely small distance in loop ({distance:.6f}m)")
                        self.current_route_index += 1
                        continue
                    
                    if distance <= remaining_distance:
                        self.current_route_index += 1
                        remaining_distance -= distance
                    else:
                        # Stop before next point
                        if distance > 0:  # Prevent division by zero
                            fraction = remaining_distance / distance
                            delta_lat = next_pos.latitude() - current_pos.latitude()
                            delta_lon = next_pos.longitude() - current_pos.longitude()
                            
                            next_lat = current_pos.latitude() + (delta_lat * fraction)
                            next_lon = current_pos.longitude() + (delta_lon * fraction)
                            
                            # Report interpolated position
                            intermediate_position = QGeoCoordinate(next_lat, next_lon)
                            self.positionUpdated.emit(intermediate_position)
                        break
                
                if loop_count >= 100:
                    print("Warning: Loop count limit reached in route point processing")
                
                # Check index bounds
                if self.current_route_index >= len(self.route_coordinates):
                    self.current_route_index = len(self.route_coordinates) - 1
                
                # Update current position (was missing in original code)
                current_position = self.route_coordinates[self.current_route_index]
                self.positionUpdated.emit(current_position)
            else:
                # Can't reach next point, calculate intermediate position
                if distance > 0:  # Prevent division by zero
                    fraction = distance_to_move / distance
                    delta_lat = next_pos.latitude() - current_pos.latitude()
                    delta_lon = next_pos.longitude() - current_pos.longitude()
                    
                    next_lat = current_pos.latitude() + (delta_lat * fraction)
                    next_lon = current_pos.longitude() + (delta_lon * fraction)
                    
                    # Report interpolated position
                    intermediate_position = QGeoCoordinate(next_lat, next_lon)
                    self.positionUpdated.emit(intermediate_position)
                else:
                    # Force move to next point if distance is zero
                    print("Warning: Zero distance, forcing move to next point")
                    self.current_route_index += 1
                    if self.current_route_index < len(self.route_coordinates):
                        self.positionUpdated.emit(self.route_coordinates[self.current_route_index])
                    else:
                        # Prevent out of bounds
                        self.current_route_index = len(self.route_coordinates) - 1
                        self.positionUpdated.emit(self.route_coordinates[-1])
            
            # Check for next instruction (turns, etc.)
            self.checkNextInstruction()
            
            # Calculate remaining distance
            remaining_distance = 0
            for i in range(self.current_route_index, len(self.route_coordinates) - 1):
                pos1 = self.route_coordinates[i]
                pos2 = self.route_coordinates[i + 1]
                remaining_distance += pos1.distanceTo(pos2)
            
            # Send remaining distance (convert explicitly to float for reliability)
            self.remainingDistance.emit(float(remaining_distance))
            # Send with backup signal too
            self.updateDistance.emit(float(remaining_distance))
            
            # Debug output
            if self.update_count % 5 == 0 or self.update_count < 5:
                print(f"Distance signal sent: {remaining_distance:.1f}m")
            
            # Report progress periodically
            if self.update_count % 5 == 0 or self.update_count < 5:
                print(f"Update {self.update_count}: Position {self.current_route_index}/{len(self.route_coordinates)-1}, Distance remaining: {remaining_distance:.1f}m")
            
            # Schedule next update
            if self.simulation_active:
                print(f"Scheduling next position update: Count {self.update_count + 1}")
                self.single_timer.start(self.simulation_interval)
            else:
                print("No next update scheduled - simulation inactive")
        
        except Exception as e:
            print(f"Error during position update: {str(e)}")
            # Still schedule next update even after error
            if self.simulation_active:
                print("Scheduling next update after error")
                self.single_timer.start(self.simulation_interval)
    
    def checkNextInstruction(self):
        """Check for upcoming instructions and notify if needed"""
        if not self.route_instructions or self.current_instruction_index >= len(self.route_instructions) - 1:
            return
        
        next_instruction = self.route_instructions[self.current_instruction_index + 1]
        instruction_point_index = next_instruction['index']
        
        # Number of points in advance for notification (higher means earlier notification)
        advance_notice_points = 5
        
        # When approaching the point for the next instruction
        if self.current_route_index >= instruction_point_index - advance_notice_points:
            self.current_instruction_index += 1
            instruction_text = next_instruction['text']
            distance = next_instruction['distance']
            
            # Format distance for voice guidance
            if distance > 1000:
                distance_text = self.getMessage('km_ahead', round(distance / 1000, 1), instruction_text)
            else:
                distance_text = self.getMessage('m_ahead', round(distance), instruction_text)
            
            # Notify and speak instruction
            self.nextInstruction.emit(distance_text)
            self.speakInstruction(distance_text)
    
    def speakInstruction(self, text):
        """Provide voice guidance"""
        print(f"Speaking: {text}")
        try:
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
        except Exception as e:
            print(f"Voice guidance error: {str(e)}")
            # Continue app even if voice fails

def main():
    app = QGuiApplication(sys.argv)
    
    # Create NavigationController instance
    nav_controller = NavigationController()
    
    # Set up QML engine
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("navController", nav_controller)
    
    # Load QML file
    engine.load(QUrl.fromLocalFile("navigation.qml"))
    
    if not engine.rootObjects():
        return -1
    
    # Pre-calculate a route for Mountain View area after application starts
    QTimer.singleShot(500, lambda: nav_controller.calculateRoute(DEFAULT_START_COORDINATE, DEFAULT_END_COORDINATE))
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())