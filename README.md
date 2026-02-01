# stream-pad-web

A web-based control panel for OBS that lets you control your stream from your phone or tablet. Think of it like an Elgato Stream Deck, but accessible from any browser on your local network.

Built with Flask and Python, this creates a local web server that connects to OBS Studio. Switch scenes, toggle sources, and control audio from anywhere in your house.

## Features

- 📱 Control OBS from any device with a web browser
- 🎬 One-tap scene switching
- 🔇 Quick audio source mute/unmute controls
- 🎨 Customizable button layouts and icons
- 🌐 Works over local network - no internet required
- ⚡ Real-time WebSocket connection to OBS

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Prerequisites

1. **OBS Studio** (latest version)
2. **Enable OBS WebSocket Server**:
   - Open OBS Studio
   - Go to **Tools** → **WebSocket Server Settings**
     <br>
     <img width="180" height="198" alt="image" src="https://github.com/user-attachments/assets/ae1e12d2-c452-42ce-b45a-90b33ccc448b" />
     </br>
   - Enable **WebSocket server**
     <br>
     <img width="665" height="297" alt="image" src="https://github.com/user-attachments/assets/8eb08d32-c22e-4318-bc2b-836e3acc7490" />
     </br>
   - Click **Show Connect Info** to reveal the Server IP, Server Port, and Password.

---

## Installation

### Using the Executable (Recommended)

1. Download the latest release from [Releases](https://github.com/stevent-surya/stream-pad-web/releases)
2. Extract the ZIP file to a folder
3. Ensure the folder contains:
   - `START.bat` - Run this to start the application
   - `Stream Controller.exe` - Main application
   - `config.json` - Configuration file
   - `assets/` folder - For custom icons

### Running

1. **Double-click `START.bat`** (recommended)
   - This will start the application with error logging
   - If there's an error, the console window stays open so you can see what went wrong
   - Useful for troubleshooting configuration issues

2. Alternatively, you can double-click `Stream Controller.exe` directly

3. The console will display:
```
      ============================================================
       STREAM CONTROLLER - ACTIVE
      ============================================================
      
      [STATUS] Server is running.
      [GUIDE]  Open this URL on your mobile device:
               http://192.168.1.10:5000
      
      [NOTE]   Ensure your PC and mobile device are on the same Wi-Fi.
      [NOTE]   Keep this window open while streaming.
```
4. Open the URL on your phone/tablet to access the controller

**First Time Setup:**
- If `config.json` doesn't exist, the app will show an error
- Create a `config.json` file using the template in [Configuration](#configuration) section
- Run `START.bat` again

---

## Configuration

All settings are managed in `config.json`. Edit with any text editor.

### Structure Overview
```json
{
    "ui_settings": { ... },
    "obs_settings": { ... },
    "audio_sources": [ ... ],
    "buttons": [ ... ]
}
```

### UI Settings
```json
"ui_settings": {
    "scene_width_percent": 75,
    "grid_columns": 3
}
```

- `scene_width_percent`: Screen width for scene buttons (50-90)
- `grid_columns`: Number of buttons per row

### OBS Connection
```json
"obs_settings": {
    "host": "192.168.1.10",
    "port": 4455,
    "password": "your_password"
}
```

- `host`: Your PC's IP address (use `ipconfig` on Windows to find it)
- `port`: OBS WebSocket port (default: 4455)
- `password`: Password from OBS WebSocket settings

### Audio Sources
```json
"audio_sources": [
    {
        "name": "Mic/Aux",
        "icon_type": "fa",
        "icon": "fa-microphone"
    },
    {
        "name": "Discord",
        "icon_type": "img",
        "icon": "discord.jpg"
    }
]
```

- `name`: Exact name from OBS Audio Mixer
- `icon_type`: `"fa"` for Font Awesome icons, `"img"` for custom images
- `icon`: Icon class name or image filename (must be in `assets/` folder)

### Scene Buttons
```json
"buttons": [
    {
        "label": "START",
        "scene_obs": "Start Stream",
        "icon_type": "fa",
        "icon": "fa-signal",
        "style": "normal"
    },
    {
        "label": "BRB",
        "scene_obs": "Be Right Back",
        "icon_type": "fa",
        "icon": "fa-mug-hot",
        "style": "normal"
    }
]
```

- `label`: Button display text
- `scene_obs`: Exact OBS scene name (case-sensitive)
- `icon_type`: `"fa"` or `"img"`
- `icon`: Font Awesome class or image filename
- `style`: Button color - `normal`, `pink`, `purple`, `yellow`, `red_wide`

### Custom Icons

1. Place image files (`.png`, `.jpg`) in the `assets/` folder
2. Reference filename in `config.json`:
```json
   {
       "icon_type": "img",
       "icon": "my-icon.png"
   }
```
3. Restart the application

**Font Awesome Icons:** Find icons at [fontawesome.com/icons](https://fontawesome.com/icons)

---

## Development

Want to modify the code or contribute to the project? Here's how to get set up.

### Environment Setup

You'll need **Python 3.8 or newer** installed on your PC.

1. **Clone the repository**:
```bash
git clone https://github.com/stevent-surya/stream-pad-web.git  
cd stream-pad-web
```

2. **Create a virtual environment**:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Running Locally

Run the app with Python - it'll automatically look for `config.json` in the project root:
```bash
python app.py
```

Open your browser and go to `http://localhost:5000` to see the interface.

### Project Structure
```
   stream-pad-web/
   ├── START.bat              # Launcher with error logging
   ├── Stream Controller.exe  # Main application
   ├── app.py                 # Flask app entry point
   ├── templates/
   │   └── index.html         # Web interface
   ├── assets/                # Icons and custom images
   │   ├── discord.jpg
   │   ├── music.png
   │   └── osu.jpg
   ├── config.json            # User configuration
   └── requirements.txt       # Python dependencies
```
Feel free to poke around and modify whatever you want!

---

## Troubleshooting

### Connection Issues

| Problem | Solution |
|---------|----------|
| Authentication Failed | Verify password in `config.json` matches OBS WebSocket settings |
| Connection Refused | Ensure OBS is running and WebSocket server is enabled |
| Can't access from phone | Check both devices are on same WiFi network and `host` IP is correct |

### Button Issues

| Problem | Solution |
|---------|----------|
| Scene won't switch | Verify `scene_obs` matches OBS scene name exactly (case-sensitive) |
| Audio mute not working | Verify `name` matches source in OBS Audio Mixer exactly |
| Icon not showing | Check filename matches and file exists in `assets/` folder |

### Config File Issues

| Problem | Solution |
|---------|----------|
| "Config file not found" error | Create `config.json` using the template above |
| Syntax errors | Validate JSON at [jsonlint.com](https://jsonlint.com) |
| Changes not applying | Restart the application after editing |
| Missing elements | Ensure all required fields are present |

**Common JSON mistakes:**
- Missing commas between objects
- Trailing comma after last item
- Unmatched brackets or quotes

**Tip:** Always use `START.bat` to run the application - if there's a config error, the console window will stay open and show you exactly what's wrong.

---

## License

Copyright (c) 2026 Aspire. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
