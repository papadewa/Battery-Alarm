"""Integration checks for native settings, persistence, sound generation, and autostart command."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import unittest
import wave
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QScrollArea, QPushButton
from app import Controller, Sound, set_autostart
from core import Settings
from tones import synthesize
from array import array
import math


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_settings_save_via_button_and_scroll(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Controller(self.app, folder, testing=True)
            c.open_settings()
            self.app.processEvents()
            scroll = c.preferences.findChild(QScrollArea)
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
            self.app.processEvents()
            save = next(b for b in c.preferences.findChildren(QPushButton) if b.text() == 'Simpan pengaturan')
            position = save.mapTo(scroll.viewport(), save.rect().center())
            self.assertTrue(scroll.viewport().rect().contains(position))
            c.preferences.low.setValue(30)
            c.preferences.high.setValue(90)
            with patch.object(c, 'poll'):
                QTest.mouseClick(save, Qt.MouseButton.LeftButton)
            self.assertEqual(c.settings.low, 30)
            self.assertTrue(c.config_file.exists())
            c.preferences.high.setValue(32)
            QTest.mouseClick(save, Qt.MouseButton.LeftButton)
            self.assertIn('5%', c.preferences.feedback.text())
            self.assertIn('#A8342B', c.preferences.feedback.styleSheet())
            self.assertEqual(c.settings.high, 90)
            c.preferences.close()
            c.widget.hide()
            c.tray.hide()

    @unittest.skipUnless(os.name == 'nt', 'Windows audio backend')
    def test_sound_file_format_and_volume(self):
        with tempfile.TemporaryDirectory() as folder:
            sound = Sound(Path(folder))
            with patch('winsound.PlaySound') as play:
                sound.play(Settings(volume=25))
                self.assertGreaterEqual(play.call_count, 2)
            with wave.open(str(Path(folder) / 'alarm.wav')) as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getframerate(), 22050)
                self.assertGreater(wav.getnframes(), 22050)

    @unittest.skipUnless(os.name == 'nt', 'Windows autostart backend')
    def test_windows_autostart_quoted_and_reversible(self):
        mock_key = MagicMock()
        with patch('sys.frozen', True, create=True), patch('sys.executable', r'C:\Program Files\Battery Cat\BatteryCat.exe'), patch('winreg.CreateKey', return_value=mock_key), patch('winreg.SetValueEx') as write, patch('winreg.DeleteValue') as delete:
            set_autostart(True)
            self.assertEqual(write.call_args.args[-1], '"C:\\Program Files\\Battery Cat\\BatteryCat.exe" --background')
            set_autostart(False)
            self.assertEqual(delete.call_args.args[-1], 'BatteryCat')

    def test_app_import_does_not_force_offscreen(self):
        # Regression: skins.py once set QT_QPA_PLATFORM=offscreen at import
        # time, turning the shipped app into an invisible ghost process.
        import subprocess
        import sys
        env = {k: v for k, v in os.environ.items() if k != 'QT_QPA_PLATFORM'}
        root = Path(__file__).resolve().parent
        code = "import os; import app; print(os.environ.get('QT_QPA_PLATFORM'))"
        proc = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, env=env, cwd=root)
        self.assertEqual(proc.stdout.strip().splitlines()[-1], 'None', proc.stderr)

    def test_skins_render_with_opaque_dial(self):
        from PySide6.QtGui import qAlpha
        from skins import render
        from core import SKINS
        self.assertEqual(len(SKINS), 5)
        for name in SKINS:
            if name == 'Kucing':
                continue
            img = render(name)
            self.assertFalse(img.isNull(), name)
            self.assertTrue(img.hasAlphaChannel(), name)
            self.assertEqual((img.width(), img.height()), (512, 512), name)
            # Dial center must be opaque so battery text stays readable.
            self.assertGreater(qAlpha(img.pixel(256, 315)), 200, name)
            # Corners must stay transparent (clickable-mask contract).
            self.assertEqual(qAlpha(img.pixel(4, 4)), 0, name)

    def test_strong_tones_louder_without_clipping(self):
        def rms(pcm):
            values = array('h', pcm)
            return math.sqrt(sum(v*v for v in values) / len(values))
        soft = rms(synthesize('Lembut', 100))
        for tone in ('Bip tegas', 'Bel nyaring', 'Sirene'):
            pcm = synthesize(tone, 100)
            self.assertGreater(rms(pcm), soft * 2)
            self.assertLess(max(abs(v) for v in array('h', pcm)), 32767)

    @unittest.skipUnless(os.name == 'nt', 'Windows audio backend')
    def test_low_sound_independent_from_target_sound(self):
        with tempfile.TemporaryDirectory() as folder:
            sound = Sound(Path(folder))
            s = Settings(sound=False, low_sound=True, low_tone='Sirene')
            with patch('winsound.PlaySound'), patch('app.synthesize', wraps=synthesize) as synth:
                sound.play(s, 'low')
                synth.assert_called_once_with('Sirene', s.volume)
                synth.reset_mock()
                sound.play(s, 'high')
                synth.assert_not_called()
            restored = Settings.parse({'sound': False, 'tone': 'Ceria'})
            self.assertTrue(restored.low_sound)
            self.assertEqual(restored.low_tone, 'Bip tegas')


if __name__ == '__main__':
    unittest.main()
