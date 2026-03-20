import os
import sys
import json
import math
import copy
import PyQt5
import winsound
import keyboard

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QColorDialog, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPalette, QKeySequence

dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'Qt5', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

CONFIG_FILE = "config.json"
DEFAULT_SETTINGS = {
    'ball_pos_x': 200, 'ball_pos_y': 200,
    'reflect_pos_x': 500, 'reflect_pos_y': 100,
    'ball_radius': 12, 'reflect_radius': 7,
    'line_width_aim': 1, 'line_width_reflect': 2,
    'bg_opacity': 150,
    'color_ball_outer': "#FFFFFF", 'color_ball_inner': "#FFFFFF",
    'color_aim': "#00FF7F", 'color_reflect_dot': "#78C8FF78",
    'color_reflect_line': "#00FFFF", 'color_ui_border': "#B400AAFF",
    'color_pocket': "#FF0000", 'color_pocket_border': "#FFFFFF",
    'lang': 'th',
    'hotkeys': {
        'toggle_lock': 'insert', 'exit': 'end',
        'save': 'f5', 'lang': 'f9', 'settings': 'f2'
    }
}

LANG = {
    'en': {
        'title': "Program Settings", 'close': "X",
        'sec_ball': "Cue Ball", 'rad': "Radius:", 'out_col': "Outer Color:", 'in_col': "Inner Color:", 'aim_w': "Aim Line Width:", 'aim_col': "Aim Line Color:",
        'sec_ref': "Reflection", 'ref_rad': "Point Radius:", 'ref_col': "Point Color:", 'ref_w': "Line Width:", 'ref_lcol': "Line Color:",
        'sec_ui': "Overlay UI", 'bg_op': "BG Opacity:", 'bd_col': "Border Color:", 'pk_col': "Pocket Color:", 'pk_bd_col': "Pocket Border:",
        'sec_key': "Hotkeys", 'k_lock': "Lock/Unlock:", 'k_save': "Save Settings:", 'k_lang': "Change Lang:", 'k_set': "Settings UI:", 'k_exit': "Exit Program:",
        'btn_reset': "Reset to Defaults",
        'ov_locked': "LOCKED", 'ov_edit': "EDITING MODE", 'ov_lock': "Lock", 'ov_set': "Settings", 'ov_save': "Save", 'ov_exit': "Exit"
    },
    'th': {
        'title': "ตั้งค่าโปรแกรม", 'close': "ปิด",
        'sec_ball': "ลูกขาว (Cue Ball)", 'rad': "รัศมี:", 'out_col': "สีขอบนอก:", 'in_col': "สีจุดกลาง:", 'aim_w': "ขนาดเส้นเล็ง:", 'aim_col': "สีเส้นเล็ง:",
        'sec_ref': "เส้นสะท้อน (Reflection)", 'ref_rad': "รัศมีจุดสะท้อน:", 'ref_col': "สีจุดสะท้อน:", 'ref_w': "ขนาดเส้นสะท้อน:", 'ref_lcol': "สีเส้นสะท้อน:",
        'sec_ui': "หน้าจอ (Overlay UI)", 'bg_op': "ความใสพื้นหลัง:", 'bd_col': "สีขอบโต๊ะ:", 'pk_col': "สีหลุม:", 'pk_bd_col': "สีขอบหลุม:",
        'sec_key': "คีย์ลัด (Hotkeys)", 'k_lock': "ล็อค/ปลดล็อค:", 'k_save': "บันทึกการตั้งค่า:", 'k_lang': "เปลี่ยนภาษา:", 'k_set': "เปิดตั้งค่า:", 'k_exit': "ปิดโปรแกรม:",
        'btn_reset': "คืนค่าเริ่มต้น (Reset)",
        'ov_locked': "ล็อคแล้ว (LOCKED)", 'ov_edit': "โหมดแก้ไข (EDITING)", 'ov_lock': "ล็อค", 'ov_set': "ตั้งค่า", 'ov_save': "บันทึก", 'ov_exit': "ปิด"
    }
}

