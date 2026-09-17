from pathlib import Path
import hashlib
import zipfile

root = Path(__file__).resolve().parent
release = root / 'release'
release.mkdir(exist_ok=True)
destination = release / 'Battery-Cat-1.1.2-Source.zip'
excluded = {'.venv', 'dist', 'build', 'release', 'qa', '__pycache__'}
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if path.is_file() and not any(part in excluded for part in relative.parts) and path.suffix not in {'.spec', '.pyc'}:
            archive.write(path, Path('BatteryCat') / relative)
artifacts = [release / 'Battery-Cat-1.1.2-Windows-x64-Setup.exe', destination]
lines = [hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name for path in artifacts]
(release / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
for path in artifacts:
    print(path.name, path.stat().st_size, 'bytes')
