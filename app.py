# -*- coding: utf-8 -*-
"""
Re:Zero Live2D Desktop Companion
Windows 바탕화면 투명 Live2D 리제로 마스코트 & 다중 캐릭터 변경 지원 (코덱스 Codex 연동 지원)
(순수 시각/말풍선/모션 컴패니언 - TTS 의존성 제거)
"""

import os
import sys
import time
import json
import random
import tempfile
import urllib.request
import urllib.parse
import threading
import ctypes
import traceback
from ctypes import wintypes
from bottle import Bottle, request, response, static_file, HTTPResponse
import webview

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

CRASH_LOG = os.path.join(APP_DIR, "crash.log")
def log_msg(msg):
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

sys.excepthook = lambda t, v, tb: log_msg(f"Unhandled: {''.join(traceback.format_exception(t, v, tb))}")
threading.excepthook = lambda a: log_msg(f"Thread: {a.exc_type} {a.exc_value}\n{''.join(traceback.format_tb(a.exc_traceback))}")

WV2_STORAGE = os.path.join(tempfile.gettempdir(), "rezero_wv2_data")
os.makedirs(WV2_STORAGE, exist_ok=True)

try:
    from character_manager import char_mgr, CHARACTERS_DIR
except Exception as e:
    log_msg(f"Failed to import character_manager: {e}")
    CHARACTERS_DIR = os.path.join(APP_DIR, "Live2D Characters")
    char_mgr = None

try:
    from emotion_engine import analyze_emotion, CODEX_EVENTS
except Exception as ee:
    log_msg(f"Failed to import emotion_engine: {ee}")
    CODEX_EVENTS = {}
    def analyze_emotion(t):
        return {"key": "normal", "clean_text": t}

# Win32 APIs
user32 = ctypes.windll.user32
user32.GetCursorPos.argtypes = [ctypes.c_void_p]
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.c_void_p]
user32.GetWindowRect.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.SetWindowPos.restype = wintypes.BOOL
user32.ReleaseCapture.argtypes = []
user32.ReleaseCapture.restype = wintypes.BOOL
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
user32.SendMessageW.restype = ctypes.c_ssize_t

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', wintypes.DWORD),
        ('dwMemoryLoad', wintypes.DWORD),
        ('ullTotalPhys', ctypes.c_uint64),
        ('ullAvailPhys', ctypes.c_uint64),
        ('ullTotalPageFile', ctypes.c_uint64),
        ('ullAvailPageFile', ctypes.c_uint64),
        ('ullTotalVirtual', ctypes.c_uint64),
        ('ullAvailVirtual', ctypes.c_uint64),
        ('ullAvailExtendedVirtual', ctypes.c_uint64),
    ]

def get_system_load():
    mem_load = 0
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            mem_load = stat.dwMemoryLoad
    except Exception:
        pass
    return 10.0, float(mem_load)

