# Battery Cat 1.1.2

Widget kepala kucing untuk mengingatkan baterai laptop. Bekerja offline, tanpa akun, server, atau telemetri.

## Memasang di Windows

Jalankan `Battery-Cat-1.1.2-Windows-x64-Setup.exe`, ikuti petunjuk, lalu buka Battery Cat. Mendukung Windows 10/11 x64. Python dan Qt sudah disertakan; tidak perlu memasangnya sendiri. Installer ini belum ditandatangani dengan sertifikat penerbit.

## Pembaruan 1.1.2

Perbaikan penting: aplikasi yang dipasang kini tampil normal (sebelumnya berjalan tak terlihat di latar). Tutup versi lama lewat Task Manager bila perlu, lalu pasang versi ini.

## Pembaruan 1.1.1

Lima skin hewan: Kucing, Beruang, Kelinci, Katak, dan Panda, dapat diganti lewat Pengaturan. Ukuran widget baru Mini 120 px dan Mungil 72 px; pada ukuran kecil, widget menampilkan persen besar, status satu kata, dan batas alarm ringkas agar tetap terbaca. Pengaturan lama tetap digunakan; skin awal Kucing dan ukuran lama tidak berubah.

## Pembaruan 1.1

Tiga nada tambahan: Bip tegas, Bel nyaring, dan Sirene. Suara baterai rendah dan target pengisian dapat diaktifkan dan dipilih secara terpisah, masing-masing dengan tombol tes. Volume berlaku untuk kedua alarm. Pilihan keras memakai sinyal lebih kuat dan durasi sekitar 7 detik; tetap mengikuti volume dan mute Windows. Pengaturan lama tetap digunakan; suara rendah baru aktif secara default dengan Bip tegas.

Teks Rendah dan Target sekarang dua baris di dalam lingkaran, dengan ukuran huruf yang mengikuti widget secara konsisten pada skala layar berbeda.

Tutup Battery Cat melalui menu Keluar sebelum memasang pembaruan ke folder yang sama.

## Menggunakan

- Geser kepala kucing untuk memindahkannya. Posisi disimpan otomatis.
- Klik dua kali kepala kucing untuk membuka pengaturan. Klik kanan untuk menu.
- Batas awal: alarm rendah 20%, target pengisian 100%. Target bisa diubah hingga 100%.
- Alarm rendah hanya aktif ketika charger tidak terhubung; alarm target hanya saat charger terhubung.
- Bunyi alarm berlangsung beberapa detik. Jendela peringatan tetap muncul sampai dihentikan, ditunda, atau kondisinya berakhir. Menutup peringatan sama dengan menghentikan alarm untuk kondisi tersebut.
- Tombol Tunda memunculkan pengingat kembali setelah durasi pilihan jika kondisi masih berlaku.
- Sembunyikan widget melalui menu; pemantauan tetap berjalan. Klik ikon di dekat jam untuk menampilkan kembali.
- Opsi mulai otomatis hanya aktif jika dipilih. Saat login, aplikasi mulai di tray; klik ikon untuk membuka kucing.
- Pilih skin hewan (Kucing, Beruang, Kelinci, Katak, Panda) dan ukuran widget hingga sekecil 72 px di Pengaturan. Pada ukuran kecil, widget menampilkan persen besar agar tetap terbaca; detail lengkap tersedia di tooltip dan menu.
- Pilih Keluar Battery Cat untuk menghentikan aplikasi sepenuhnya.
- Gunakan Add/Remove Programs atau pintasan Uninstall untuk menghapus aplikasi. Tutup Battery Cat lebih dahulu. Preferensi pengguna tetap disimpan.

## Informasi dan batasan

Persentase dan estimasi berasal dari OS. Charger terhubung tidak selalu berarti baterai sedang diisi. Estimasi waktu bukan jaminan dan dapat tidak tersedia. Aplikasi memeriksa baterai setiap 15 detik; sesudah sleep akan memeriksa lagi ketika proses dilanjutkan. Alarm tidak berjalan selama laptop sleep atau mati. Suara mengikuti volume/mute perangkat. Aplikasi ini mengingatkan, tidak memutus arus listrik atau mengubah batas charge firmware. Jika ada beberapa baterai, data mengikuti agregat OS yang disediakan psutil.

Pengaturan Windows berada di `%APPDATA%\BatteryCat\Battery Cat\settings.json`. Batas pengisian harus minimal 5% di atas batas rendah. Pencegahan alarm berulang memakai toleransi 3% atau sesi charger baru.

## Pengembang / OS lain

Kode memakai Python 3.11+, PySide6 Essentials 6.8.3 dan psutil 7.2.2. Windows adalah target installer yang diverifikasi pada pengerjaan ini. macOS dan Linux memerlukan build serta pengujian di OS masing-masing; belum tersedia installer terverifikasi untuk keduanya. Linux perlu dukungan tray pada desktop dan `paplay` atau `aplay` untuk suara nada; jika tidak ada, aplikasi memakai bunyi sistem. Perilaku transparansi, posisi, dan selalu di atas bergantung compositor, terutama Wayland.

```text
python -m venv .venv
# Aktifkan lingkungan sesuai OS, lalu:
python -m pip install -r requirements.txt
python app.py
python -m unittest -v
python build.py
```

Windows: kompilasi `installer.nsi` menggunakan NSIS 3 setelah build. `verify_ui.py` menguji UI secara terisolasi. Mode `--smoke-test <report.json>` memeriksa executable dengan data sementara tanpa menulis pengaturan pengguna.

Kode aplikasi disediakan bersama proyek dan boleh diubah untuk kebutuhan pribadi. Dependensi mempertahankan lisensinya masing-masing; lihat THIRD-PARTY-NOTICES.md.
