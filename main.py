import os
import sys
import json
import winsound
import keyboard
import math

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

CONFIG_FILE = "pool_config.json"
class HotkeySignaler(QObject):
    toggle_signal = pyqtSignal()
    exit_signal = pyqtSignal()
    save_signal = pyqtSignal()
    lang_signal = pyqtSignal()

class PoolGuidelineGlobal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.default_geometry = (100, 100, 1000, 500)
        self.ball_pos = QPoint(200, 200)
        self.ball_radius = 12 
        self.is_locked = False
        self.table_padding = 25 
        self.current_lang = 'th'
        self.load_settings()
        self.dragging_ball = False
        self.dragging_window = False
        self.resizing = False
        self.offset = QPoint()

        self.signaler = HotkeySignaler()
        self.signaler.toggle_signal.connect(self.toggle_lock)
        self.signaler.exit_signal.connect(self.close_and_save)
        self.signaler.save_signal.connect(self.save_settings_with_sound)
        self.signaler.lang_signal.connect(self.toggle_language)

        keyboard.add_hotkey('insert', lambda: self.signaler.toggle_signal.emit())
        keyboard.add_hotkey('end', lambda: self.signaler.exit_signal.emit())
        keyboard.add_hotkey('f5', lambda: self.signaler.save_signal.emit())
        keyboard.add_hotkey('f9', lambda: self.signaler.lang_signal.emit()) 

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'th' else 'th'
        self.save_settings()
        self.update()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.setGeometry(data['x'], data['y'], data['w'], data['h'])
                    self.ball_pos = QPoint(data['ball_x'], data['ball_y'])
                    self.current_lang = data.get('lang', 'th') 
            except:
                self.setGeometry(*self.default_geometry)
        else:
            self.setGeometry(*self.default_geometry)

    def save_settings(self):
        data = {
            'x': self.x(), 'y': self.y(),
            'w': self.width(), 'h': self.height(),
            'ball_x': self.ball_pos.x(),
            'ball_y': self.ball_pos.y(),
            'lang': self.current_lang
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)

    def save_settings_with_sound(self):
        self.save_settings()
        try:
            winsound.Beep(1500, 100)
        except:
            pass

    def close_and_save(self):
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        playable_rect = QRect(self.table_padding, self.table_padding + 25, w - (self.table_padding * 2), h - (self.table_padding * 2) - 15)
        bg_opacity = 30 if self.is_locked else 150
        painter.setBrush(QColor(20, 20, 20, bg_opacity))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 10, 10)
        painter.setPen(QPen(QColor(0, 170, 255, 180 if not self.is_locked else 50), 2, Qt.DashLine))
        painter.drawRect(playable_rect)
        corner_offset = self.ball_radius + 2 
        side_offset_y = self.ball_radius - 2 
        left = playable_rect.left()
        right = playable_rect.right()
        top = playable_rect.top()
        bottom = playable_rect.bottom()
        mid_x = w // 2

        pockets = [
            QPoint(left + corner_offset, top + corner_offset),
            QPoint(mid_x, top + side_offset_y),
            QPoint(right - corner_offset, top + corner_offset),
            QPoint(left + corner_offset, bottom - corner_offset),
            QPoint(mid_x, bottom - side_offset_y),
            QPoint(right - corner_offset, bottom - corner_offset)
        ]

        line_alpha = 180 if self.is_locked else 100
        
        for p in pockets:
            painter.setBrush(QColor(255, 0, 0, line_alpha))
            painter.setPen(QPen(QColor(255, 255, 255, line_alpha), 1))
            painter.drawEllipse(p, 6, 6)
            dx, dy = p.x() - self.ball_pos.x(), p.y() - self.ball_pos.y()
            angle = math.atan2(dy, dx)
            painter.setPen(QPen(QColor(0, 255, 127, line_alpha), 1.2, Qt.DashLine))
            painter.drawLine(self.ball_pos, p)
            offset_x, offset_y = math.sin(angle) * self.ball_radius, math.cos(angle) * self.ball_radius
            painter.setPen(QPen(QColor(255, 255, 255, line_alpha - 50), 1))
            painter.drawLine(int(self.ball_pos.x() + offset_x), int(self.ball_pos.y() - offset_y), int(p.x() + offset_x), int(p.y() - offset_y))
            painter.drawLine(int(self.ball_pos.x() - offset_x), int(self.ball_pos.y() + offset_y), int(p.x() - offset_x), int(p.y() + offset_y))

        painter.setFont(QFont("Tahoma", 10, QFont.Bold))
        app_name = "8 Ball Pool Guideline"
        if self.current_lang == 'th':
            mode_status = "ล็อคแล้ว (LOCKED)" if self.is_locked else "โหมดแก้ไข (EDITING)"
            key_info = "Insert: ล็อค/ปลดล็อค | F5: บันทึก | F9: สลับภาษา | End: ปิด"
        else:
            mode_status = "LOCKED" if self.is_locked else "EDITING MODE"
            key_info = "Insert: Lock/Unlock | F5: Save | F9: Change Lang | End: Exit"
            
        display_text = f"{app_name} | {mode_status} | {key_info}"
        painter.setPen(QColor(80, 255, 80) if not self.is_locked else QColor(255, 80, 80))
        painter.drawText(QRect(0, 5, w, 30), Qt.AlignCenter, display_text)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawEllipse(self.ball_pos, self.ball_radius, self.ball_radius)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(self.ball_pos, 2, 2)

    def mousePressEvent(self, event):
        if self.is_locked: return
        if event.button() == Qt.LeftButton:
            if (event.pos() - self.ball_pos).manhattanLength() < 25:
                self.dragging_ball = True
            elif event.x() > self.width() - 30 and event.y() > self.height() - 30:
                self.resizing = True
            elif event.y() < 40:
                self.dragging_window = True
                self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.is_locked: return
        if self.dragging_ball:
            w, h = self.width(), self.height()
            min_x = self.table_padding
            max_x = w - self.table_padding
            min_y = self.table_padding + 25 
            max_y = h - self.table_padding
            new_x = max(min_x, min(event.x(), max_x))
            new_y = max(min_y, min(event.y(), max_y))
            self.ball_pos = QPoint(new_x, new_y)
            self.update()
            
        elif self.resizing:
            self.resize(max(400, event.x()), max(300, event.y()))
        elif self.dragging_window:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging_ball = self.dragging_window = self.resizing = False
        self.save_settings()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoolGuidelineGlobal()
    window.show()
    sys.exit(app.exec_())
