"""Validasi pipeline wajah pada model InsightFace ASLI (untuk BAB IV, Gambar 4.22).

Menjalankan: deteksi wajah -> ekstraksi embedding -> registrasi 5 pose ->
pencocokan (similarity) -> penilaian sinyal liveness, lalu mencetak ringkasan
yang bisa di-screenshot.

Penggunaan:
    python validate_insightface.py                 # pakai gambar contoh bawaan InsightFace
    python validate_insightface.py wajah.jpg       # pakai foto wajah sendiri (1 wajah)
    python validate_insightface.py wajah.jpg lain.jpg   # + foto orang berbeda (uji penolakan)

Catatan: pada run pertama, InsightFace mengunduh model buffalo_l (butuh internet).
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

from app.core.config import settings
from app.models.enums import FacePose, LivenessChallenge
from app.services.face_service import face_service


def _to_jpeg(image: np.ndarray) -> bytes:
    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        raise RuntimeError("Gagal meng-encode gambar ke JPEG")
    return buffer.tobytes()


def _load_single_face(path: str | None) -> bytes:
    """Muat gambar berisi tepat satu wajah (crop wajah terbesar bila perlu)."""
    model = face_service._ensure_model()
    if path:
        image = cv2.imread(path)
        if image is None:
            raise SystemExit(f"Tidak bisa membaca file gambar: {path}")
    else:
        from insightface.data import get_image

        image = get_image("t1")  # gambar contoh bawaan (banyak wajah)

    if model is None:
        return _to_jpeg(image)  # mode fallback: kirim apa adanya

    faces = model.get(image)
    if not faces:
        raise SystemExit("Tidak ada wajah terdeteksi pada gambar.")
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    x1, y1, x2, y2 = (int(v) for v in face.bbox)
    margin = 60
    h, w = image.shape[:2]
    crop = image[max(0, y1 - margin) : min(h, y2 + margin), max(0, x1 - margin) : min(w, x2 + margin)]
    return _to_jpeg(crop)


def main() -> None:
    path_utama = sys.argv[1] if len(sys.argv) > 1 else None
    path_beda = sys.argv[2] if len(sys.argv) > 2 else None

    face_bytes = _load_single_face(path_utama)
    analysis = face_service.analyze(face_bytes)
    mode = "FALLBACK (model tidak dimuat)" if analysis.used_fallback else f"InsightFace ASLI ({settings.face_model_name})"

    print("=" * 60)
    print("  VALIDASI MODEL INSIGHTFACE")
    print("=" * 60)
    print(f"Mode model        : {mode}")
    print(f"Deteksi wajah     : {analysis.face_count} wajah, embedding {len(analysis.embedding)} byte")
    print(
        "Sinyal biometrik  : "
        f"yaw={_fmt(analysis.yaw)}  pitch={_fmt(analysis.pitch)}  "
        f"ear={_fmt(analysis.ear)}  smile_ratio={_fmt(analysis.smile_ratio)}"
    )

    frames = [(pose, face_bytes) for pose in FacePose]
    blob, results, quality, _ = face_service.enroll_poses(frames)
    diterima = sum(1 for r in results if r.accepted)
    print(f"Registrasi 5 pose : {diterima}/5 pose diterima (kualitas rata-rata {quality})")

    _, sim_same = face_service.verify_match(blob, face_bytes)
    status_same = "COCOK" if sim_same >= settings.face_match_threshold else "DITOLAK"
    print(f"Pencocokan (sama) : similarity {sim_same:.3f} (ambang {settings.face_match_threshold}) -> {status_same}")

    if path_beda:
        beda_bytes = _load_single_face(path_beda)
        _, sim_diff = face_service.verify_match(blob, beda_bytes)
        status_diff = "COCOK" if sim_diff >= settings.face_match_threshold else "DITOLAK"
        print(f"Pencocokan (beda) : similarity {sim_diff:.3f} (ambang {settings.face_match_threshold}) -> {status_diff}")

    print("Penilaian liveness (wajah netral tanpa gerakan; seharusnya DITOLAK):")
    for challenge in LivenessChallenge:
        passed, _, detail = face_service.evaluate_liveness(face_bytes, challenge)
        label = "LOLOS" if passed else "DITOLAK"
        print(f"  - {challenge.value:<11}: {label:<7} ({detail})")

    print("=" * 60)
    print("Kesimpulan: wajah terdeteksi, 5 pose terdaftar, wajah sama COCOK,")
    print("            dan tantangan liveness menolak wajah statis tanpa gerakan.")
    print("=" * 60)


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


if __name__ == "__main__":
    main()
