"""Package only reviewed source, teaching material and synthetic data for the owner."""
import json
from pathlib import Path
import zipfile

from source_manifest import source_files, manifest

ROOT = Path(__file__).resolve().parents[1]


def package_source():
    destination = ROOT / "outputs" / "signal-ledger-source.zip"
    destination.parent.mkdir(exist_ok=True)
    records = manifest()
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in source_files():
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("SOURCE_MANIFEST.json", json.dumps(records, indent=2))
    return destination, len(records)


if __name__ == "__main__":
    destination, count = package_source()
    print(f"Packaged {count} reviewed files: {destination}")
