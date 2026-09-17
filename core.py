"""Platform-independent battery alarm decisions. No GUI or polling side effects."""
from dataclasses import dataclass, asdict
import math

TONES = ('Lembut', 'Ceria', 'Bip tegas', 'Bel nyaring', 'Sirene')

SKINS = ('Kucing', 'Beruang', 'Kelinci', 'Katak', 'Panda')

# Widget sizes offered in the UI: (label, pixels). 72/120 use compact
# text tiers so the percentage stays legible on tiny widgets.
SIZES = (('Mungil · 72 px', 72), ('Mini · 120 px', 120), ('Kecil · 240 px', 240),
         ('Sedang · 320 px', 320), ('Besar · 400 px', 400))


@dataclass
class Settings:
    low: int = 20
    high: int = 100
    enabled: bool = True
    sound: bool = True
    low_sound: bool = True
    volume: int = 65
    tone: str = 'Lembut'
    low_tone: str = 'Bip tegas'
    snooze: int = 5
    size: int = 320
    skin: str = 'Kucing'
    topmost: bool = False
    autostart: bool = False
    x: int | None = None
    y: int | None = None

    @classmethod
    def parse(cls, data):
        s = cls()
        if not isinstance(data, dict):
            return s
        for key in asdict(s):
            if key not in data:
                continue
            v = data[key]
            if key in ('enabled', 'sound', 'low_sound', 'topmost', 'autostart') and type(v) is bool:
                setattr(s, key, v)
            elif key in ('low', 'high', 'volume', 'snooze', 'size', 'x', 'y') and type(v) is int:
                setattr(s, key, v)
            elif key in ('tone', 'low_tone') and v in TONES:
                setattr(s, key, v)
            elif key == 'skin' and v in SKINS:
                setattr(s, key, v)
        s.low = max(5, min(60, s.low))
        s.high = max(s.low + 5, min(100, s.high))
        s.volume = max(0, min(100, s.volume))
        s.snooze = max(1, min(60, s.snooze))
        s.size = max(72, min(440, s.size))
        return s


@dataclass
class Battery:
    percent: float
    plugged: bool
    seconds: int = -1

    def valid(self):
        return math.isfinite(self.percent) and 0 <= self.percent <= 100


class AlarmEngine:
    def __init__(self):
        self.latched = set()
        self.active = None
        self.snoozed_until = 0
        self.previous_plugged = None

    def reset(self):
        self.__init__()

    def acknowledge(self):
        self.active = None
        self.snoozed_until = 0

    def snooze(self, now, minutes):
        if self.active:
            self.latched.discard(self.active)
        self.active = None
        self.snoozed_until = now + minutes * 60

    def update(self, battery, settings, now):
        if not settings.enabled or battery is None or not battery.valid():
            self.active = None
            return None
        if self.previous_plugged is not None and battery.plugged != self.previous_plugged:
            self.reset()
        self.previous_plugged = battery.plugged
        if battery.percent >= settings.low + 3:
            self.latched.discard('low')
        if battery.percent <= settings.high - 3:
            self.latched.discard('high')
        kind = ('low' if not battery.plugged and battery.percent <= settings.low else
                'high' if battery.plugged and battery.percent >= settings.high else None)
        if self.active != kind:
            self.active = None
        if kind and kind not in self.latched and now >= self.snoozed_until:
            self.latched.add(kind)
            self.active = kind
            return kind
        return None


def status_text(battery):
    if battery is None:
        return 'Baterai tidak tersedia'
    if battery.plugged:
        return 'Baterai penuh' if battery.percent >= 100 else 'Charger terhubung'
    return 'Menggunakan baterai'


def short_status(state):
    """Compact one-word status for tiny widgets (72/120 px).

    Takes the full status line (or state keyword) and returns a short
    label that stays legible at ~9 px.
    """
    mapping = {
        'Baterai penuh': 'Penuh',
        'Charger terhubung': 'Charging',
        'Menggunakan baterai': 'Baterai',
        'Baterai tidak tersedia': '—',
        'Pemantauan dijeda': 'Jeda',
        'Pengingat ditunda': 'Tunda',
        'Gagal membaca baterai': 'Error',
    }
    return mapping.get(state, state)


def remaining_text(battery):
    if battery is None:
        return 'Periksa baterai perangkat'
    if battery.plugged:
        return 'Daya tersambung'
    if battery.seconds < 0:
        return 'Estimasi belum tersedia'
    minutes = max(1, battery.seconds // 60)
    h, m = divmod(minutes, 60)
    return f'Est. {h} jam {m} menit' if h else f'Est. {m} menit tersisa'
