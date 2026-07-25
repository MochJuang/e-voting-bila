"""Utilitas bersama untuk test."""

from __future__ import annotations

import base64

import cv2
import numpy as np

API = "/api/v1"


def make_face_b64(seed: int = 0) -> str:
    """Buat citra JPEG (base64) deterministik untuk uji — dipakai sebagai 'wajah'.

    Pada mode fallback (tanpa model InsightFace), embedding dihitung dari byte citra
    sehingga citra yang sama menghasilkan embedding identik, dan citra berbeda
    menghasilkan embedding berbeda.
    """
    rng = np.random.default_rng(seed)
    img = rng.integers(90, 160, (224, 224, 3), dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", img)
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def frame_bytes(seed: int = 0) -> bytes:
    return base64.b64decode(make_face_b64(seed).split(",", 1)[1])
