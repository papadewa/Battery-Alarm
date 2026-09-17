import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time
import wave
from dataclasses import asdict

import psutil
from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, QStandardPaths, QLockFile, QCoreApplication
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPixmap, QPen, QRegion
from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QSlider, QCheckBox,
    QComboBox, QSystemTrayIcon, QMenu, QMessageBox, QGroupBox, QScrollArea)
from core import Settings, Battery, AlarmEngine, status_text, remaining_text, TONES, SKINS, SIZES, short_status
from tones import synthesize, RATE
from skins import skin_path

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
INK, MUTED, LOW, GOOD = '#512B1D', '#795646', '#A8342B', '#32664A'

_startup_log_path = None

def _startup_log(msg):
    global _startup_log_path
    if _startup_log_path is None:
        try:
            log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
            log_dir.mkdir(parents=True, exist_ok=True)
            _startup_log_path = log_dir / 'startup.log'
        except Exception:
            _startup_log_path = Path('startup.log')
    try:
        with open(_startup_log_path, 'a', encoding='utf-8') as f:
            f.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    except Exception:
        pass

_startup_log(f'=== Battery Cat starting === args={sys.argv} frozen={getattr(sys, "frozen", False)}')
STYLE = '''
QWidget { color: #512B1D; font-family: "Nunito"; font-size: 14px; }
QDialog { background: #FFF9EF; }
QScrollArea, QWidget#settingsBody { background: #FFF9EF; border: none; }
QLabel { background: transparent; }
QLabel#title { font-size: 25px; font-weight: 700; }
QLabel#muted { color: #795646; }
QGroupBox { font-weight: 600; border: 1px solid #DFC9B7; border-radius: 12px; margin-top: 14px; padding: 20px 14px 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }
QSpinBox, QComboBox { background: #FFFFFF; border: 1px solid #B99A84; border-radius: 6px; padding: 6px 10px; min-height: 24px; }
QPushButton { background: #F6E5D6; border: 1px solid #DFC9B7; border-radius: 8px; padding: 8px 16px; min-height: 20px; font-weight: 600; }
QPushButton:hover { background: #F5CEB6; }
QPushButton:pressed { background: #EDB695; }
QPushButton#primary { background: #8C4126; color: white; border-color: #8C4126; }
QPushButton#primary:hover { background: #71331D; }
QPushButton:focus, QSpinBox:focus, QComboBox:focus { border: 2px solid #8C4126; }
QCheckBox { spacing: 10px; min-height: 30px; }
QCheckBox::indicator { width: 18px; height: 18px; }
QSlider::groove:horizontal { height: 5px; background: #DFC9B7; border-radius: 2px; }
QSlider::handle:horizontal { background: #8C4126; width: 17px; margin: -6px 0; border-radius: 8px; }
QToolTip { background: #FFF9EF; color: #512B1D; border: 1px solid #DFC9B7; padding: 6px; }
'''


def widget_font(pixels, weight=QFont.Weight.Normal):
    font = QFont('Nunito')
    font.setPixelSize(pixels)
    font.setWeight(weight)
    return font


def button(text, callback, primary=False):
    w = QPushButton(text)
    if primary:
        w.setObjectName('primary')
    w.clicked.connect(callback)
    return w


def text_label(text, name=None):
    w = QLabel(text)
    w.setWordWrap(True)
    if name:
        w.setObjectName(name)
    return w


def set_autostart(enabled):
    if not getattr(sys, 'frozen', False):
        if enabled:
            raise RuntimeError('Jalankan versi terpasang untuk mengaktifkan mulai otomatis.')
        return
    exe = str(Path(sys.executable).resolve())
    if sys.platform == 'win32':
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
            if enabled:
                winreg.SetValueEx(key, 'BatteryCat', 0, winreg.REG_SZ, f'"{exe}" --background')
            else:
                try:
                    winreg.DeleteValue(key, 'BatteryCat')
                except FileNotFoundError:
                    pass
    elif sys.platform == 'darwin':
        import plistlib
        path = Path.home() / 'Library/LaunchAgents/com.batterycat.app.plist'
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(plistlib.dumps({'Label': 'com.batterycat.app', 'ProgramArguments': [exe, '--background'], 'RunAtLoad': True}))
        else:
            path.unlink(missing_ok=True)
    else:
        path = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'autostart/battery-cat.desktop'
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Desktop Entry quoted argument escaping, independent of shell syntax.
            escaped = exe.replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
            path.write_text(f'[Desktop Entry]\nType=Application\nName=Battery Cat\nExec="{escaped}" --background\nTerminal=false\n', encoding='utf-8')
        else:
            path.unlink(missing_ok=True)