CONFIG_PATH = os.path.join(APP_DIR, "config.json")
DEFAULT_CONFIG = {
    "character": "ac_base_rem01",
    "win_w": 320,
    "win_h": 400,
    "scale": 1.0,
    "subtitle_enabled": True,
    "subtitle_size": 13,
    "display_mode": "bubble",
    "resource_alert": True,
    "subtitle_mode": True,
    "port": 8990
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg = dict(DEFAULT_CONFIG)
                cfg.update(data)
                return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log_msg(f"Failed to save config: {e}")
        return False

# Webview instances
main_window = None
settings_window = None

class TrackerApi:
    def __init__(self):
        self.hwnd = None

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd

    def close_settings(self):
        global settings_window
        if settings_window is not None:
            try:
                settings_window.destroy()
            except Exception:
                pass
            settings_window = None
            return True
        return False

    def toggle_settings(self):
        global settings_window
        if settings_window is not None:
            try:
                settings_window.destroy()
            except Exception:
                pass
            settings_window = None
            return False

        try:
            cfg = load_config()
            port = cfg.get("port", 8990)
            settings_url = f"http://127.0.0.1:{port}/settings?_v={int(time.time() * 1000)}"
            settings_window = webview.create_window(
                "🌸 Re:Zero Live2D 컴패니언 설정",
                url=settings_url,
                width=620,
                height=700,
                resizable=True,
                on_top=True,
                js_api=self
            )
            def on_settings_closed():
                global settings_window
                settings_window = None
            settings_window.events.closed += on_settings_closed
            return True
        except Exception as e:
            log_msg(f"create settings_window error: {e}")
            settings_window = None
            return False

    def open_settings(self):
        global settings_window
        if settings_window is not None:
            self.close_settings()
            time.sleep(0.15)
        return self.toggle_settings()

    def start_drag(self):
        if self.hwnd and user32.IsWindow(self.hwnd):
            user32.ReleaseCapture()
            user32.SendMessageW(self.hwnd, 0x0112, 0xF012, 0)
            return True
        return False

    def move_window(self, dx, dy):
        if self.hwnd and user32.IsWindow(self.hwnd):
            rect = wintypes.RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            user32.SetWindowPos(self.hwnd, 0, rect.left + int(dx), rect.top + int(dy), 0, 0, 0x0001 | 0x0004 | 0x0010)
            return True
        return False

    def resize_window(self, width, height):
        if self.hwnd and user32.IsWindow(self.hwnd):
            rect = wintypes.RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            new_w = max(260, min(1920, int(width)))
            new_h = max(320, min(1440, int(height)))
            new_x = rect.right - new_w
            new_y = rect.bottom - new_h
            user32.SetWindowPos(self.hwnd, 0, new_x, new_y, new_w, new_h, 0x0004 | 0x0010)
            cfg = load_config()
            cfg["win_w"] = new_w
            cfg["win_h"] = new_h
            save_config(cfg)
            return True
        return False

    def get_tracking(self):
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        rect = wintypes.RECT()
        if self.hwnd and user32.IsWindow(self.hwnd):
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            center_x = (rect.left + rect.right) / 2
            center_y = (rect.top + rect.bottom) / 2
        else:
            center_x = 960
            center_y = 540
        dx = pt.x - center_x
        dy = pt.y - center_y
        dist = max(1.0, (dx*dx + dy*dy)**0.5)
        max_dist = 600.0
        ratio = min(1.0, dist / max_dist)
        norm_x = (dx / dist) * ratio
        norm_y = (dy / dist) * ratio
        return {
            "x": round(norm_x, 3),
            "y": round(norm_y, 3),
            "raw_dx": round(dx, 1),
            "raw_dy": round(dy, 1)
        }

tracker_api = TrackerApi()

# Bottle Application
app = Bottle()

@app.hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Origin, Accept"

@app.route("/static/<filepath:path>")
def serve_static(filepath):
    return static_file(filepath, root=os.path.join(APP_DIR, "static"))

@app.route("/characters/<char_id>/<filepath:path>")
def serve_character_file(char_id, filepath):
    char_dir = os.path.join(CHARACTERS_DIR, char_id)
    return static_file(filepath, root=char_dir)

@app.route("/")
def serve_index():
    p = os.path.join(APP_DIR, "index.html")
    with open(p, "r", encoding="utf-8") as f:
        html = f.read()
    return HTTPResponse(body=html, status=200, headers={"Content-Type": "text/html; charset=utf-8"})

@app.route("/settings")
def serve_settings():
    p = os.path.join(APP_DIR, "settings.html")
    with open(p, "r", encoding="utf-8") as f:
        html = f.read()
    return HTTPResponse(body=html, status=200, headers={"Content-Type": "text/html; charset=utf-8"})

@app.route("/api/health")
def api_health():
    response.content_type = "application/json"
    hwnd_str = hex(tracker_api.hwnd) if tracker_api.hwnd else None
    return json.dumps({"status": "ok", "app": "reZero_live2d", "codex_ready": True, "hwnd": hwnd_str})

@app.route("/api/config", method=["GET", "POST"])
def api_config():
    response.content_type = "application/json"
    if request.method == "POST":
        try:
            req_data = request.json or {}
            cfg = load_config()
            cfg.update(req_data)
            save_config(cfg)
            if main_window:
                try:
                    main_window.evaluate_js(f"window.onConfigUpdated && window.onConfigUpdated({json.dumps(cfg)});")
                except Exception:
                    pass
            return json.dumps({"success": True, "config": cfg})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    return json.dumps(load_config())

@app.route("/api/characters")
def api_characters():
    response.content_type = "application/json"
    chars = char_mgr.list_characters() if char_mgr else []
    return json.dumps({"success": True, "total": len(chars), "characters": chars})

@app.route("/api/character", method=["GET", "POST"])
def api_character():
    response.content_type = "application/json"
    cfg = load_config()
    current_char_id = cfg.get("character", "ac_base_rem01")

    if request.method == "POST":
        data = request.json or {}
        new_char_id = data.get("character")
        if new_char_id and char_mgr and char_mgr.get_character(new_char_id):
            cfg["character"] = new_char_id
            save_config(cfg)
            char_info = char_mgr.get_character(new_char_id)
            if main_window:
                try:
                    main_window.evaluate_js(f"window.loadCharacter && window.loadCharacter('{new_char_id}');")
                except Exception as e:
                    log_msg(f"evaluate_js loadCharacter error: {e}")
            return json.dumps({"success": True, "character": new_char_id, "info": char_info})
        return json.dumps({"success": False, "error": "Invalid character id"})

    char_info = char_mgr.get_character(current_char_id) if char_mgr else None
    return json.dumps({"character": current_char_id, "info": char_info})

@app.route("/api/character_info")
def api_character_info():
    response.content_type = "application/json"
    char_id = request.query.get("id") or load_config().get("character", "ac_base_rem01")
    info = char_mgr.get_character(char_id) if char_mgr else None
    if info:
        return json.dumps({"success": True, "info": info})
    return json.dumps({"success": False, "error": "Character not found"}), 404

@app.route("/api/mouse")
def api_mouse():
    response.content_type = "application/json"
    return json.dumps(tracker_api.get_tracking())

@app.route("/api/toggle_settings", method=["GET", "POST"])
def api_toggle_settings():
    response.content_type = "application/json"
    res = tracker_api.toggle_settings()
    return json.dumps({"success": True, "open": bool(res)})

@app.route("/api/open_settings", method=["GET", "POST"])
def api_open_settings():
    response.content_type = "application/json"
    res = tracker_api.open_settings()
    return json.dumps({"success": True, "open": bool(res)})

@app.route("/api/close_settings", method=["GET", "POST"])
def api_close_settings():
    response.content_type = "application/json"
    res = tracker_api.close_settings()
    return json.dumps({"success": True, "closed": bool(res)})

@app.route("/api/system_stats")
def api_system_stats():
    response.content_type = "application/json"
    cpu, mem = get_system_load()
    return json.dumps({"cpu": cpu, "memory": mem})

# Codex Event Endpoint
@app.route("/api/event", method=["POST"])
@app.route("/api/codex/event", method=["POST"])
def api_codex_event():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        event_type = data.get("event", "success").lower()
        custom_msg = data.get("message")
        char_id = data.get("character") or load_config().get("character", "ac_base_rem01")

        ev_info = CODEX_EVENTS.get(event_type, {
            "emotion": "joy_cheer",
            "default_msg": "코덱스 작업이 완료되었습니다!"
        })

        emo_key = ev_info["emotion"]
        msg = custom_msg or ev_info["default_msg"]

        motion_file = char_mgr.get_motion_for_emotion(char_id, emo_key) if char_mgr else None

        payload = {
            "text": msg,
            "motion": motion_file,
            "emotion": emo_key,
            "character": char_id,
            "source": "codex",
            "event": event_type
        }

        if main_window:
            try:
                main_window.evaluate_js(f"window.playSpeech && window.playSpeech({json.dumps(payload)});")
            except Exception as js_err:
                log_msg(f"evaluate_js event error: {js_err}")

        return json.dumps({"success": True, "payload": payload})
    except Exception as e:
        log_msg(f"api_codex_event error: {e}")
        return json.dumps({"success": False, "error": str(e)})

# Dialogue / Speech Bubble Endpoint
@app.route("/api/speak", method=["POST"])
def api_speak():
    response.content_type = "application/json"
    try:
        data = request.json or {}
        text = data.get("text", "").strip()
        if not text:
            return json.dumps({"success": False, "error": "Empty text"})

        cfg = load_config()
        char_id = data.get("character") or cfg.get("character", "ac_base_rem01")

        # Emotion analysis
        req_emotion = data.get("emotion")
        if req_emotion:
            emo_info = analyze_emotion(f"[{req_emotion}] {text}")
        else:
            emo_info = analyze_emotion(text)

        emo_key = emo_info.get("key", "normal")
        clean_text = emo_info.get("clean_text", text)

        # Motion selection for the current character
        motion_file = None
        if char_mgr:
            motion_file = char_mgr.get_motion_for_emotion(char_id, emo_key)

        payload = {
            "text": clean_text,
            "motion": motion_file,
            "emotion": emo_key,
            "character": char_id
        }

        if main_window:
            try:
                main_window.evaluate_js(f"window.playSpeech && window.playSpeech({json.dumps(payload)});")
            except Exception as js_err:
                log_msg(f"evaluate_js playSpeech error: {js_err}")

        return json.dumps({"success": True, "payload": payload})
    except Exception as e:
        log_msg(f"api_speak error: {traceback.format_exc()}")
        return json.dumps({"success": False, "error": str(e)})

def run_server(port=8990):
    try:
        log_msg(f"Starting Re:Zero Companion server on 127.0.0.1:{port}...")
        app.run(host="127.0.0.1", port=port, quiet=True)
    except Exception as e:
        log_msg(f"run_server() fatal: {traceback.format_exc()}")

def check_already_running(port=8990):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/health")
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass
    return False

if __name__ == "__main__":
    cfg = load_config()
    port = cfg.get("port", 8990)

    # CLI speak client option: python app.py --speak "안녕하세요"
    if len(sys.argv) > 2 and sys.argv[1] == "--speak":
        txt = " ".join(sys.argv[2:])
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/speak",
                data=json.dumps({"text": txt}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=6) as r:
                print(r.read().decode("utf-8"))
        except Exception as e:
            print("Speak command error:", e)
        sys.exit(0)

    if check_already_running(port):
        print("Re:Zero Live2D Companion is already running!")
        sys.exit(0)

    # Start server in background thread
    srv_thread = threading.Thread(target=lambda: run_server(port), daemon=True)
    srv_thread.start()

    win_w = cfg.get("win_w", 320)
    win_h = cfg.get("win_h", 400)
    sw = user32.GetSystemMetrics(0) or 1920
    sh = user32.GetSystemMetrics(1) or 1080
    init_x = max(0, sw - win_w - 30)
    init_y = max(0, sh - win_h - 60)

    main_window = webview.create_window(
        "Re:Zero Live2D Companion",
        url=f"http://127.0.0.1:{port}/?v={int(time.time())}",
        width=win_w,
        height=win_h,
        x=init_x,
        y=init_y,
        frameless=True,
        transparent=True,
        on_top=True,
        background_color="#000000",
        js_api=tracker_api
    )

    def on_window_ready():
        log_msg("on_window_ready triggered")
        try:
            import webview.platforms.winforms as wf
            from System import Action
            import System.Drawing as Drawing

            class MARGINS(ctypes.Structure):
                _fields_ = [
                    ("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)
                ]

            for _ in range(30):
                inst = wf.BrowserView.instances.get(main_window.uid)
                if inst:
                    hwnd = inst.Handle.ToInt64()
                    tracker_api.set_hwnd(hwnd)
                    log_msg(f"Attached hwnd: {hex(hwnd)}")
                    m = MARGINS(-1, -1, -1, -1)
                    ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(m))

                    def _configure_form():
                        inst.BackColor = Drawing.Color.Black
                        if hasattr(inst, 'browser') and hasattr(inst.browser, 'webview'):
                            inst.browser.webview.DefaultBackgroundColor = Drawing.Color.Transparent
                        inst.Show()
                        inst.BringToFront()
                        inst.Activate()

                    try:
                        inst.Invoke(Action(_configure_form))
                        log_msg("Configured transparent form successfully")
                    except Exception as ie:
                        log_msg(f"Invoke show error: {ie}")
                    break
                time.sleep(0.1)
        except Exception as e:
            log_msg(f"on_window_ready error: {traceback.format_exc()}")

        # Initial greeting
        def greeting():
            time.sleep(1.0)
            try:
                curr_info = char_mgr.get_character(cfg.get("character", "ac_base_rem01")) if char_mgr else None
                name = curr_info.get("baseName", "렘") if curr_info else "렘"
                greet_txt = f"안녕하세요! {name}이에요. 코덱스 작업을 시작할 준비가 되었어요!"
                payload = {
                    "text": greet_txt,
                    "character": cfg.get("character", "ac_base_rem01"),
                    "motion": char_mgr.get_motion_for_emotion(cfg.get("character", "ac_base_rem01"), "joy_cheer") if char_mgr else None
                }
                if main_window:
                    main_window.evaluate_js(f"window.playSpeech && window.playSpeech({json.dumps(payload)});")
            except Exception as ge:
                log_msg(f"Greeting error: {ge}")
        threading.Thread(target=greeting, daemon=True).start()

    try:
        webview.start(on_window_ready, storage_path=WV2_STORAGE, private_mode=False)
    except Exception as e:
        log_msg(f"webview.start() exception: {traceback.format_exc()}")
