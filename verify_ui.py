"""Render real Qt widgets and exercise integration without changing user settings."""
import json
import os
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
from app import Controller, Battery

app = QApplication([])
app.setApplicationName('Battery Cat QA')
out = Path(__file__).resolve().parent / 'qa' / os.environ.get('BATTERYCAT_QA_VARIANT', '.')
out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=out) as folder:
    c = Controller(app, folder, testing=True)
    assert c.widget.image.hasAlphaChannel(), 'Artwork must have alpha transparency'
    c.battery = Battery(67, False, 9480)
    c.widget.show()
    c.refresh_labels()
    app.processEvents()
    c.widget.grab().save(str(out / 'widget-normal.png'))
    c.open_settings()
    app.processEvents()
    c.preferences.grab().save(str(out / 'settings.png'))
    c.preferences.low.setValue(25)
    c.preferences.high.setValue(85)
    with patch.object(c, 'poll'):
        c.preferences.commit()
    assert json.loads(c.config_file.read_text())['high'] == 85
    c.battery = Battery(23, False, 1800)
    c.evaluate()
    assert c.alarm is not None and c.engine.active == 'low'
    app.processEvents()
    c.widget.grab().save(str(out / 'widget-low.png'))
    c.alarm.grab().save(str(out / 'alarm-low.png'))
    c.snooze()
    assert c.alarm is None and c.engine.snoozed_until > time.monotonic()
    c.battery = Battery(86, True)
    c.evaluate()
    assert c.alarm is not None and c.engine.active == 'high'
    app.processEvents()
    c.alarm.grab().save(str(out / 'alarm-target.png'))
    c.acknowledge()
    c.evaluate()
    assert c.alarm is None
    c.battery = None
    c.evaluate()
    app.processEvents()
    c.widget.grab().save(str(out / 'widget-unavailable.png'))
    c.settings.size = 240
    c.widget.configure()
    c.battery = Battery(100, True)
    c.refresh_labels()
    app.processEvents()
    c.widget.grab().save(str(out / 'widget-small.png'))
    from core import SKINS
    for skin in SKINS:
        c.settings.skin = skin
        c.widget.load_image()
        assert not c.widget.image.isNull(), skin
        c.settings.size = 320
        c.widget.configure()
        c.battery = Battery(67, False, 9480)
        c.refresh_labels()
        app.processEvents()
        c.widget.grab().save(str(out / f'widget-skin-{skin}.png'))
    for px in (120, 72):
        c.settings.skin = 'Kucing'
        c.settings.size = px
        c.widget.load_image()
        c.widget.configure()
        c.battery = Battery(67, False, 9480)
        c.refresh_labels()
        app.processEvents()
        c.widget.grab().save(str(out / f'widget-{px}.png'))
    c.settings.sound = False
    c.preferences.close()
    c.widget.hide()
    c.tray.hide()
print('PASS: alpha, persistence, low alarm, snooze, charger transition, target alarm, acknowledge, missing battery, small widget, 5 skins, 120/72px tiers.')
