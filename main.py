import sys
import winsound
import keyboard
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

class HotkeySignaler(QObject):
    toggle_signal = pyqtSignal()
    exit_signal = pyqtSignal()

class PoolGuidelineGlobal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 895, 487)
        self.ball_pos = QPoint(200, 200)
        self.ball_radius = 12 
        self.is_locked = False
        
        # ระยะขอบโต๊ะ (Padding) ปรับตัวเลขนี้เพื่อให้ตรงกับขอบสีน้ำเงินในเกมของคุณ
        self.table_padding = 25 
        
        self.dragging_ball = False
        self.dragging_window = False
        self.resizing = False
        self.offset = QPoint()

        self.signaler = HotkeySignaler()
        self.signaler.toggle_signal.connect(self.toggle_lock)
        self.signaler.exit_signal.connect(self.close)
        
        keyboard.add_hotkey('insert', lambda: self.signaler.toggle_signal.emit())
        keyboard.add_hotkey('end', lambda: self.signaler.exit_signal.emit())

    def play_sound(self, mode):
        try:
            if mode == "lock": winsound.Beep(1000, 150)
            else: winsound.Beep(400, 150)
        except: pass

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
            self.play_sound("lock")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowTransparentForInput)
            self.play_sound("unlock")
        self.show()
        self.update()

    def draw_pocket_frame(self, painter, x, y, type="corner"):
        painter.setPen(QPen(QColor(60, 70, 150, 255), 3))
        size = 30
        if "top" in type: painter.drawLine(x, y, x, y + size)
        else: painter.drawLine(x, y, x, y - size)
        if "left" in type: painter.drawLine(x, y, x + size, y)
        else: painter.drawLine(x, y, x - size, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        
        # (ระบบกรอบจำลอง Playable Area ยังคงอยู่เพื่อให้เห็นขอบเขตตอนปรับแต่ง)
        playable_rect = QRect(self.table_padding, self.table_padding + 15, 
                             w - (self.table_padding * 2), h - (self.table_padding * 2) - 10)

        # วาดพื้นหลัง
        bg_opacity = 40 if self.is_locked else 160
        painter.setBrush(QColor(30, 30, 30, bg_opacity))
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawRoundedRect(0, 0, w, h, 10, 10)

        if not self.is_locked:
            painter.setPen(QPen(QColor(0, 120, 255, 80), 1, Qt.DashLine))
            painter.drawRect(playable_rect)

        # ตำแหน่งปากหลุม
        pockets = [QPoint(self.table_padding, self.table_padding + 20),           # บนซ้าย
                   QPoint(w // 2, self.table_padding + 15),                      # บนกลาง
                   QPoint(w - self.table_padding, self.table_padding + 20),      # บนขวา
                   QPoint(self.table_padding, h - self.table_padding),           # ล่างซ้าย
                   QPoint(w // 2, h - self.table_padding + 5),                  # ล่างกลาง
                   QPoint(w - self.table_padding, h - self.table_padding)]       # ล่างขวา

        line_alpha = 180 if self.is_locked else 100
        
        for p in pockets:
            # --- ส่วนที่แก้ไข: นำระบบกรองเส้นออก ---
            # (โค้ดที่เคยเช็ค mid_point, mid_left, mid_right ถูกลบออกไป)

            dx = p.x() - self.ball_pos.x()
            dy = p.y() - self.ball_pos.y()
            angle = math.atan2(dy, dx)
            
            # 1. วาดเส้นแกนกลาง (สีเขียวประ) -> วาดทันที
            painter.setPen(QPen(QColor(0, 255, 127, line_alpha), 1.2, Qt.DashLine))
            painter.drawLine(self.ball_pos, p)
            
            # 2. วาดเส้นขอบลูก (สีขาวขนาน) -> วาดทันที
            offset_x = math.sin(angle) * self.ball_radius
            offset_y = math.cos(angle) * self.ball_radius
            
            painter.setPen(QPen(QColor(255, 255, 255, line_alpha - 50), 1))
            painter.drawLine(
                int(self.ball_pos.x() + offset_x), int(self.ball_pos.y() - offset_y),
                int(p.x() + offset_x), int(p.y() - offset_y)
            )
            painter.drawLine(
                int(self.ball_pos.x() - offset_x), int(self.ball_pos.y() + offset_y),
                int(p.x() - offset_x), int(p.y() + offset_y)
            )
            
            # วาดจุดหลุม
            painter.setBrush(QColor(200, 50, 50))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(p, 4, 4)

        # UI & Ball Marker (ยังคงระบบเดิม)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        status = "!!! LOCKED !!!" if self.is_locked else "EDITING MODE (Triple Validation Removed)"
        painter.drawText(15, 25, f"🎱 {status}")

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 255), 2))
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
            self.ball_pos = event.pos()
            self.update()
        elif self.resizing:
            self.resize(max(400, event.x()), max(300, event.y()))
        elif self.dragging_window:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging_ball = self.dragging_window = self.resizing = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoolGuidelineGlobal()
    window.show()
    
    sys.exit(app.exec_())