"""Reproducible platform-local PyInstaller build; no runtime download needed by users."""
from pathlib import Path
import os
import subprocess
import sys

root = Path(__file__).resolve().parent
os.chdir(root)
subprocess.run([sys.executable, '-m', 'unittest', '-v'], check=True)
args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--onedir', '--name', 'BatteryCat',
        '--add-data', f'assets{os.pathsep}assets', '--add-data', f'THIRD-PARTY-NOTICES.md{os.pathsep}.',
        '--add-data', f'README.md{os.pathsep}.', '--copy-metadata', 'psutil',
        '--exclude-module', 'PySide6.QtNetwork', '--exclude-module', 'PySide6.QtQml', '--exclude-module', 'PySide6.QtQuick',
        '--exclude-module', 'PySide6.QtOpenGL', '--exclude-module', 'PySide6.QtPdf', '--exclude-module', 'PySide6.QtDesigner']
if sys.platform == 'win32':
    args += ['--icon', 'assets/cat-clock.ico', '--version-file', 'version.txt']
args.append('app.py')
subprocess.run(args, check=True)
if sys.platform == 'win32':
    # Remove only files installed by this package. User files in InstallDir survive uninstall.
    base = root / 'dist/BatteryCat'
    lines = []
    for path in sorted(base.rglob('*')):
        if path.is_file():
            relative = str(path.relative_to(base)).replace('/', '\\')
            lines.append(f'  Delete "$INSTDIR\\{relative}"')
    dirs = sorted([p for p in base.rglob('*') if p.is_dir()], key=lambda p: len(p.parts), reverse=True)
    lines += [f'  RMDir "$INSTDIR\\{str(p.relative_to(base))}"' for p in dirs]
    (root / 'uninstall-files.nsh').write_text('\n'.join(lines), encoding='utf-8')
print('Build finished:', root / 'dist')