class HotkeySignaler(QObject):
    toggle_signal = pyqtSignal()
    exit_signal = pyqtSignal()
    save_signal = pyqtSignal()
    lang_signal = pyqtSignal()
    settings_signal = pyqtSignal()

class HotkeyManager:
    def __init__(self, signaler):
        self.signaler = signaler
        self.hotkeys = copy.deepcopy(DEFAULT_SETTINGS['hotkeys'])

    def load_from_config(self, data):
        if 'hotkeys' in data:
            self.hotkeys.update(data['hotkeys'])
        self.register_all()

    def register_all(self):
        keyboard.unhook_all()
        try:
            keyboard.add_hotkey(self.hotkeys['toggle_lock'], self.signaler.toggle_signal.emit)
            keyboard.add_hotkey(self.hotkeys['exit'], self.signaler.exit_signal.emit)
            keyboard.add_hotkey(self.hotkeys['save'], self.signaler.save_signal.emit)
            keyboard.add_hotkey(self.hotkeys['lang'], self.signaler.lang_signal.emit)
            keyboard.add_hotkey(self.hotkeys['settings'], self.signaler.settings_signal.emit)
        except Exception as e:
            print(f"Error registering hotkeys: {e}")

    def get_data(self):
        return self.hotkeys

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setStyleSheet("""
            QPushButton { background-color: #303030; color: #CCCCCC; border: 1px solid #3A3A3A; padding: 5px; text-align: left; font-weight: bold; }
            QPushButton:checked { background-color: #3A3A3A; color: white; }
            QPushButton:hover { background-color: #404040; }
        """)
        self.toggle_button.toggled.connect(self.on_toggle)
        self.layout.addWidget(self.toggle_button)

        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("QFrame { background-color: #252525; border: 1px solid #3A3A3A; border-top: none; }")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(5)
        self.layout.addWidget(self.content_frame)

    def on_toggle(self, checked):
        self.content_frame.setVisible(checked)

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)

