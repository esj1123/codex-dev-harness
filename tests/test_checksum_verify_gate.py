from pathlib import Path
import shutil

from scripts import generate_checksums
from scripts.gates import checksum_verify_gate


REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_release_evidence(target_root: Path) -> None:
    relative_paths = [
        *generate_checksums.REQUIRED_RELEASE_ARTIFACTS,
        *generate_checksums.OPTIONAL_RELEASE_ARTIFACTS,
        generate_checksums.DEFAULT_CHECKSUMS_PATH,
    ]
    for relative_path in relative_paths:
        source = REPO_ROOT / relative_path
        if not source.is_file():
            continue
        target = target_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def test_checksum_verify_gate_passes_current_tree() -> None:
    result = checksum_verify_gate.run(REPO_ROOT)

    assert result.name == "checksum_verify_gate"
    assert result.passed is True
    assert "verified checksum entries: 5" in result.messages


def test_checksum_verify_gate_fails_for_tampered_temp_copy(tmp_path: Path) -> None:
    copy_release_evidence(tmp_path)
    assert checksum_verify_gate.run(tmp_path).passed is True
    manifest = tmp_path / generate_checksums.DEFAULT_MANIFEST_PATH
    manifest.write_bytes(manifest.read_bytes() + b"\n")

    result = checksum_verify_gate.run(tmp_path)

    assert result.passed is False
    assert any(
        message.startswith("MISMATCH artifacts/release-manifest.json")
        for message in result.messages
    )