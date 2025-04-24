from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QBrush, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint


class GlassButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self._blur_radius = 0
        self.setStyleSheet("""
            background: transparent;
            color: white;
            font-size: 16px;
            border: none;
            font-weight: 500;
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        glass = QLinearGradient(0, 0, 0, self.height())
        glass.setColorAt(0, QColor(255, 103, 0, 180))
        glass.setColorAt(1, QColor(255, 140, 0, 220))

        painter.setBrush(QBrush(glass))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)

        if self.underMouse():
            highlight = QLinearGradient(0, 0, self.width(), 0)
            highlight.setColorAt(0, QColor(255, 255, 255, 0))
            highlight.setColorAt(0.3, QColor(255, 255, 255, 60))
            highlight.setColorAt(0.7, QColor(255, 255, 255, 60))
            highlight.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(highlight))
            painter.drawRoundedRect(self.rect(), 12, 12)

        super().paintEvent(event)

    def enterEvent(self, event):
        self.animateHover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animateHover(False)
        super().leaveEvent(event)

    def animateHover(self, hover):
        anim = QPropertyAnimation(self, b"blurRadius", self)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        anim.setStartValue(self._blur_radius)
        anim.setEndValue(10 if hover else 0)
        anim.start()

    def getBlurRadius(self):
        return self._blur_radius

    def setBlurRadius(self, radius):
        self._blur_radius = radius
        self.update()

    blurRadius = pyqtProperty(int, getBlurRadius, setBlurRadius)


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(900, 650)
        self.setupUI()
        self.setupAnimations()

    def setupUI(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.main_widget.setGraphicsEffect(shadow)

        self.background = QLabel(self.main_widget)
        self.background.setGeometry(0, 0, 900, 650)
        self.background.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #f9f9f9, stop:1 #ffffff);
            border-radius: 20px;
        """)

        self.header = QWidget(self.main_widget)
        self.header.setGeometry(0, 0, 900, 80)
        self.header.setStyleSheet("background: transparent;")

        self.title = QLabel("VISIONARY", self.header)
        self.title.setGeometry(40, 20, 400, 40)
        self.title.setStyleSheet("""
            color: #333;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 1px;
        """)

        self.nav_stack = QStackedWidget(self.main_widget)
        self.nav_stack.setGeometry(40, 100, 820, 480)

        self.createDashboardPage()
        self.createAnalyticsPage()
        self.createSettingsPage()

        self.footer = QWidget(self.main_widget)
        self.footer.setGeometry(0, 590, 900, 60)
        self.footer.setStyleSheet("background: transparent;")

        self.createNavButton("Dashboard", 150, 0, active=True)
        self.createNavButton("Analytics", 350, 1)
        self.createNavButton("Settings", 550, 2)

        self.addWindowControls()

    def createDashboardPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        card1 = self.createCard("实时数据", "128,450", "↑12% 本周增长")
        card2 = self.createCard("活跃用户", "24,891", "↑8% 昨日增长")

        chart_frame = QFrame()
        chart_frame.setMinimumHeight(250)
        chart_frame.setStyleSheet("""
            background: white;
            border-radius: 16px;
            border: 1px solid #eee;
        """)

        layout.addWidget(card1)
        layout.addWidget(card2)
        layout.addWidget(chart_frame)
        layout.setSpacing(20)

        self.nav_stack.addWidget(page)

    def createAnalyticsPage(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        self.nav_stack.addWidget(page)

    def createSettingsPage(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        self.nav_stack.addWidget(page)

    def createCard(self, title, value, trend):
        card = QFrame()
        card.setMinimumHeight(100)
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #eee;
            }
        """)

        layout = QHBoxLayout(card)
        text_frame = QWidget()
        text_layout = QVBoxLayout(text_frame)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 14px; font-weight: 500;")

        value_label = QLabel(value)
        value_label.setStyleSheet("color: #333; font-size: 32px; font-weight: 700; margin: 5px 0;")

        trend_label = QLabel(trend)
        trend_label.setStyleSheet("color: #FF6700; font-size: 13px; font-weight: 500;")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        text_layout.addWidget(trend_label)
        text_layout.addStretch()

        decor = QLabel()
        decor.setFixedSize(80, 80)
        decor.setStyleSheet("""
            background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5,
                                        fx:0.3, fy:0.3,
                                        stop:0 rgba(255,103,0,30),
                                        stop:1 rgba(255,103,0,5));
            border-radius: 40px;
        """)

        layout.addWidget(text_frame, 1)
        layout.addWidget(decor)
        layout.setContentsMargins(25, 15, 25, 15)

        return card

    def createNavButton(self, text, x, index, active=False):
        btn = GlassButton(text, self.footer)
        btn.setGeometry(x, 10, 180, 40)
        btn.clicked.connect(lambda: self.switchPage(index))
        if active:
            btn.setStyleSheet("color: white; font-weight: 600;")

    def addWindowControls(self):
        close_btn = QPushButton("✕", self.header)
        close_btn.setGeometry(850, 20, 30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #999;
                font-size: 18px;
                font-weight: 300;
                border: none;
            }
            QPushButton:hover {
                color: #FF6700;
            }
        """)
        close_btn.clicked.connect(self.close)

        min_btn = QPushButton("–", self.header)
        min_btn.setGeometry(810, 20, 30, 30)
        min_btn.setStyleSheet(close_btn.styleSheet())
        min_btn.clicked.connect(self.showMinimized)

    def switchPage(self, index):
        self.nav_stack.setCurrentIndex(index)

    def setupAnimations(self):
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(500)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

    def showEvent(self, event):
        self.opacity_anim.start()
        super().showEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
            event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    preferred_fonts = ["MiSans", "SF Pro Display", "Segoe UI", "PingFang SC", "Helvetica Neue"]
    for f in preferred_fonts:
        if f in QFont().families():
            app.setFont(QFont(f, 12))
            break

    window = ModernWindow()
    window.show()
    sys.exit(app.exec_())
