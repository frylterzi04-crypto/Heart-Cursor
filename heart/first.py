import sys
import random
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics
from pynput import mouse

# Tıklama olaylarını PyQt arayüzüne iletmek için sinyal sınıfı
class MouseSignals(QObject):
    click_signal = pyqtSignal(int, int)

signals = MouseSignals()

class HeartParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(18, 28)
        self.alpha = 255  # Opaklık (Saydamlık)
        self.speed_y = random.uniform(1.5, 3.0)  # Yukarı yükselme hızı
        self.speed_x = random.uniform(-0.5, 0.5) # Hafif sağa/sola kayma

class HeartOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.hearts = []
        self.init_ui()
        
    def init_ui(self):
        # Pencereyi tamamen şeffaf, çerçevesiz ve tıklamaları aşağı geçiren katman yap
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Tüm ekranı kapla
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Efekt animasyonu için zamanlayıcı (30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(33)

    def add_heart(self, x, y):
        # Tıklanan noktaya yeni bir kalp ekle
        self.hearts.append(HeartParticle(x, y))

    def update_particles(self):
        if not self.hearts:
            return

        # Kalpleri yukarı doğru hareket ettir ve şeffaflaştır
        for heart in self.hearts[:]:
            heart.y -= heart.speed_y
            heart.x += heart.speed_x
            heart.alpha -= 5  # Kaybolma hızı
            
            if heart.alpha <= 0:
                self.hearts.remove(heart)
                
        self.update()  # Ekranı yeniden çiz

    def paintEvent(self, event):
        if not self.hearts:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for heart in self.hearts:
            font = QFont("Segoe UI Emoji", heart.size)
            painter.setFont(font)
            
            # Kalp rengi ve saydamlığı
            color = QColor(255, 50, 100, max(0, int(heart.alpha)))
            painter.setPen(color)
            
            # Kalbi tam imleç ucuna ortalayarak çiz
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect("❤️")
            draw_x = int(heart.x - rect.width() / 2)
            draw_y = int(heart.y + rect.height() / 4)
            
            painter.drawText(draw_x, draw_y, "❤️")

# Global fare dinleyicisi
def on_click(x, y, button, pressed):
    if pressed:
        signals.click_signal.emit(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    overlay = HeartOverlay()
    overlay.show()
    
    # Tıklama sinyalini arayüze bağla
    signals.click_signal.connect(overlay.add_heart)
    
    # Fare dinleyicisini arka planda başlat
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    sys.exit(app.exec())