class Sound:
    def __init__(self, folder):
        self.folder = folder
        self.process = None

    def stop(self):
        if sys.platform == 'win32':
            import winsound
            winsound.PlaySound(None, 0)
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.process = None

    def play(self, settings, kind="high"):
        self.stop()
        enabled = settings.low_sound if kind == "low" else settings.sound
        if not enabled or settings.volume == 0:
            return
        path = self.folder / 'alarm.wav'
        tone = settings.low_tone if kind == "low" else settings.tone
        samples = synthesize(tone, settings.volume)
        with wave.open(str(path), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(samples)
        if sys.platform == 'win32':
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        else:
            player = shutil.which('afplay' if sys.platform == 'darwin' else 'paplay') or shutil.which('aplay')
            if player:
                self.process = subprocess.Popen([player, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                QApplication.beep()


class CatWidget(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.image = QPixmap()
        self.load_image()
        self.drag_offset = None
        self.setWindowTitle('Battery Cat')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda point: owner.menu.exec(self.mapToGlobal(point)))
        self.setAccessibleName('Widget Battery Cat')
        self.configure()

    def load_image(self):
        name = self.owner.settings.skin
        img = QPixmap(str(skin_path(name, ROOT)))
        if img.isNull():
            _startup_log(f'Skin {name} missing, fallback to Kucing')
            img = QPixmap(str(ROOT / 'assets/cat-clock.png'))
        self.image = img

    def configure(self):
        visible = self.isVisible()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.owner.settings.topmost:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        size = self.owner.settings.size
        self.setFixedSize(size, size)
        scaled = self.image.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # The actual artwork alpha defines clickable area, not a rectangle approximation.
        self.setMask(QRegion(scaled.mask()))
        if visible:
            self.show()
        self.clamp_position()
        self.update()

    def clamp_position(self):
        available = [s.availableGeometry() for s in QApplication.screens()]
        if not any(r.contains(self.geometry().center()) for r in available):
            r = QApplication.primaryScreen().availableGeometry()
            self.move(r.right() - self.width() - 24, r.bottom() - self.height() - 32)
        else:
            r = next(r for r in available if r.contains(self.geometry().center()))
            self.move(max(r.left(), min(self.x(), r.right() - self.width() + 1)), max(r.top(), min(self.y(), r.bottom() - self.height() + 1)))

    def paint_compact(self):
        """Text overlay in device pixels for tiny widgets (<200 px).

        At 72/120 px the legacy 320-space text shrinks to ~2-5 px, so we
        redraw in real pixels with minimum sizes: percentage always,
        one-word status + limits row on 110+ px, percentage only below.
        Color coding (LOW/GOOD/INK) is preserved as the primary signal.
        """
        s = float(self.width())
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.drawPixmap(0, 0, self.width(), self.height(), self.image)
        b = self.owner.battery
        st = self.owner.settings
        color = LOW if b and b.percent <= st.low and not b.plugged else GOOD if b and b.plugged else INK
        if self.owner.error:
            state = 'Gagal membaca baterai'
        elif not st.enabled:
            state = 'Pemantauan dijeda'
        elif self.owner.engine.snoozed_until > time.monotonic():
            state = 'Pengingat ditunda'
        else:
            state = status_text(b)
        value = f'{b.percent:.0f}%' if b else '—'
        p.setPen(QColor(color))
        font = QFont('Nunito')
        font.setWeight(QFont.Weight.Bold)
        if s < 110:
            font.setPixelSize(max(13, int(s * 0.19)))
            p.setFont(font)
            p.drawText(QRectF(0, s * 0.42, s, s * 0.26), Qt.AlignmentFlag.AlignCenter, value)
        else:
            font.setPixelSize(max(16, int(s * 0.17)))
            p.setFont(font)
            p.drawText(QRectF(0, s * 0.40, s, s * 0.20), Qt.AlignmentFlag.AlignCenter, value)
            small = QFont('Nunito')
            small.setWeight(QFont.Weight.DemiBold)
            small.setPixelSize(max(9, int(s * 0.075)))
            p.setFont(small)
            p.setPen(QColor(INK))
            p.drawText(QRectF(0, s * 0.60, s, s * 0.12), Qt.AlignmentFlag.AlignCenter, short_status(state))
            tiny = QFont('Nunito')
            tiny.setPixelSize(max(9, int(s * 0.07)))
            p.setFont(tiny)
            p.setPen(QColor(MUTED))
            p.drawText(QRectF(0, s * 0.72, s, s * 0.10), Qt.AlignmentFlag.AlignCenter, f'L{st.low} · T{st.high}')
        p.end()

    def paintEvent(self, event):
        if self.width() < 200:
            self.paint_compact()
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.scale(self.width() / 320, self.height() / 320)
        p.drawPixmap(0, 0, 320, 320, self.image)
        b = self.owner.battery
        s = self.owner.settings
        color = LOW if b and b.percent <= s.low and not b.plugged else GOOD if b and b.plugged else INK
        p.setPen(QColor(color))
        p.setFont(widget_font(50, QFont.Weight.Bold))
        value = f'{b.percent:.0f}%' if b else '—'
        p.drawText(QRectF(65, 126, 190, 65), Qt.AlignmentFlag.AlignCenter, value)
        p.setFont(widget_font(12, QFont.Weight.DemiBold))
        state = status_text(b) if s.enabled else 'Pemantauan dijeda'
        if self.owner.engine.snoozed_until > time.monotonic():
            state = 'Pengingat ditunda'
        if self.owner.error:
            state = 'Gagal membaca baterai'
        p.drawText(QRectF(61, 186, 198, 22), Qt.AlignmentFlag.AlignCenter, state)
        p.setPen(QColor(MUTED))
        p.setFont(widget_font(11))
        p.drawText(QRectF(63, 209, 194, 20), Qt.AlignmentFlag.AlignCenter, remaining_text(b))
        p.setPen(QPen(QColor('#DFC9B7'), 1))
        p.drawLine(120, 232, 200, 232)
        p.setFont(widget_font(11, QFont.Weight.DemiBold))
        p.setPen(QColor(INK))
        p.drawText(QRectF(108, 236, 104, 16), Qt.AlignmentFlag.AlignCenter, f'Rendah {s.low}%')
        p.drawText(QRectF(108, 252, 104, 16), Qt.AlignmentFlag.AlignCenter, f'Target {s.high}%')
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if self.drag_offset is not None:
            self.drag_offset = None
            self.clamp_position()
            self.owner.save_position()

    def mouseDoubleClickEvent(self, event):
        self.owner.open_settings()

    def closeEvent(self, event):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            event.ignore()
        else:
            self.owner.quit()


class Preferences(QDialog):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.setWindowTitle('Pengaturan · Battery Cat')
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLE)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body.setObjectName('settingsBody')
        scroll.setWidget(body)
        root_layout.addWidget(scroll)
        self.resize(500, min(820, QApplication.primaryScreen().availableGeometry().height() - 80))
        outer = QVBoxLayout(body)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(14)
        outer.addWidget(text_label('Teman kecil, pengingat setia.', 'title'))
        outer.addWidget(text_label('Atur sekali. Kucingmu akan menjaga waktunya.', 'muted'))
        self.live = text_label('Membaca baterai…')
        outer.addWidget(self.live)
        group = QGroupBox('Kapan aku mengingatkan?')
        form = QFormLayout(group)
        form.setVerticalSpacing(10)
        self.low, self.high = QSpinBox(), QSpinBox()
        self.low.setRange(5, 60)
        self.high.setRange(10, 100)
        self.low.setSuffix(' %')
        self.high.setSuffix(' %')
        form.addRow('Baterai rendah', self.low)
        form.addRow('Target pengisian', self.high)
        self.snooze = QSpinBox()
        self.snooze.setRange(1, 60)
        self.snooze.setSuffix(' menit')
        form.addRow('Durasi tunda', self.snooze)
        outer.addWidget(group)
        group = QGroupBox('Suara pengingat')
        form = QFormLayout(group)
        self.sound = QCheckBox('Suara target pengisian')
        form.addRow(self.sound)
        self.tone = QComboBox()
        self.tone.addItems(TONES)
        form.addRow('Nada target', self.tone)
        form.addRow(button('Tes suara target', lambda: self.test_sound('high')))
        self.low_sound = QCheckBox('Suara baterai rendah')
        form.addRow(self.low_sound)
        self.low_tone = QComboBox()
        self.low_tone.addItems(TONES)
        form.addRow('Nada baterai rendah', self.low_tone)
        form.addRow(button('Tes suara baterai rendah', lambda: self.test_sound('low')))
        volume_row = QHBoxLayout()
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setAccessibleName('Volume alarm')
        self.volume_label = QLabel()
        self.volume.valueChanged.connect(lambda v: self.volume_label.setText(f'{v}%'))
        volume_row.addWidget(self.volume)
        volume_row.addWidget(self.volume_label)
        form.addRow('Volume', volume_row)
        outer.addWidget(group)
        self.enabled = QCheckBox('Aktifkan pemantauan baterai')
        self.topmost = QCheckBox('Widget selalu di atas jendela lain')
        self.autostart = QCheckBox('Mulai otomatis saat masuk ke laptop')
        for control in (self.enabled, self.topmost, self.autostart):
            outer.addWidget(control)
        row = QHBoxLayout()
        row.addWidget(QLabel('Skin hewan'))
        self.skin = QComboBox()
        self.skin.addItems(SKINS)
        row.addWidget(self.skin, 1)
        outer.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel('Ukuran widget'))
        self.size = QComboBox()
        for label, val in SIZES:
            self.size.addItem(label, val)
        row.addWidget(self.size, 1)
        outer.addLayout(row)
        outer.addWidget(text_label('Geser kepala kucing untuk memindahkannya. Klik dua kali untuk pengaturan; klik kanan untuk menu. Alarm berbunyi singkat dan bisa ditunda.', 'muted'))
        self.feedback = text_label('')
        self.feedback.setStyleSheet('color: #A8342B')
        outer.addWidget(self.feedback)
        row = QHBoxLayout()
        row.addWidget(button('Tutup', self.close))
        row.addStretch()
        row.addWidget(button('Simpan pengaturan', self.commit, True))
        outer.addLayout(row)
        self.reload()

    def reload(self):
        s = self.owner.settings
        for key in ('low', 'high', 'snooze', 'volume'):
            getattr(self, key).setValue(getattr(s, key))
        self.volume_label.setText(f'{s.volume}%')
        for key in ('sound', 'low_sound', 'enabled', 'topmost', 'autostart'):
            getattr(self, key).setChecked(getattr(s, key))
        self.tone.setCurrentText(s.tone)
        self.low_tone.setCurrentText(s.low_tone)
        self.skin.setCurrentText(s.skin if s.skin in SKINS else SKINS[0])
        idx = self.size.findData(s.size)
        self.size.setCurrentIndex(idx if idx >= 0 else 1)
        self.feedback.setText('')

    def values(self):
        s = Settings.parse(asdict(self.owner.settings))
        for key in ('low', 'high', 'snooze', 'volume'):
            setattr(s, key, getattr(self, key).value())
        for key in ('sound', 'low_sound', 'enabled', 'topmost', 'autostart'):
            setattr(s, key, getattr(self, key).isChecked())
        s.tone = self.tone.currentText()
        s.low_tone = self.low_tone.currentText()
        s.skin = self.skin.currentText()
        s.size = self.size.currentData()
        return s

    def test_sound(self, kind="high"):
        s = self.values()
        s.sound = True
        s.low_sound = True
        try:
            self.owner.sound.play(s, kind)
        except Exception as exc:
            self.feedback.setText(f'Suara tidak dapat diputar: {exc}')

    def commit(self):
        self.feedback.setStyleSheet('color: #A8342B')
        s = self.values()
        if s.high < s.low + 5:
            self.feedback.setText('Target pengisian harus setidaknya 5% di atas batas rendah.')
            return
        try:
            if s.autostart != self.owner.settings.autostart:
                set_autostart(s.autostart)
            self.owner.persist(s)
        except Exception as exc:
            self.feedback.setText(f'Belum tersimpan: {exc}')
            return
        thresholds_changed = (s.low, s.high, s.enabled) != (self.owner.settings.low, self.owner.settings.high, self.owner.settings.enabled)
        self.owner.settings = s
        if thresholds_changed:
            self.owner.engine.reset()
            self.owner.dismiss_alarm()
        self.owner.widget.load_image()
        self.owner.widget.configure()
        self.owner.update_menu()
        self.owner.poll()
        self.feedback.setStyleSheet('color: #32664A')
        self.feedback.setText('Tersimpan. Kucingmu siap menemani.')

    def closeEvent(self, event):
        self.owner.sound.stop()
        super().closeEvent(event)


class AlarmWindow(QDialog):
    def __init__(self, owner, kind):
        super().__init__()
        self.owner = owner
        self.setWindowTitle('Pengingat · Battery Cat')
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setStyleSheet(STYLE)
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        picture = QLabel()
        picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        picture.setPixmap(owner.widget.image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(picture)
        self.title_text = ('Waktunya charge!' if kind == 'low' else 'Baterai sudah penuh!' if owner.settings.high == 100 else 'Target sudah tercapai!')
        layout.addWidget(text_label(self.title_text, 'title'))
        value = owner.battery.percent if owner.battery else 0
        message = f'Baterai tinggal {value:.0f}%. Sambungkan charger agar kamu bisa lanjut dengan tenang.' if kind == 'low' else f'Baterai mencapai {value:.0f}%. Target pengisianmu {owner.settings.high}%; kamu bisa melepas charger sekarang.'
        layout.addWidget(text_label(message))
        layout.addWidget(button('Hentikan alarm', owner.acknowledge, True))
        layout.addWidget(button(f'Ingatkan lagi {owner.settings.snooze} menit', owner.snooze))

    def reject(self):
        self.owner.acknowledge()


class Controller:
    def __init__(self, app, data_dir=None, testing=False):
        _startup_log('Controller.__init__ start')
        self.app = app
        QFontDatabase.addApplicationFont(str(ROOT / 'assets/Nunito.ttf'))
        app.setFont(QFont('Nunito', 10))
        self.testing = testing
        self.folder = Path(data_dir or QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
        self.folder.mkdir(parents=True, exist_ok=True)
        self.config_file = self.folder / 'settings.json'
        self.settings = Settings()
        self.load_error = None
        if self.config_file.exists():
            try:
                self.settings = Settings.parse(json.loads(self.config_file.read_text(encoding='utf-8')))
            except (ValueError, OSError):
                self.load_error = 'Pengaturan lama tidak dapat dibaca. Pengaturan awal dipakai; simpan lagi untuk memperbaikinya.'
        self.engine = AlarmEngine()
        self.battery = None
        self.error = None
        self.alarm = None
        self.preferences = None
        self.sound = Sound(self.folder)
        _startup_log('Loading icon and widget image')
        self.icon = QIcon(str(ROOT / 'assets/cat-clock.png'))
        if self.icon.isNull():
            _startup_log('WARNING: Icon is null - cat-clock.png may be missing')
        self.app.setWindowIcon(self.icon)
        self.menu = QMenu()
        self.widget = CatWidget(self)
        if self.widget.image.isNull():
            _startup_log('WARNING: Widget image is null - cat-clock.png may be missing')
        self.tray = QSystemTrayIcon(self.icon, self.app)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.tray_clicked)
        self.tray.messageClicked.connect(self.show_widget)
        self.update_menu()
        _startup_log(f'platform={app.platformName()} tray available={QSystemTrayIcon.isSystemTrayAvailable()} testing={testing} background={"--background" in sys.argv}')
        if not testing:
            self.tray.show()
        if self.settings.x is not None and self.settings.y is not None:
            self.widget.move(self.settings.x, self.settings.y)
        else:
            self.widget.move(-10000, -10000)
        self.widget.clamp_position()
        self.widget.setToolTip('Geser untuk memindahkan · Klik dua kali untuk pengaturan · Klik kanan untuk menu')
        self.timer = QTimer()
        self.timer.setInterval(15000)
        self.timer.timeout.connect(self.poll)
        if not testing:
            self.poll()
            self.timer.start()
            show_widget = '--background' not in sys.argv or not QSystemTrayIcon.isSystemTrayAvailable()
            _startup_log(f'Widget show decision: show_widget={show_widget} background_mode={"--background" in sys.argv} tray_available={QSystemTrayIcon.isSystemTrayAvailable()}')
            if show_widget:
                self.widget.show()
                _startup_log('Widget shown')
            else:
                _startup_log('Widget hidden (background mode with tray)')
            if not self.config_file.exists() or self.load_error:
                self.open_settings()
                if self.load_error:
                    self.preferences.feedback.setText(self.load_error)
        _startup_log('Controller.__init__ complete')

    def persist(self, settings):
        tmp = self.config_file.with_suffix('.tmp')
        tmp.write_text(json.dumps(asdict(settings), indent=2), encoding='utf-8')
        os.replace(tmp, self.config_file)

    def save_position(self):
        self.settings.x, self.settings.y = self.widget.x(), self.widget.y()
        try:
            self.persist(self.settings)
        except OSError:
            self.tray.showMessage('Battery Cat', 'Posisi belum tersimpan. Periksa izin penyimpanan aplikasi.')

    def update_menu(self):
        self.menu.clear()
        self.menu.addAction('Tampilkan kucing', self.show_widget)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.menu.addAction('Sembunyikan kucing', self.widget.hide)
        self.menu.addAction('Pengaturan…', self.open_settings)
        self.menu.addAction('Jeda pemantauan' if self.settings.enabled else 'Lanjutkan pemantauan', self.toggle)
        self.menu.addSeparator()
        self.menu.addAction('Hentikan alarm', self.acknowledge)
        self.menu.addAction('Keluar Battery Cat', self.quit)

    def toggle(self):
        new = Settings.parse(asdict(self.settings))
        new.enabled = not new.enabled
        try:
            self.persist(new)
        except OSError as exc:
            QMessageBox.warning(self.widget, 'Belum tersimpan', str(exc))
            return
        self.settings = new
        self.engine.reset()
        self.dismiss_alarm()
        self.update_menu()
        if self.preferences:
            self.preferences.enabled.setChecked(new.enabled)
        self.poll()

    def tray_clicked(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_widget()

    def show_widget(self):
        self.widget.clamp_position()
        self.widget.show()
        self.widget.raise_()

    def open_settings(self):
        if self.preferences is None:
            self.preferences = Preferences(self)
        elif not self.preferences.isVisible():
            self.preferences.reload()
        self.refresh_labels()
        self.preferences.show()
        self.preferences.raise_()
        self.preferences.activateWindow()

    def refresh_labels(self):
        self.widget.update()
        line = f'{self.battery.percent:.0f}% · {status_text(self.battery)}' if self.battery else 'Baterai tidak tersedia'
        if self.error:
            line = 'Tidak dapat membaca baterai. Mencoba lagi otomatis.'
        self.tray.setToolTip(f'Battery Cat · {line}')
        if self.preferences:
            self.preferences.live.setText(line + '\n' + remaining_text(self.battery))

    def poll(self):
        try:
            raw = psutil.sensors_battery()
            self.battery = Battery(raw.percent, raw.power_plugged, raw.secsleft) if raw else None
            if self.battery and not self.battery.valid():
                raise ValueError('Invalid battery reading')
            self.error = None
        except Exception as exc:
            self.battery = None
            self.error = str(exc)
        self.evaluate()

    def evaluate(self):
        event = self.engine.update(self.battery, self.settings, time.monotonic())
        if not self.engine.active:
            self.dismiss_alarm()
        if event:
            self.dismiss_alarm()
            self.alarm = AlarmWindow(self, event)
            self.alarm.show()
            self.alarm.raise_()
            if not self.testing:
                self.tray.showMessage('Battery Cat', self.alarm.title_text, QSystemTrayIcon.MessageIcon.Warning if event == 'low' else QSystemTrayIcon.MessageIcon.Information, 10000)
                try:
                    self.sound.play(self.settings, event)
                except (OSError, RuntimeError):
                    QApplication.beep()
        self.refresh_labels()

    def dismiss_alarm(self):
        if self.alarm:
            self.alarm.hide()
            self.alarm.deleteLater()
            self.alarm = None
            self.sound.stop()

    def acknowledge(self):
        self.engine.acknowledge()
        self.dismiss_alarm()
        self.sound.stop()
        self.refresh_labels()

    def snooze(self):
        self.engine.snooze(time.monotonic(), self.settings.snooze)
        self.dismiss_alarm()
        self.refresh_labels()

    def quit(self):
        self.timer.stop()
        self.save_position()
        self.sound.stop()
        self.tray.hide()
        self.app.quit()


def _is_process_alive(pid):
    try:
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError, PermissionError):
        return False


def main():
    _startup_log('main() start')
    app = QApplication(sys.argv)
    app.setApplicationName('Battery Cat')
    app.setOrganizationName('BatteryCat')
    app.setQuitOnLastWindowClosed(False)
    if '--smoke-test' in sys.argv:
        # Explicit packaging diagnostic: isolated data, real OS battery read, no sound/autostart.
        import tempfile
        report = Path(sys.argv[sys.argv.index('--smoke-test') + 1]).resolve()
        with tempfile.TemporaryDirectory(dir=report.parent) as temp:
            c = Controller(app, temp, testing=True)
            c.settings.enabled = False
            c.poll()
            c.widget.show()
            c.open_settings()
            def finish_test():
                report.write_text(json.dumps({'ok': c.error is None, 'battery': asdict(c.battery) if c.battery else None, 'error': c.error, 'font_loaded': 'Nunito' in QFontDatabase.families(), 'alpha': c.widget.image.hasAlphaChannel(), 'rss_mb': round(psutil.Process().memory_info().rss / 1048576, 1)}, indent=2), encoding='utf-8')
                c.preferences.close()
                c.widget.hide()
                app.quit()
            QTimer.singleShot(5000, finish_test)
            return app.exec()
    folder = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    folder.mkdir(parents=True, exist_ok=True)
    lock_path = folder / 'instance.lock'
    lock = QLockFile(str(lock_path))
    lock.setStaleLockTime(0)
    _startup_log(f'Attempting lock: {lock_path}')
    if not lock.tryLock(100):
        _startup_log('Lock failed - another instance may be running')
        # Check if lock holder process is still alive
        try:
            # getLockInfo returns (pid: int, hostname: str, appname: str)
            pid, hostname, appname = lock.getLockInfo()
            if pid and pid > 0:
                _startup_log(f'Lock holder PID: {pid}')
                if not _is_process_alive(pid):
                    _startup_log('Lock holder process dead - forcing lock break')
                    lock.removeStaleLockFile()
                    if lock.tryLock(100):
                        _startup_log('Lock acquired after breaking stale lock')
                    else:
                        _startup_log('Still cannot acquire lock after breaking stale lock')
                        QMessageBox.information(None, 'Battery Cat sudah aktif', 'Kucingmu sudah berjalan. Buka lewat ikon Battery Cat di dekat jam laptop.')
                        return 0
                else:
                    _startup_log('Lock holder process alive - another instance running')
                    QMessageBox.information(None, 'Battery Cat sudah aktif', 'Kucingmu sudah berjalan. Buka lewat ikon Battery Cat di dekat jam laptop.')
                    return 0
            else:
                _startup_log('Could not get lock info (no PID)')
                QMessageBox.information(None, 'Battery Cat sudah aktif', 'Kucingmu sudah berjalan. Buka lewat ikon Battery Cat di dekat jam laptop.')
                return 0
        except Exception as exc:
            _startup_log(f'Lock check error: {exc}')
            QMessageBox.information(None, 'Battery Cat sudah aktif', 'Kucingmu sudah berjalan. Buka lewat ikon Battery Cat di dekat jam laptop.')
            return 0
    _startup_log('Lock acquired successfully')
    controller = Controller(app)
    app.aboutToQuit.connect(controller.sound.stop)
    _startup_log('Entering app.exec()')
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