class KeyBindButton(QPushButton):
    key_changed = pyqtSignal(str)
    def __init__(self, key_name, parent=None):
        super().__init__(key_name.upper(), parent)
        self.key_name = key_name
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton { background-color: #202020; color: #00AAFF; border: 1px solid #3A3A3A; padding: 5px; }
            QPushButton:checked { background-color: #004466; color: white; }
            QPushButton:hover { background-color: #2A2A2A; }
        """)

    def keyPressEvent(self, event):
        if self.isChecked():
            key = event.key()
            if key == Qt.Key_Escape:
                self.setChecked(False)
                self.setText(self.key_name.upper())
                return

            key_str = QKeySequence(key).toString().lower()
            if not key_str: 
                return
            
            special_keys = {
                Qt.Key_Insert: 'insert', Qt.Key_End: 'end', Qt.Key_F1: 'f1', Qt.Key_F2: 'f2',
                Qt.Key_F3: 'f3', Qt.Key_F4: 'f4', Qt.Key_F5: 'f5', Qt.Key_F6: 'f6',
                Qt.Key_F7: 'f7', Qt.Key_F8: 'f8', Qt.Key_F9: 'f9', Qt.Key_F10: 'f10',
                Qt.Key_F11: 'f11', Qt.Key_F12: 'f12', Qt.Key_Delete: 'delete',
                Qt.Key_Home: 'home', Qt.Key_PageUp: 'page up', Qt.Key_PageDown: 'page down'
            }
            if key in special_keys: key_str = special_keys[key]
            self.key_changed.emit(key_str)
            self.setText(key_str.upper())
            self.setChecked(False)
        else:
            super().keyPressEvent(event)

class SettingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_w = main_window
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(350, 650)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        title_bar = QFrame()
        title_bar.setStyleSheet("background-color: #3A3A3A; color: white; border-bottom: 1px solid #202020;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 2, 10, 2)

        self.title_label = QLabel()
        self.title_label.setFont(QFont("Tahoma", 9, QFont.Bold))
        title_layout.addWidget(self.title_label)

        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(30, 20)
        self.close_btn.setStyleSheet("background:none; border:none; color: #888; font-weight:bold;")
        self.close_btn.clicked.connect(self.hide)
        title_layout.addWidget(self.close_btn)

        self.main_layout.addWidget(title_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background-color: #1A1A1A; }")
        self.main_layout.addWidget(self.scroll)

        self.rebuild_ui() 

    def rebuild_ui(self):
        if hasattr(self, 'content_widget'):
            self.content_widget.deleteLater()

        lang_code = self.main_w.settings['lang']
        t = LANG[lang_code]

        self.title_label.setText(t['title'])
        self.close_btn.setText(t['close'] if lang_code == 'th' else "X")
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #1A1A1A; color: #CCCCCC;")
        self.v_layout = QVBoxLayout(self.content_widget)
        self.v_layout.setContentsMargins(10, 10, 10, 10)
        self.v_layout.setSpacing(10)

        sec_ball = CollapsibleSection(t['sec_ball'])
        self.v_layout.addWidget(sec_ball)
        self.create_slider(sec_ball, t['rad'], 5, 30, self.main_w.settings['ball_radius'], lambda v: self.main_w.update_setting('ball_radius', v))
        self.create_color_picker(sec_ball, t['out_col'], 'color_ball_outer', self.main_w.settings['color_ball_outer'])
        self.create_color_picker(sec_ball, t['in_col'], 'color_ball_inner', self.main_w.settings['color_ball_inner'])
        self.create_slider(sec_ball, t['aim_w'], 1, 5, self.main_w.settings['line_width_aim'], lambda v: self.main_w.update_setting('line_width_aim', v))
        self.create_color_picker(sec_ball, t['aim_col'], 'color_aim', self.main_w.settings['color_aim'])

        sec_reflect = CollapsibleSection(t['sec_ref'])
        self.v_layout.addWidget(sec_reflect)
        self.create_slider(sec_reflect, t['ref_rad'], 3, 15, self.main_w.settings['reflect_radius'], lambda v: self.main_w.update_setting('reflect_radius', v))
        self.create_color_picker(sec_reflect, t['ref_col'], 'color_reflect_dot', self.main_w.settings['color_reflect_dot'])
        self.create_slider(sec_reflect, t['ref_w'], 1, 5, self.main_w.settings['line_width_reflect'], lambda v: self.main_w.update_setting('line_width_reflect', v))
        self.create_color_picker(sec_reflect, t['ref_lcol'], 'color_reflect_line', self.main_w.settings['color_reflect_line'])

        sec_ui = CollapsibleSection(t['sec_ui'])
        self.v_layout.addWidget(sec_ui)
        self.create_slider(sec_ui, t['bg_op'], 0, 255, self.main_w.settings['bg_opacity'], lambda v: self.main_w.update_setting('bg_opacity', v))
        self.create_color_picker(sec_ui, t['bd_col'], 'color_ui_border', self.main_w.settings['color_ui_border'])
        self.create_color_picker(sec_ui, t['pk_col'], 'color_pocket', self.main_w.settings['color_pocket'])
        self.create_color_picker(sec_ui, t['pk_bd_col'], 'color_pocket_border', self.main_w.settings['color_pocket_border'])

        sec_keys = CollapsibleSection(t['sec_key'])
        self.v_layout.addWidget(sec_keys)
        self.create_keybind(sec_keys, t['k_lock'], 'toggle_lock')
        self.create_keybind(sec_keys, t['k_save'], 'save')
        self.create_keybind(sec_keys, t['k_lang'], 'lang')
        self.create_keybind(sec_keys, t['k_set'], 'settings')
        self.create_keybind(sec_keys, t['k_exit'], 'exit')
        self.v_layout.addSpacing(10)
        reset_btn = QPushButton(t['btn_reset'])
        reset_btn.setStyleSheet("""
            QPushButton { background-color: #8B0000; color: white; border: 1px solid #FF0000; padding: 8px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #FF0000; }
        """)
        reset_btn.clicked.connect(self.main_w.reset_to_defaults)
        self.v_layout.addWidget(reset_btn)
        self.v_layout.addStretch()
        self.scroll.setWidget(self.content_widget)

    def create_slider(self, section, label, min_v, max_v, curr_v, callback):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setMinimumWidth(120)
        lbl.setStyleSheet("border: none; background: none;")
        layout.addWidget(lbl)

        val_lbl = QLabel(str(curr_v))
        val_lbl.setMinimumWidth(25)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet("color: #00AAFF; font-weight: bold; border: none; background: none;")
        layout.addWidget(val_lbl)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(curr_v)
        slider.setStyleSheet("""
            QSlider::groove:horizontal { border: 1px solid #3A3A3A; height: 6px; background: #202020; margin: 2px 0; }
            QSlider::handle:horizontal { background: #00AAFF; border: 1px solid #00AAFF; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
            QSlider::handle:horizontal:hover { background: white; border-color: white; }
        """)
        slider.valueChanged.connect(callback)
        slider.valueChanged.connect(lambda v: val_lbl.setText(str(v)))
        layout.addWidget(slider)
        section.addWidget(row)

    def create_color_picker(self, section, label, setting_key, curr_color):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setStyleSheet("border: none; background: none;")
        layout.addWidget(lbl)

        color_btn = QPushButton()
        color_btn.setFixedSize(60, 22)
        color_btn.setStyleSheet(f"background-color: {curr_color}; border: 1px solid #3A3A3A;")

        def pick_color():
            color = QColorDialog.getColor(QColor(self.main_w.settings[setting_key]), self, "Select Color", QColorDialog.ShowAlphaChannel)
            if color.isValid():
                hex_color = color.name(QColor.HexArgb)
                color_btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #3A3A3A;")
                self.main_w.update_setting(setting_key, hex_color)

        color_btn.clicked.connect(pick_color)
        layout.addWidget(color_btn)
        section.addWidget(row)

    def create_keybind(self, section, label, hotkey_key):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setStyleSheet("border: none; background: none;")
        layout.addWidget(lbl)

        curr_key = self.main_w.hotkey_manager.hotkeys[hotkey_key]
        bind_btn = KeyBindButton(curr_key)

        def change_key(new_key):
            for k, v in self.main_w.hotkey_manager.hotkeys.items():
                if v == new_key and k != hotkey_key:
                    bind_btn.setText(curr_key.upper())
                    return
            self.main_w.hotkey_manager.hotkeys[hotkey_key] = new_key
            self.main_w.hotkey_manager.register_all()

        bind_btn.key_changed.connect(change_key)
        layout.addWidget(bind_btn)
        section.addWidget(row)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(26, 26, 26, 240))
        painter.setPen(QPen(QColor(58, 58, 58), 1))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

class PoolGuidelineGlobal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.default_geometry = (100, 100, 1000, 500)

        self.is_locked = False
        self.table_padding = 25 
        self.dragging_ball = False
        self.dragging_reflect = False
        self.dragging_window = False
        self.resizing = False
        self.offset = QPoint()

        self.settings = copy.deepcopy(DEFAULT_SETTINGS)
        self.ball_pos = QPoint(200, 200)
        self.reflect_pos = QPoint(500, 100)

        self.signaler = HotkeySignaler()
        self.hotkey_manager = HotkeyManager(self.signaler)

        self.signaler.toggle_signal.connect(self.toggle_lock)
        self.signaler.exit_signal.connect(self.close_and_save)
        self.signaler.save_signal.connect(self.save_settings_with_sound)
        self.signaler.lang_signal.connect(self.toggle_language)
        self.signaler.settings_signal.connect(self.toggle_settings_ui)

        self.load_settings()
        self.settings_ui = SettingsWindow(self)

    def reset_to_defaults(self):
        curr_x, curr_y, curr_w, curr_h = self.x(), self.y(), self.width(), self.height()
        self.settings = copy.deepcopy(DEFAULT_SETTINGS)
        self.settings.update({'x': curr_x, 'y': curr_y, 'w': curr_w, 'h': curr_h})
        self.ball_pos = QPoint(self.settings['ball_pos_x'], self.settings['ball_pos_y'])
        self.reflect_pos = QPoint(self.settings['reflect_pos_x'], self.settings['reflect_pos_y'])
        self.hotkey_manager.hotkeys = copy.deepcopy(self.settings['hotkeys'])
        self.hotkey_manager.register_all()
        self.settings_ui.rebuild_ui()
        self.save_settings()
        self.update()
        winsound.Beep(1000, 150) 

    def update_setting(self, key, value):
        self.settings[key] = value
        self.update()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.settings.update(data) 
                    self.setGeometry(self.settings.get('x', 100), self.settings.get('y', 100), 
                                     self.settings.get('w', 1000), self.settings.get('h', 500))
                    self.ball_pos = QPoint(self.settings['ball_pos_x'], self.settings['ball_pos_y'])
                    self.reflect_pos = QPoint(self.settings['reflect_pos_x'], self.settings['reflect_pos_y'])
                    self.hotkey_manager.load_from_config(self.settings)
            except Exception:
                self.setGeometry(*self.default_geometry)
                self.hotkey_manager.register_all()
        else:
            self.setGeometry(*self.default_geometry)
            self.hotkey_manager.register_all()

    def save_settings(self):
        self.settings.update({
            'x': self.x(), 'y': self.y(),
            'w': self.width(), 'h': self.height(),
            'ball_pos_x': self.ball_pos.x(), 'ball_pos_y': self.ball_pos.y(),
            'reflect_pos_x': self.reflect_pos.x(), 'reflect_pos_y': self.reflect_pos.y(),
            'hotkeys': self.hotkey_manager.get_data()
        })
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e: print(e)

    def save_settings_with_sound(self):
        self.save_settings()
        try: winsound.Beep(1500, 100)
        except: pass

    def toggle_language(self):
        new_lang = 'en' if self.settings['lang'] == 'th' else 'th'
        self.settings['lang'] = new_lang
        self.settings_ui.rebuild_ui() 

        self.update()

    def close_and_save(self):
        self.settings_ui.close()
        self.save_settings()
        self.close()

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.save_settings()
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowTransparentForInput)
        self.show()
        self.update()

    def toggle_settings_ui(self):
        if self.is_locked: return 
        if self.settings_ui.isVisible():
            self.settings_ui.hide()
        else:
            self.settings_ui.move(self.x() + self.width(), self.y())
            self.settings_ui.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        playable_rect = QRect(self.table_padding, self.table_padding + 25, w - (self.table_padding * 2), h - (self.table_padding * 2) - 15)
        opacity = 30 if self.is_locked else self.settings['bg_opacity']
        painter.setBrush(QColor(20, 20, 20, opacity))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 10, 10)
        border_color = QColor(self.settings['color_ui_border'])
        if self.is_locked: border_color.setAlpha(50)
        painter.setPen(QPen(border_color, 1, Qt.SolidLine))
        painter.drawRect(playable_rect)
        left, right = playable_rect.left(), playable_rect.right()
        top, bottom = playable_rect.top(), playable_rect.bottom()
        corner_offset = self.settings['ball_radius'] + 2 
        side_offset_y = self.settings['ball_radius'] - 2 
        mid_x = w // 2
        pockets = [
            QPoint(left + corner_offset, top + corner_offset), QPoint(mid_x, top + side_offset_y),
            QPoint(right - corner_offset, top + corner_offset), QPoint(left + corner_offset, bottom - corner_offset),
            QPoint(mid_x, bottom - side_offset_y), QPoint(right - corner_offset, bottom - corner_offset)
        ]

        line_alpha = 180 if self.is_locked else 100
        aim_color, pocket_color, pocket_border_color = QColor(self.settings['color_aim']), QColor(self.settings['color_pocket']), QColor(self.settings['color_pocket_border'])
        aim_color.setAlpha(line_alpha); pocket_color.setAlpha(line_alpha); pocket_border_color.setAlpha(line_alpha)

        for p in pockets:
            painter.setBrush(pocket_color)
            painter.setPen(QPen(pocket_border_color, 1))
            painter.drawEllipse(p, 6, 6) 
            painter.setPen(QPen(aim_color, self.settings['line_width_aim'], Qt.SolidLine))
            painter.drawLine(self.ball_pos, p)

            dx, dy = p.x() - self.ball_pos.x(), p.y() - self.ball_pos.y()
            angle = math.atan2(dy, dx)
            ball_r = self.settings['ball_radius']
            offset_x, offset_y = math.sin(angle) * ball_r, math.cos(angle) * ball_r

            tangent_col = pocket_border_color
            tangent_col.setAlpha(max(0, line_alpha - 50))
            painter.setPen(QPen(tangent_col, 1))
            painter.drawLine(int(self.ball_pos.x() + offset_x), int(self.ball_pos.y() - offset_y), int(p.x() + offset_x), int(p.y() - offset_y))
            painter.drawLine(int(self.ball_pos.x() - offset_x), int(self.ball_pos.y() + offset_y), int(p.x() - offset_x), int(p.y() + offset_y))

        reflect_x, reflect_y = max(left, min(self.reflect_pos.x(), right)), max(top, min(self.reflect_pos.y(), bottom))
        dists = {'left': abs(reflect_x - left), 'right': abs(reflect_x - right), 'top': abs(reflect_y - top), 'bottom': abs(reflect_y - bottom)}
        edge = min(dists, key=dists.get)
        if edge == 'left': reflect_x = left
        elif edge == 'right': reflect_x = right
        elif edge == 'top': reflect_y = top
        else: reflect_y = bottom
        self.reflect_pos = QPoint(reflect_x, reflect_y)

        aim_col_reflect = QColor(self.settings['color_aim'])
        if self.is_locked: aim_col_reflect.setAlpha(220)
        painter.setPen(QPen(aim_col_reflect, self.settings['line_width_aim'], Qt.SolidLine))
        painter.drawLine(self.ball_pos, self.reflect_pos)
        self.draw_reflection_line(painter, reflect_x, reflect_y, edge, playable_rect)

        dot_color = QColor(self.settings['color_reflect_dot']) 
        painter.setBrush(dot_color)
        p_border_col = QColor("#CCFFFFFF") 
        p_border_col.setAlpha(200)
        painter.setPen(QPen(p_border_col, 0.8))
        painter.drawEllipse(self.reflect_pos, self.settings['reflect_radius'], self.settings['reflect_radius'])

        painter.setBrush(Qt.NoBrush)
        ball_r, ball_col_outer = self.settings['ball_radius'], QColor(self.settings['color_ball_outer'])
        painter.setPen(QPen(ball_col_outer, 2))
        painter.drawEllipse(self.ball_pos, ball_r, ball_r)

        ball_col_inner = QColor(self.settings['color_ball_inner'])
        painter.setBrush(ball_col_inner)
        painter.drawEllipse(self.ball_pos, 2, 2)

        painter.setPen(Qt.NoPen)
        self.draw_info_text(painter, w, h)

    def draw_reflection_line(self, painter, reflect_x, reflect_y, edge, playable_rect):
        vx, vy = reflect_x - self.ball_pos.x(), reflect_y - self.ball_pos.y()
        if vx == 0 and vy == 0: return
        nx, ny = 0, 0
        if edge == 'left': nx, ny = -1, 0
        elif edge == 'right': nx, ny = 1, 0
        elif edge == 'top': nx, ny = 0, -1
        else: nx, ny = 0, 1
        dot = vx * nx + vy * ny
        rvx, rvy = vx - 2 * dot * nx, vy - 2 * dot * ny
        mag = math.hypot(rvx, rvy)
        if mag > 0:
            rx2, ry2, t_values = 0, 0, []
            l, r, t_t, b_b = playable_rect.left(), playable_rect.right(), playable_rect.top(), playable_rect.bottom()

            if rvx != 0:
                t_l, t_r = (l - reflect_x) / rvx, (r - reflect_x) / rvx
                if t_l > 0.001: t_values.append(t_l)
                if t_r > 0.001: t_values.append(t_r)
            if rvy != 0:
                t_top, t_bot = (t_t - reflect_y) / rvy, (b_b - reflect_y) / rvy
                if t_top > 0.001: t_values.append(t_top)
                if t_bot > 0.001: t_values.append(t_bot)

            if t_values:
                t = min(t_values)
                rx2, ry2 = int(reflect_x + rvx * t), int(reflect_y + rvy * t)
            else: 
                rx2, ry2 = int(reflect_x + rvx / mag * 2000), int(reflect_y + rvy / mag * 2000)

            ref_color = QColor(self.settings['color_reflect_line'])
            if self.is_locked: ref_color.setAlpha(220)
            painter.setPen(QPen(ref_color, self.settings['line_width_reflect'], Qt.SolidLine))
            painter.drawLine(QPoint(reflect_x, reflect_y), QPoint(rx2, ry2))

    def draw_info_text(self, painter, w, h):
        painter.setFont(QFont("Tahoma", 10, QFont.Bold))
        app_name = "8 Ball Pool Guideline"
        hkeys = self.hotkey_manager.hotkeys
        lang = self.settings['lang']
        t = LANG[lang]
        lock_k = hkeys.get('toggle_lock', 'INS').upper()
        set_k = hkeys.get('settings', 'F2').upper()
        save_k = hkeys.get('save', 'F5').upper()
        exit_k = hkeys.get('exit', 'END').upper()
        mode_status = t['ov_locked'] if self.is_locked else t['ov_edit']
        key_info = f"{lock_k}: {t['ov_lock']} | {set_k}: {t['ov_set']} | {save_k}: {t['ov_save']} | {exit_k}: {t['ov_exit']}"
        display_text = f"{app_name} | {mode_status} | {key_info}"
        txt_color = QColor(80, 255, 80) if not self.is_locked else QColor(255, 80, 80)
        painter.setPen(txt_color)
        painter.drawText(QRect(0, 5, w, 30), Qt.AlignCenter, display_text)

    def mousePressEvent(self, event):
        if self.is_locked: return
        if event.button() == Qt.LeftButton:
            if (event.pos() - self.ball_pos).manhattanLength() < 25: self.dragging_ball = True
            elif (event.pos() - self.reflect_pos).manhattanLength() < 20: self.dragging_reflect = True
            elif event.x() > self.width() - 30 and event.y() > self.height() - 30: self.resizing = True
            elif event.y() < 40:
                self.dragging_window = True
                self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.is_locked: return
        update_settings_pos = False
        min_x, max_x = self.table_padding, self.width() - self.table_padding
        min_y, max_y = self.table_padding + 25, self.height() - self.table_padding
        if self.dragging_ball:
            self.ball_pos = QPoint(max(min_x, min(event.x(), max_x)), max(min_y, min(event.y(), max_y)))
            self.update()
        elif self.dragging_reflect:
            self.reflect_pos = QPoint(max(min_x, min(event.x(), max_x)), max(min_y, min(event.y(), max_y)))
            self.update()
        elif self.resizing:
            self.resize(max(400, event.x()), max(300, event.y()))
            update_settings_pos = True
        elif self.dragging_window:
            self.move(event.globalPos() - self.offset)
            update_settings_pos = True

        if update_settings_pos and self.settings_ui.isVisible():
             self.settings_ui.move(self.x() + self.width(), self.y())

    def mouseReleaseEvent(self, event):
        self.dragging_ball = self.dragging_reflect = self.dragging_window = self.resizing = False
        self.save_settings()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1A1A1A")); palette.setColor(QPalette.WindowText, QColor("#CCCCCC"))
    palette.setColor(QPalette.Base, QColor("#202020")); palette.setColor(QPalette.AlternateBase, QColor("#1A1A1A"))
    palette.setColor(QPalette.ToolTipBase, Qt.white); palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, QColor("#CCCCCC")); palette.setColor(QPalette.Button, QColor("#3A3A3A"))
    palette.setColor(QPalette.ButtonText, Qt.white); palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor("#00AAFF")); palette.setColor(QPalette.Highlight, QColor("#00AAFF"))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    window = PoolGuidelineGlobal()
    window.show()
    sys.exit(app.exec_())
