import sys
import json
import time
import logging
import threading
import socket
from pathlib import Path
from typing import Dict, Any, Optional

# send_from_directory needed for external assets
from flask import Flask, render_template, request, cli, send_from_directory
from flask_socketio import SocketIO, emit
import obsws_python as obs

# Logging Configuration
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('obsws_python').setLevel(logging.WARN)
logging.getLogger('urllib3').setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("StreamController")

cli.show_server_banner = lambda *x: None

# Path Configuration
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.resolve()

CONFIG_FILE = BASE_DIR / "config.json"
ASSETS_DIR = BASE_DIR / "assets"  # [ADDED] External assets folder

# Configuration Manager
class ConfigLoader:
    @staticmethod
    def load() -> Dict[str, Any]:
        if not CONFIG_FILE.exists():
            print(f"\n[CRITICAL] Configuration file not found at:\n{CONFIG_FILE}")
            print("Please create 'config.json' and restart the application.\n")
            sys.exit(1)
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"\n[CRITICAL] Invalid JSON format in 'config.json':\n{e}\n")
            sys.exit(1)

# OBS WebSocket Bridge
class OBSBridge:
    def __init__(self, config: Dict[str, Any], socket_instance: SocketIO):
        self.settings = config.get('obs_settings', {})
        self.sources = [s['name'] for s in config.get('audio_sources', [])]
        self.socket = socket_instance
        self.client: Optional[obs.ReqClient] = None
        self._is_connected = False
        self._stop_event = threading.Event()

    def connect(self):
        try:
            self.client = obs.ReqClient(
                host=self.settings.get('host', 'localhost'),
                port=self.settings.get('port', 4455),
                password=self.settings.get('password', '')
            )
            self._is_connected = True
        except Exception:
            self._is_connected = False

    def start_service(self):
        thread = threading.Thread(target=self._poll_loop, daemon=True)
        thread.start()

    def _poll_loop(self):
        last_scene = ""
        last_volumes = {src: -1 for src in self.sources}

        while not self._stop_event.is_set():
            if not self._is_connected or not self.client:
                self.connect()
                time.sleep(2)
                continue

            try:
                current_scene = self.client.get_current_program_scene().current_program_scene_name
                if current_scene != last_scene:
                    self.socket.emit('update_scene', {'scene': current_scene})
                    last_scene = current_scene

                for source in self.sources:
                    try:
                        vol_data = self.client.get_input_volume(source)
                        vol_pct = round(vol_data.input_volume_mul * 100)
                        if last_volumes.get(source) != vol_pct:
                            self.socket.emit('update_volume', {'source': source, 'val': vol_pct})
                            last_volumes[source] = vol_pct
                    except Exception:
                        pass 
            except Exception:
                self._is_connected = False
            
            time.sleep(0.5)

    def set_scene(self, scene_name: str):
        if self._is_connected and self.client:
            try:
                self.client.set_current_program_scene(scene_name)
                self.socket.emit('update_scene', {'scene': scene_name})
            except Exception:
                pass

    def set_volume(self, source: str, volume: int):
        if self._is_connected and self.client:
            try:
                self.client.set_input_volume(source, vol_mul=(volume / 100.0))
            except Exception:
                pass

    def get_initial_state(self) -> Dict[str, Any]:
        if not self._is_connected or not self.client:
            return {}
        
        state = {'volumes': {}}
        try:
            state['scene'] = self.client.get_current_program_scene().current_program_scene_name
            for src in self.sources:
                try:
                    vol = self.client.get_input_volume(src).input_volume_mul
                    state['volumes'][src] = round(vol * 100)
                except Exception:
                    pass
        except Exception:
            pass
        return state

# Flask & SocketIO Setup
config = ConfigLoader.load()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
obs_bridge = OBSBridge(config, socketio)

@app.route('/')
def index():
    return render_template(
        'index.html',
        buttons=config.get('buttons', []),
        audios=config.get('audio_sources', []),
        layout=config.get('ui_settings', {"scene_width_percent": 65, "grid_columns": 3})
    )

# Route to serve icons from the external 'assets' folder
@app.route('/custom_icons/<path:filename>')
def serve_custom_icons(filename):
    return send_from_directory(ASSETS_DIR, filename)

@socketio.on('connect')
def handle_connect():
    state = obs_bridge.get_initial_state()
    if 'scene' in state:
        emit('update_scene', {'scene': state['scene']})
    if 'volumes' in state:
        for src, vol in state['volumes'].items():
            emit('update_volume', {'source': src, 'val': vol})

@socketio.on('command_scene')
def on_scene_command(data):
    obs_bridge.set_scene(data['scene'])

@socketio.on('command_volume')
def on_volume_command(data):
    obs_bridge.set_volume(data['source'], int(data['val']))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print(" STREAM CONTROLLER - ACTIVE")
        print("="*60)

        obs_bridge.start_service()

        local_ip = get_local_ip()
        print(f"\n[STATUS] Server is running.")
        print(f"[GUIDE]  Open this URL on your mobile device:")
        print(f"         http://{local_ip}:5000\n")
        print("[NOTE]   Ensure your PC and mobile device are on the same Wi-Fi.")
        print("[NOTE]   Keep this window open while streaming.\n")

        socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, log_output=False)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("\n" + "!"*60)
        print("CRITICAL ERROR:")
        print(e)
        print("!"*60 + "\n")
        input("Press [ENTER] to exit...")