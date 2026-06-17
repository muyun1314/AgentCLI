# -*- coding: utf-8 -*-
"""
Agent Cli Quick Launch — pywebview + HTML/CSS 版
=================================================
Python 后端 = 业务逻辑 + 系统调用
HTML/CSS/JS 前端 = UI 渲染（web/index.html）
"""
import json
import os
import subprocess
import sys
import ctypes
import logging
import shutil
import urllib.request
import urllib.error
import uuid
import time

# ============================================================
# Constants
# ============================================================
VERSION = "1.0.0"
GITHUB_REPO = "muyun1314/AgentCLI"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "app.log")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# ============================================================
# DPI Awareness
# ============================================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    filename=LOG_FILE, level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# ============================================================
# Config
# ============================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": [], "default_launcher": "Windows Terminal", "theme": "dark", "lang": "zh"}

def save_config(config):
    tmp = CONFIG_FILE + ".tmp." + uuid.uuid4().hex[:8]
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CONFIG_FILE)
    except Exception:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass
        raise

def get_home():
    return os.path.expanduser("~")

def is_wt_installed():
    return os.path.exists(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"))

# ============================================================
# Known Agents
# ============================================================
KNOWN_AGENTS = {
    "mimo": {"name": "MiMo", "type": "npm", "pkg": "@mimo-ai/cli",
             "official": "npm install -g @mimo-ai/cli",
             "mirror": "npm install -g --registry=https://registry.npmmirror.com @mimo-ai/cli",
             "config": f"{get_home()}\\.config\\mimocode", "uninstall": "npm uninstall -g @mimo-ai/cli"},
    "claude": {"name": "Claude", "type": "npm", "pkg": "@anthropic-ai/claude-code",
               "official": "npm install -g @anthropic-ai/claude-code",
               "mirror": "npm install -g --registry=https://registry.npmmirror.com @anthropic-ai/claude-code",
               "config": f"{get_home()}\\.claude", "uninstall": "npm uninstall -g @anthropic-ai/claude-code"},
    "codex": {"name": "Codex", "type": "npm", "pkg": "@openai/codex",
              "official": "npm install -g @openai/codex",
              "mirror": "npm install -g --registry=https://registry.npmmirror.com @openai/codex",
              "config": f"{get_home()}\\.codex\\config.toml", "uninstall": "npm uninstall -g @openai/codex"},
    "deveco": {"name": "Deveco", "type": "npm", "pkg": "@deveco/deveco-code",
               "official": "npm install -g @deveco/deveco-code",
               "mirror": "npm install -g --registry=https://registry.npmmirror.com @deveco/deveco-code",
               "config": f"{get_home()}\\.config\\deveco", "uninstall": "npm uninstall -g @deveco/deveco-code"},
    "copilot": {"name": "Copilot", "type": "npm", "pkg": "@github/copilot",
                "official": "npm install -g @github/copilot",
                "mirror": "npm install -g --registry=https://registry.npmmirror.com @github/copilot",
                "config": f"{get_home()}\\.copilot", "uninstall": "npm uninstall -g @github/copilot"},
    "aider": {"name": "Aider", "type": "pip", "pkg": "aider-chat",
              "official": "pip install aider-chat",
              "mirror": "pip install aider-chat -i https://pypi.tuna.tsinghua.edu.cn/simple",
              "config": f"{get_home()}\\.aider.conf.yml", "uninstall": "pip uninstall aider-chat -y"},
    "cn": {"name": "Continue", "type": "npm", "pkg": "@continuedev/cli",
           "official": "npm install -g @continuedev/cli",
           "mirror": "npm install -g --registry=https://registry.npmmirror.com @continuedev/cli",
           "config": f"{get_home()}\\.continue", "uninstall": "npm uninstall -g @continuedev/cli"},
    "cursor": {"name": "Cursor", "type": "winget", "pkg": "Cursor.Cursor",
               "official": "winget install Cursor.Cursor", "mirror": "",
               "config": f"{get_home()}\\.cursor", "uninstall": "winget uninstall Cursor.Cursor"},
    "windsurf": {"name": "Windsurf", "type": "winget", "pkg": "Codeium.Windsurf",
                 "official": "winget install Codeium.Windsurf", "mirror": "",
                 "config": f"{get_home()}\\.windsurf", "uninstall": "winget uninstall Codeium.Windsurf"},
    "cline": {"name": "Cline", "type": "npm", "pkg": "cline",
              "official": "npm install -g cline",
              "mirror": "npm install -g --registry=https://registry.npmmirror.com cline",
              "config": f"{get_home()}\\.cline", "uninstall": "npm uninstall -g cline"},
}

CMD_ALIAS = {"continue": "cn"}
_WINGET_DETECT_CACHE = None

def _get_winget_installed():
    global _WINGET_DETECT_CACHE
    if _WINGET_DETECT_CACHE is not None:
        return _WINGET_DETECT_CACHE
    result = set()
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    try:
        import winreg
        for reg_path in reg_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                        name, _ = winreg.QueryValueEx(sub, "DisplayName")
                        if name:
                            result.add(name.lower())
                        winreg.CloseKey(sub)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                pass
    except Exception:
        pass
    _WINGET_DETECT_CACHE = result
    return result

def _clear_winget_cache():
    global _WINGET_DETECT_CACHE
    _WINGET_DETECT_CACHE = None

def is_agent_installed(cmd, agent_type="npm"):
    if agent_type == "winget":
        pkg = KNOWN_AGENTS.get(cmd, {}).get("pkg", "")
        return bool(pkg and pkg.lower() in _get_winget_installed())
    if agent_type == "npm":
        if shutil.which(cmd) is not None:
            return True
        pkg = KNOWN_AGENTS.get(cmd, {}).get("pkg", "")
        if pkg:
            try:
                r = subprocess.run(
                    ["npm", "list", "-g", pkg, "--depth=0"],
                    capture_output=True, text=True, timeout=5
                )
                if r.returncode == 0 and pkg in r.stdout:
                    return True
            except Exception:
                pass
        return False
    return shutil.which(cmd) is not None

def resolve_cmd(cmd):
    return CMD_ALIAS.get(cmd, cmd)


# ============================================================
# Launch
# ============================================================
def open_launcher(command, launcher="Windows Terminal", title=""):
    try:
        if launcher == "Windows Terminal":
            wt_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe")
            if not os.path.exists(wt_path):
                return {"error": "Windows Terminal 未安装"}
            subprocess.Popen([wt_path, "-w", "new-window", "--suppressApplicationTitle",
                              "--title", title, "cmd", "/k", command])
        elif launcher == "PowerShell":
            subprocess.Popen(["powershell.exe", "-NoExit", "-Command", command],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # CMD
            import tempfile
            fd, bat_path = tempfile.mkstemp(suffix=".bat", prefix="launch_")
            os.close(fd)
            script = (
                f'@echo off\r\ntitle {title}\r\n'
                f'{command}\r\n'
            )
            with open(bat_path, "w", encoding="gbk", newline="") as f:
                f.write(script)
            subprocess.Popen(["cmd.exe", "/k", bat_path],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        return {"success": True}
    except Exception as e:
        logging.error("启动失败: %s", e)
        return {"error": str(e)}


# ============================================================
# GitHub Update
# ============================================================
def check_github_update():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("tag_name", "").lstrip("v"), data.get("html_url", "")
    except Exception:
        return None, None


# ============================================================
# API Class — exposed to JavaScript via pywebview
# ============================================================
class AgentApi:
    def __init__(self):
        self.config = load_config()
        self._auto_detect_all()

    def _auto_detect_all(self):
        """检测所有已知 agent 的安装状态"""
        _clear_winget_cache()

    def _get_agents_status(self):
        """返回所有 known agents 及其安装状态"""
        result = {}
        for cmd, info in KNOWN_AGENTS.items():
            data = dict(info)
            data["installed"] = is_agent_installed(cmd, info.get("type", "npm"))
            result[cmd] = data
        return result

    # ── Config ──
    def get_config(self):
        return self.config

    def get_version(self):
        return VERSION

    def get_known_agents(self):
        return self._get_agents_status()

    def is_wt_installed(self):
        return is_wt_installed()

    def set_default_launcher(self, launcher):
        if launcher in ("Windows Terminal", "PowerShell", "CMD"):
            self.config["default_launcher"] = launcher
            save_config(self.config)

    def save_settings(self, theme, lang):
        self.config["theme"] = theme
        self.config["lang"] = lang
        save_config(self.config)

    def open_url(self, url):
        try:
            os.startfile(url)
        except Exception:
            pass

    def check_update(self):
        ver, url = check_github_update()
        if ver and ver != VERSION:
            return {"version": ver, "url": url}
        return {"version": None, "url": None}

    # ── Project CRUD ──
    def add_project(self, name, command):
        self.config["projects"].append({"name": name.strip(), "command": command.strip()})
        save_config(self.config)
        return self.config

    def edit_project(self, idx, name, command):
        if 0 <= idx < len(self.config["projects"]):
            self.config["projects"][idx] = {"name": name.strip(), "command": command.strip()}
            save_config(self.config)
        return self.config

    def delete_project(self, idx):
        if 0 <= idx < len(self.config["projects"]):
            del self.config["projects"][idx]
            save_config(self.config)
        return self.config

    def move_up(self, idx):
        if 0 < idx < len(self.config["projects"]):
            p = self.config["projects"]
            p[idx], p[idx - 1] = p[idx - 1], p[idx]
            save_config(self.config)
        return self.config

    def move_down(self, idx):
        if 0 <= idx < len(self.config["projects"]) - 1:
            p = self.config["projects"]
            p[idx], p[idx + 1] = p[idx + 1], p[idx]
            save_config(self.config)
        return self.config

    # ── Run ──
    def run_project(self, idx):
        if 0 <= idx < len(self.config["projects"]):
            p = self.config["projects"][idx]
            launcher = self.config.get("default_launcher", "Windows Terminal")
            result = open_launcher(p["command"], launcher, p["name"])
            if result.get("error"):
                return {"error": result["error"]}
        return {"success": True}

    # ── Detect ──
    def detect(self):
        _clear_winget_cache()
        existing = {resolve_cmd(p["command"].split()[0].lower()) for p in self.config["projects"]}
        remaining, removed = [], []
        for p in self.config["projects"]:
            cmd_name = resolve_cmd(p["command"].lower())
            agent_type = KNOWN_AGENTS.get(cmd_name, {}).get("type", "npm")
            if is_agent_installed(cmd_name, agent_type):
                remaining.append(p)
            else:
                removed.append(p["name"])
        self.config["projects"] = remaining

        found = []
        agents_map = {"mimo": "mimo", "claude": "claude", "codex": "codex",
                      "deveco": "deveco", "copilot": "copilot", "aider": "aider",
                      "cn": "cn", "cursor": "cursor", "windsurf": "windsurf", "cline": "cline"}
        for key, binary in agents_map.items():
            agent_type = KNOWN_AGENTS.get(key, {}).get("type", "npm")
            if is_agent_installed(binary, agent_type):
                name = KNOWN_AGENTS[key]["name"]
                if key not in existing:
                    found.append({"name": name, "command": binary})

        self.config["projects"].extend(found)
        save_config(self.config)
        return self.config

    # ── Config / Folder / Uninstall ──
    def open_config(self, idx):
        if 0 <= idx < len(self.config["projects"]):
            p = self.config["projects"][idx]
            cmd = resolve_cmd(p["command"].split()[0].lower())
            if cmd in KNOWN_AGENTS:
                cp = os.path.expandvars(KNOWN_AGENTS[cmd]["config"])
                if os.path.isfile(cp):
                    os.startfile(cp)
                elif os.path.isdir(cp):
                    for f in os.listdir(cp):
                        if f.endswith((".json", ".yml", ".yaml", ".toml", ".conf")):
                            os.startfile(os.path.join(cp, f))
                            return
                    os.startfile(cp)

    def open_config_folder(self, idx):
        if 0 <= idx < len(self.config["projects"]):
            p = self.config["projects"][idx]
            cmd = resolve_cmd(p["command"].split()[0].lower())
            if cmd in KNOWN_AGENTS:
                cp = os.path.expandvars(KNOWN_AGENTS[cmd]["config"])
                if os.path.exists(cp):
                    os.startfile(cp if os.path.isdir(cp) else os.path.dirname(cp))
                else:
                    os.startfile(get_home())
            else:
                os.startfile(get_home())

    def uninstall_project(self, idx):
        if 0 <= idx < len(self.config["projects"]):
            p = self.config["projects"][idx]
            cmd = resolve_cmd(p["command"].split()[0].lower())
            if cmd in KNOWN_AGENTS:
                agent_type = KNOWN_AGENTS[cmd].get("type", "npm")
                if not is_agent_installed(cmd, agent_type):
                    return {"error": "未安装"}
                uninst = KNOWN_AGENTS[cmd]["uninstall"]
                subprocess.Popen(["cmd", "/c", uninst],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)

    # ── Install ──
    def install_wt(self):
        try:
            os.startfile("ms-windows-store://pdp/?ProductId=9N0DX20HK701")
        except Exception:
            try:
                subprocess.Popen(["cmd", "/c", "start ms-windows-store://pdp/?ProductId=9N0DX20HK701"])
            except Exception:
                pass

    def install_agent(self, cmd, source="official"):
        if cmd not in KNOWN_AGENTS:
            return {"error": "Unknown agent"}
        agent_type = KNOWN_AGENTS[cmd].get("type", "npm")
        if is_agent_installed(cmd, agent_type):
            return {"error": "Already installed"}
        ic = KNOWN_AGENTS[cmd][source]
        try:
            if ic.startswith("pip"):
                subprocess.Popen(["powershell.exe", "-NoExit", "-Command", ic],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                uid = uuid.uuid4().hex[:8]
                bp = os.path.join(os.environ.get("TEMP", "."), f"install_temp_{uid}.bat")
                with open(bp, "w", encoding="gbk", newline="") as f:
                    f.write(f'@echo off\r\n{ic}\r\n')
                subprocess.Popen(["cmd.exe", "/k", bp],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            _clear_winget_cache()
            return {"success": True}
        except Exception as e:
            logging.error("安装 %s 失败: %s", cmd, e)
            return {"error": str(e)}

    def copy_command(self, cmd, source):
        """Copy install command to clipboard"""
        if cmd in KNOWN_AGENTS:
            text = KNOWN_AGENTS[cmd][source]
            try:
                subprocess.run(["clip"], input=text.encode("utf-8"), check=False)
            except Exception:
                pass
            return True
        return False


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    import webview, threading
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    api = AgentApi()

    # Start a local HTTP server to serve web/ directory (logo.png etc.)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.join(BASE_DIR, "web"), **kwargs)

    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]

    def run_server():
        server.serve_forever()
    threading.Thread(target=run_server, daemon=True).start()

    window = webview.create_window(
        title="AgentCLI",
        url=f"http://127.0.0.1:{port}/index.html",
        js_api=api,
        width=860,
        height=620,
        min_size=(620, 480),
    )

    # Set window/taskbar icon via process icon (inherited by all windows)
    try:
        ico = os.path.join(BASE_DIR, "logo", "logo.ico")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AgentCLI")
        # Enumerate windows in a loop with retries
        def _set_icon():
            import time
            result = []  # mutable container for found hwnd
            for _ in range(20):  # retry for ~10 seconds
                time.sleep(0.5)
                result.clear()
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
                def _enum_cb(h, _):
                    buf = ctypes.create_unicode_buffer(256)
                    ctypes.windll.user32.GetWindowTextW(h, buf, 256)
                    if "AgentCLI" in buf.value:
                        result.append(h)
                        return False
                    return True
                ctypes.windll.user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)
                if result:
                    hwnd = result[0]
                    WM_SETICON = 0x0080
                    hicon = ctypes.windll.user32.LoadImageW(None, ico, 1, 0, 0, 0x00000010|0x00000020)
                    if hicon:
                        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)
                        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)
                    break
        import threading
        threading.Thread(target=_set_icon, daemon=True).start()
    except Exception:
        pass

    webview.start()
    server.shutdown()
