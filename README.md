# IoT-Smart-Tourism-Guide

## Description

**Smart Tourism Guide** is a project aimed at modernizing the experience of visitors to cultural sites using technology. The focus is on offering real-time notifications based on geolocation and proximity detection, along with interactive features to enrich the user experience.

## Features Implemented

- **Dynamic Proximity Detection**:
  - IR sensor with Raspberry Pi to detect visitor presence.
  - Distance calculations between visitor GPS and predefined locations using `geopy`.
- **Real-Time Notifications**:
  - Web Push notifications for subscribers near specific locations.
  - Secure subscription management via a web system.
- **QR Code Integration**:
  - Generated QR codes for quick access to site information.

## Technologies Used

### Hardware

- Raspberry Pi 3 B+
- IR Proximity Sensor

### Backend

- Flask (APIs and routing)
- PyWebPush (notifications)

### Frontend

- HTML, CSS, JavaScript
- Service Workers (browser notifications)

### Libraries

- `geopy` for GPS distance calculations.
- `qrcode` for QR code generation.

## Future Plans

- Augmented Reality content with 3D reconstructions and animations.
- Multilingual support for international visitors.
- Database integration for scalable management of locations and subscriptions.
- Gamification features to enhance visitor engagement.

---

**Note**: This project is a work in progress and not yet fully complete. The next steps involve refining features and implementing advanced functionalities.
