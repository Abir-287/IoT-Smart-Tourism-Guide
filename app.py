from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
import qrcode
import os
from geopy.distance import geodesic
import requests
import json
import threading
import RPi.GPIO as GPIO
import time
from pywebpush import webpush, WebPushException

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# VAPID keys for web push notifications
VAPID_PUBLIC_KEY = "add your vapid public key here"  
VAPID_PRIVATE_KEY = "add your vapid private key here"

# Predefined locations 
locations = [
    {
        "id": 1,
        "name": "Musée Historique",
        "latitude": 35.6895,
        "longitude": 139.6917,
        "description": "Un musée fascinant avec des artefacts anciens.",
        "video_url": "static/videos/museum.mp4"
    },
    {
        "id": 2,
        "name": "Monument Ancien",
        "latitude": 35.6845,
        "longitude": 139.6920,
        "description": "Un monument ancien avec une histoire riche.",
        "video_url": "static/videos/monument.mp4"
    },{ 
        "id": 3,
        "name": "ENISo Sousse",
        "latitude": 35.8288,
        "longitude": 10.6404,
        "description": "Ecole Nationale d'Ingenieurs de Sousse, a premier engineering school in Tunisia.",
        "video_url": "static/videos/eniso.mp4"
    },{
        "id": 5,
        "name": "Tunis",
        "latitude": 36.8232,
        "longitude": 10.1701,
        "description": "Capital city of Tunisia.",
        "video_url": ""
    }

]

# Ensure QR codes folder exists
os.makedirs("qr_codes", exist_ok=True)

# IR Sensor Setup
IR_PIN = 16  # Adjust based on your GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IR_PIN, GPIO.IN)

# Store subscriptions
subscriptions = []

# Function to monitor IR sensor
def monitor_ir_sensor():
    while True:
        if not GPIO.input(IR_PIN):
            print("Obstacle détecté")
            socketio.emit("notification", {"message": "Obstacle détecté!"})
            for subscription in subscriptions:
                send_web_push(subscription, "Vous etes proche . Scannez le QR code pour en savoir plus !!")
            time.sleep(1)  # Avoid rapid triggering
        time.sleep(0.1)

# Function to send web push notification
def send_web_push(subscription_info, message):
    try:
        webpush(
            subscription_info,
            data=json.dumps({"title": "Alerte de proximité", "body": message}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": "mailto:example@example.com"}
        )
        print("Notification web envoyée.")
    except WebPushException as ex:
        print("Erreur lors de l'envoi de la notification web:", ex)

# Route: Homepage
@app.route('/')
def index():
    return render_template("index.html", locations=locations, vapid_public_key=VAPID_PUBLIC_KEY)

# Route: Subscribe to Web Push Notifications
@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription_info = request.json
    subscriptions.append(subscription_info)
    print("Nouvel abonnement ajouté:", subscription_info)
    return jsonify({"message": "Abonnement réussi"}), 200

# Route: Generate QR Code
@app.route('/generate_qr/<int:location_id>')
def generate_qr(location_id):
    location = next((loc for loc in locations if loc["id"] == location_id), None)
    if not location:
        return "Lieu non trouvé.", 404

    qr = qrcode.make(f"http://127.0.0.1:5000/location/{location_id}")
    qr_path = f"qr_codes/{location_id}.png"
    qr.save(qr_path)
    return send_file(qr_path, mimetype='image/png')

# Route: Location Details
@app.route('/location/<int:location_id>')
def location(location_id):
    location = next((loc for loc in locations if loc["id"] == location_id), None)
    if not location:
        return "Lieu non trouvé.", 404
    return render_template("location.html", location=location)

@app.route('/scan')
def scan():
    return render_template("scan.html")
    
@app.route('/monument/<name>')
def monument(name):
    print(f"Received name: {name}")
    # Decode URL-encoded names (if necessary)
    from urllib.parse import unquote
    decoded_name = unquote(name)
    print(f"Decoded name: {decoded_name}")

    # Find the monument by its name
    monument = next((loc for loc in locations if loc["name"].lower() == decoded_name.lower()), None)
    if not monument:
        return "Monument non trouve.", 404

    print(f"Found monument: {monument}")
    return render_template("monument.html", location=monument)



# Route: Check Proximity
@app.route('/check_proximity', methods=['GET'])
def check_proximity():
    user_location = get_ip_location()
    if not user_location:
        return jsonify({"message": "Impossible de récupérer la position."}), 500

    user_lat, user_lon = user_location["lat"], user_location["lon"]

    for location in locations:
        distance = geodesic((user_lat, user_lon), (location["latitude"], location["longitude"])).km
        if distance < 100:  # Within 500 meters
            for subscription in subscriptions:
                send_web_push(subscription, f"Vous êtes proche de {location['name']}!")
            return jsonify(location)

    return jsonify({"message": "Aucun lieu détecté à proximité."})

# SocketIO: Handle client connection
@socketio.on('connect')
def handle_connect():
    print("Client connecté.")

# Function to get GPS location using IP
def get_ip_location():
    url = "http://ip-api.com/json/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("User location fetched:", data)  # Debug log
        return {
            "lat": data["lat"],
            "lon": data["lon"],
            "city": data["city"],
            "country": data["country"]
        }
    print("Failed to fetch user location.")  # Debug log
    return None

    
    
@app.route('/test_notification', methods=['POST'])
def test_notification():
    # Ensure there are subscriptions
    if not subscriptions:
        return jsonify({"message": "No active subscriptions"}), 400

    # Message for the notification
    message = "This is a test notification from your Raspberry Pi!"

    # Send the notification to all active subscriptions
    for subscription in subscriptions:
        send_web_push(subscription, message)

    return jsonify({"message": "Test notification sent to all subscribers!"}), 200
 

# Start monitoring IR sensor in a separate thread
threading.Thread(target=monitor_ir_sensor, daemon=True).start()

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
