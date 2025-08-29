# 🚗 Driver Monitoring System

A real-time driver fatigue detection system that monitors prolonged eye closure and yawning patterns to enhance road safety through intelligent alerts and comprehensive dashboard monitoring.

![License](https://img.shields.io/github/license/YonkimonkY/DriverMonitoring)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 Features

### Core Detection Capabilities
- **Real-time Eye Closure Detection** - Monitors prolonged eye closure using advanced computer vision
- **Yawn Detection** - Identifies yawning patterns as fatigue indicators  
- **Audio Alert System** - Immediate audio warnings when fatigue is detected
- **Multi-threshold Monitoring** - Configurable sensitivity levels for different driving conditions

### Dashboard & Analytics
- **Web-based Dashboard** - Real-time monitoring interface with live camera feed
- **Event Logging** - Comprehensive tracking of all fatigue detection events
- **Historical Data** - Review past driving sessions and fatigue patterns
- **Alert Statistics** - Analyze frequency and types of fatigue events

### Safety Features
- **Instant Notifications** - Immediate audio and visual alerts
- **Customizable Thresholds** - Adjust sensitivity based on driver preferences
- **Session Recording** - Optional recording of driving sessions for analysis
- **Emergency Protocols** - Escalating alert system for severe fatigue detection

## 🛠️ Technology Stack

- **Computer Vision**: OpenCV, dlib
- **Machine Learning**: Face landmark detection, Eye Aspect Ratio (EAR) analysis
- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Audio Processing**: pygame/playsound
- **Real-time Processing**: Threading, Queue management

## 📋 Prerequisites

- Python 3.7 or higher
- Webcam or external camera
- Audio output device (speakers/headphones)

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux Ubuntu 18.04+
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: Multi-core processor recommended for real-time processing
- **Camera**: 720p resolution minimum (1080p recommended)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YonkimonkY/DriverMonitoring.git
cd DriverMonitoring
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Required Model
The `shape_predictor_68_face_landmarks.dat` file should already be included in your repository. If not, download it from:
```bash
# Download the dlib facial landmark predictor model
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### 5. Run the Application
```bash
python app.py
```

## 🎮 Usage

### Quick Start
```bash
python app.py
```

### Web Dashboard
1. Start the application: `python app.py`
2. Open your browser and navigate to `http://localhost:5000`
3. Allow camera permissions when prompted
4. Begin monitoring - the system will automatically detect fatigue signs


## 🔧 Configuration

### Detection Parameters
```python
# config.py
EYE_ASPECT_RATIO_THRESHOLD = 0.25    # Lower = more sensitive
YAWN_THRESHOLD = 20                   # Mouth opening threshold
FATIGUE_FRAME_COUNT = 15             # Consecutive frames for alert
ALERT_COOLDOWN = 3                   # Seconds between alerts
```

### Camera Settings
```python
CAMERA_INDEX = 0                     # Default camera
CAMERA_WIDTH = 640                   # Resolution width
CAMERA_HEIGHT = 480                  # Resolution height
FPS_TARGET = 30                      # Target frame rate
```

## 📊 Dashboard & Statistics

### Live Monitoring Interface
The web dashboard provides real-time monitoring with comprehensive statistics and visual feedback.

![Dashboard Statistics](screenshot_stats.png)
*Real-time statistics dashboard showing detection metrics and driver monitoring data*

### Dashboard Features
- Live camera feed with facial landmark overlay
- Current fatigue status indicators
- Real-time eye aspect ratio graphs
- Active alert notifications

### Analytics Panel
- Session duration and statistics  
- Fatigue event timeline
- Alert frequency charts
- Driver behavior patterns

### Settings Panel
- Threshold adjustments
- Alert preferences
- Camera configuration
- Data export options

## 🔍 How It Works

### Detection Algorithm
1. **Face Detection**: Locate face using Haar cascades or HOG detector
2. **Landmark Extraction**: 68-point facial landmark detection using dlib
3. **Eye Analysis**: Calculate Eye Aspect Ratio (EAR) for drowsiness detection
4. **Mouth Monitoring**: Analyze mouth opening ratio for yawn detection
5. **Threshold Processing**: Compare metrics against configurable thresholds
6. **Alert Generation**: Trigger audio/visual alerts when fatigue detected

### Eye Aspect Ratio Formula
```
EAR = (|p2-p6| + |p3-p5|) / (2|p1-p4|)
```
Where p1...p6 are eye landmark coordinates.

## 📁 Project Structure

```
proyecto_drowsiness/
├── app.py                     # Main Flask application entry point
├── requirements.txt           # Python dependencies
├── shape_predictor_68_face_landmarks.dat  # dlib facial landmark model
├── static/                   # Static web assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # Client-side JavaScript
│   └── images/              # Images and assets
├── templates/                # HTML templates for Flask
│   ├── index.html           # Main dashboard interface
│   └── stats.html           # Statistics page
```


## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure cross-platform compatibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This system is designed as a driver assistance tool and should not be relied upon as the sole method of preventing drowsy driving. Always ensure adequate rest before driving and pull over safely if you feel drowsy.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YonkimonkY/DriverMonitoring/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YonkimonkY/DriverMonitoring/discussions)
- **Documentation**: [Wiki](https://github.com/YonkimonkY/DriverMonitoring/wiki)

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- dlib library for facial landmark detection
- Contributors and testers who helped improve the system
- Road safety organizations promoting drowsy driving awareness

## 📈 Roadmap

- [ ] Mobile app integration
- [ ] Cloud-based analytics
- [ ] Integration with vehicle systems
- [ ] Advanced ML models for improved accuracy
- [ ] Multi-language support
- [ ] API for third-party integrations

---

**🚨 Drive safely and stay alert!** 

If this project helps improve road safety, please consider giving it a ⭐ star!
