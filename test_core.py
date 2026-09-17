import unittest
from core import Settings, Battery, AlarmEngine, remaining_text, short_status


class AlarmTests(unittest.TestCase):
    def setUp(self):
        self.s = Settings()
        self.e = AlarmEngine()

    def test_low_only_unplugged_and_no_duplicates(self):
        self.assertIsNone(self.e.update(Battery(15, True), self.s, 0))
        self.assertEqual(self.e.update(Battery(15, False), self.s, 1), 'low')
        self.assertIsNone(self.e.update(Battery(14, False), self.s, 2))

    def test_full_while_plugged(self):
        self.assertIsNone(self.e.update(Battery(100, False), self.s, 0))
        self.assertEqual(self.e.update(Battery(100, True), self.s, 1), 'high')
        self.e.update(Battery(100, False), self.s, 2)
        self.assertIsNone(self.e.active)

    def test_plug_stops_low_and_next_session_rearms(self):
        self.e.update(Battery(19, False), self.s, 0)
        self.e.update(Battery(19, True), self.s, 1)
        self.assertIsNone(self.e.active)
        self.assertEqual(self.e.update(Battery(19, False), self.s, 2), 'low')

    def test_ack_and_hysteresis(self):
        self.e.update(Battery(20, False), self.s, 0)
        self.e.acknowledge()
        self.e.update(Battery(21, False), self.s, 1)
        self.assertIsNone(self.e.update(Battery(20, False), self.s, 2))
        self.e.update(Battery(23, False), self.s, 3)
        self.assertEqual(self.e.update(Battery(20, False), self.s, 4), 'low')

    def test_snooze(self):
        self.e.update(Battery(18, False), self.s, 100)
        self.e.snooze(100, 5)
        self.assertIsNone(self.e.update(Battery(17, False), self.s, 399))
        self.assertEqual(self.e.update(Battery(17, False), self.s, 400), 'low')

    def test_custom_target_and_skipped_percentage(self):
        self.s.high = 80
        self.e.update(Battery(79, True), self.s, 0)
        self.assertEqual(self.e.update(Battery(82, True), self.s, 1), 'high')

    def test_pause_missing_and_invalid(self):
        self.e.update(Battery(18, False), self.s, 0)
        self.assertIsNone(self.e.update(None, self.s, 1))
        self.assertIsNone(self.e.active)
        self.assertIsNone(self.e.update(Battery(float('nan'), False), self.s, 2))
        self.s.enabled = False
        self.assertIsNone(self.e.update(Battery(10, False), self.s, 3))

    def test_defensive_settings(self):
        s = Settings.parse({'low': 99, 'high': 3, 'size': 1, 'volume': -5, 'sound': 'false', 'tone': '<bad>'})
        self.assertEqual((s.low, s.high, s.size, s.volume, s.sound, s.tone), (60, 65, 72, 0, True, 'Lembut'))
        self.assertEqual(Settings.parse([]), Settings())

    def test_unknown_estimate(self):
        self.assertIn('belum tersedia', remaining_text(Battery(50, False, -1)))
        self.assertIn('1 jam 30 menit', remaining_text(Battery(50, False, 5400)))

    def test_skin_and_small_sizes(self):
        s = Settings.parse({'skin': 'Katak', 'size': 72})
        self.assertEqual((s.skin, s.size), ('Katak', 72))
        s = Settings.parse({'skin': 'Panda', 'size': 120})
        self.assertEqual((s.skin, s.size), ('Panda', 120))
        s = Settings.parse({'skin': '<bad>', 'size': 1})
        self.assertEqual((s.skin, s.size), ('Kucing', 72))

    def test_short_status(self):
        self.assertEqual(short_status('Menggunakan baterai'), 'Baterai')
        self.assertEqual(short_status('Charger terhubung'), 'Charging')
        self.assertEqual(short_status('Baterai penuh'), 'Penuh')
        self.assertEqual(short_status('Pemantauan dijeda'), 'Jeda')
        self.assertEqual(short_status('Pengingat ditunda'), 'Tunda')
        self.assertEqual(short_status('Gagal membaca baterai'), 'Error')


if __name__ == '__main__':
    unittest.main()
