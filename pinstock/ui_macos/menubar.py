"""macOS 메뉴바 아이콘 + 팝오버 토글 트리거."""

from PyQt6.QtCore import QObject, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from PyQt6.QtWidgets import QSystemTrayIcon, QApplication

from ..ui_windows.theme import C


# ─── 메뉴바 아이콘 ──────────────────────────────────────────────────────────
class MenuBarIcon(QObject):
    """macOS 메뉴바의 ₩ 아이콘 트리거.

    좌/우 클릭 모두 popover 토글로 처리한다 (Mac 메뉴바 native 패턴).
    종료는 popover 안의 ❌ 버튼으로.
    """

    toggle_popover_requested = pyqtSignal(QPoint, int)   # anchor_global_pos, anchor_width

    def __init__(self, app: QApplication, parent: QObject | None = None):
        super().__init__(parent)
        self.app = app
        self.tray = QSystemTrayIcon(self._make_icon(), self)
        self.tray.setToolTip("Pinstock")
        self.tray.activated.connect(self._on_activated)
        self.tray.show()

    @staticmethod
    def _make_icon() -> QIcon:
        # macOS 메뉴바는 22pt 영역에 표시 — 32px 픽맵을 Qt가 자동 다운스케일.
        px = QPixmap(32, 32)
        px.fill(QColor(0, 0, 0, 0))
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(C["blue"])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(1, 1, 30, 30)
        p.setFont(QFont("Apple SD Gothic Neo", 14, QFont.Weight.Bold))
        p.setPen(QPen(QColor(C["bg"])))
        p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "₩")
        p.end()
        return QIcon(px)

    def _on_activated(self, reason):
        """좌/우 클릭 모두 popover 토글로 처리."""
        # macOS 에서 Trigger/Context 모두 발생할 수 있음 — 둘 다 받음
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.Context,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            anchor_pos, anchor_w = self._anchor_position()
            self.toggle_popover_requested.emit(anchor_pos, anchor_w)

    def _anchor_position(self) -> tuple[QPoint, int]:
        """팝오버를 아래에 띄울 기준 좌표(= 트레이 아이콘 하단 중앙).
        tray.geometry() 가 비어 있으면 화면 우상단 메뉴바 추정 위치로 폴백."""
        geo = self.tray.geometry()
        if geo.width() > 0 and geo.height() > 0:
            return geo.bottomLeft(), geo.width()
        # 폴백: 주 화면 우상단, 메뉴바 높이 추정(24~28px)
        screen = QApplication.primaryScreen()
        sg = screen.geometry()
        # availableGeometry 의 top 이 메뉴바 아래라 그것을 기준으로 약 24px 위로
        avail = screen.availableGeometry()
        fallback_y = avail.y()
        fallback_x = sg.x() + sg.width() - 60   # 메뉴바 우측 근처
        return QPoint(fallback_x, fallback_y), 22
