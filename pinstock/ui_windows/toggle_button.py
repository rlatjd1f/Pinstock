"""원형 토글 버튼 (이모지 표시 + 드래그/클릭)."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont

from .theme import C


# ─── 동그라미 토글 버튼 (이모지만 표시, 드래그 가능) ─────────────────────────
class ToggleButton(QWidget):
    """원형 + 이모지 한 글자만 표시되는 작은 토글 버튼.
    드래그로 위치 이동 / 짧은 클릭으로 clicked 시그널 emit.
    몰컴 모드 등 빠른 숨기기/표시 토글용."""

    SIZE = 44
    DRAG_THRESHOLD = 4

    clicked = pyqtSignal()

    def __init__(self, emoji: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self._emoji = emoji
        self._drag_pos  = None
        self._press_pos = None
        self._moved     = False

        # NoDropShadowWindowHint: Qt 가 자동으로 그리는 정사각형 그림자 제거
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.NoDropShadowWindowHint
        )
        # 위젯 사각형 영역 완전 투명화
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(self.SIZE, self.SIZE)
        if tooltip:
            self.setToolTip(tooltip)

    def set_emoji(self, emoji: str):
        self._emoji = emoji
        self.update()

    RADIUS = 10   # 둥근 모서리 반지름

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 둥근 사각형 카드 (다른 위젯과 동일 톤)
        painter.setBrush(QBrush(QColor(C['bg'])))
        painter.setPen(QPen(QColor(C['surface2']), 1))
        painter.drawRoundedRect(0, 0, self.SIZE - 1, self.SIZE - 1,
                                self.RADIUS, self.RADIUS)
        # 이모지
        painter.setPen(QPen(QColor(C['text'])))
        painter.setFont(QFont("Malgun Gothic", 16))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._emoji)
        painter.end()

    # 드래그 + 클릭 구분 (StockWidget 동일 패턴)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos  = event.globalPosition().toPoint() - self.pos()
            self._press_pos = event.globalPosition().toPoint()
            self._moved     = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            if not self._moved and self._press_pos:
                delta = event.globalPosition().toPoint() - self._press_pos
                if abs(delta.x()) > self.DRAG_THRESHOLD or abs(delta.y()) > self.DRAG_THRESHOLD:
                    self._moved = True
            if self._moved:
                self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._moved:
            self.clicked.emit()
        self._drag_pos  = None
        self._press_pos = None
        self._moved     = False
