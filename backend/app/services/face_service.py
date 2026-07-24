from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass

import numpy as np

try:  # pragma: no cover - optional runtime dependency
    import cv2
except Exception:  # pragma: no cover - fallback if OpenCV is unavailable at runtime
    cv2 = None

try:  # pragma: no cover - optional runtime dependency
    from insightface.app import FaceAnalysis
except Exception:  # pragma: no cover - fallback if InsightFace is unavailable at runtime
    FaceAnalysis = None

from app.core.config import settings


@dataclass
class FaceAnalysisResult:
    embedding: bytes
    similarity: float | None
    liveness_score: float
    quality_score: int
    face_count: int
    used_fallback: bool = False


class FaceServiceError(RuntimeError):
    pass


class FaceService:
    def __init__(self) -> None:
        self._model = None
        self._model_loaded = False

    def _ensure_model(self):
        if self._model_loaded:
            return self._model
        self._model_loaded = True

        if FaceAnalysis is None:
            self._model = None
            return None

        providers = ["CPUExecutionProvider"]
        try:
            self._model = FaceAnalysis(name=settings.face_model_name, providers=providers)
            self._model.prepare(ctx_id=0, det_size=(640, 640))
        except Exception as exc:  # pragma: no cover - runtime safety
            self._model = None
            raise FaceServiceError(f"Gagal memuat InsightFace: {exc}") from exc
        return self._model

    def _decode_image(self, image_bytes: bytes) -> np.ndarray:
        if cv2 is None:
            raise FaceServiceError("OpenCV tidak tersedia di runtime")
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise FaceServiceError("Gagal membaca gambar")
        return image

    def decode_base64(self, image_base64: str) -> bytes:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        try:
            return base64.b64decode(image_base64, validate=True)
        except Exception as exc:
            raise FaceServiceError("Format base64 tidak valid") from exc

    def _quality_score(self, image: np.ndarray) -> int:
        if cv2 is None:
            return 80
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        score = 100
        if brightness < 70:
            score -= 25
        elif brightness > 200:
            score -= 10
        if blur < 80:
            score -= 25
        if min(image.shape[:2]) < 160:
            score -= 20
        return max(0, min(score, 100))

    def _liveness_score(self, image: np.ndarray, face_count: int) -> float:
        if cv2 is None:
            return 0.90
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        score = 0.95
        if face_count != 1:
            score -= 0.3
        if blur < 80:
            score -= 0.2
        if brightness < 70 or brightness > 220:
            score -= 0.15
        return round(max(0.0, min(score, 1.0)), 3)

    def _fallback_embedding(self, image_bytes: bytes) -> bytes:
        digest = hashlib.sha256(image_bytes).digest()
        return np.frombuffer(digest * 8, dtype=np.uint8).astype(np.float32).tobytes()

    def _embedding_from_face(self, face) -> bytes:
        return face.embedding.astype(np.float32).tobytes()

    @staticmethod
    def _vector_from_bytes(embedding: bytes) -> np.ndarray:
        return np.frombuffer(embedding, dtype=np.float32)

    @staticmethod
    def cosine_similarity(left: bytes, right: bytes) -> float:
        left_vec = FaceService._vector_from_bytes(left)
        right_vec = FaceService._vector_from_bytes(right)
        if left_vec.size == 0 or right_vec.size == 0:
            return 0.0
        denom = float(np.linalg.norm(left_vec) * np.linalg.norm(right_vec))
        if denom == 0.0:
            return 0.0
        return float(np.dot(left_vec, right_vec) / denom)

    def enroll(self, image_bytes: bytes) -> FaceAnalysisResult:
        image = self._decode_image(image_bytes)
        quality = self._quality_score(image)
        model = self._ensure_model()

        if model is None:
            return FaceAnalysisResult(
                embedding=self._fallback_embedding(image_bytes),
                similarity=None,
                liveness_score=0.80,
                quality_score=quality,
                face_count=1,
                used_fallback=True,
            )

        faces = model.get(image)
        if len(faces) != 1:
            raise FaceServiceError("Wajib tepat satu wajah pada frame enrollment")

        face = faces[0]
        return FaceAnalysisResult(
            embedding=self._embedding_from_face(face),
            similarity=None,
            liveness_score=self._liveness_score(image, len(faces)),
            quality_score=quality,
            face_count=len(faces),
            used_fallback=False,
        )

    def verify(self, reference_embedding: bytes, image_bytes: bytes) -> FaceAnalysisResult:
        image = self._decode_image(image_bytes)
        quality = self._quality_score(image)
        model = self._ensure_model()

        if model is None:
            candidate_embedding = self._fallback_embedding(image_bytes)
            similarity = self.cosine_similarity(reference_embedding, candidate_embedding)
            return FaceAnalysisResult(
                embedding=candidate_embedding,
                similarity=similarity,
                liveness_score=0.80,
                quality_score=quality,
                face_count=1,
                used_fallback=True,
            )

        faces = model.get(image)
        if len(faces) != 1:
            raise FaceServiceError("Wajib tepat satu wajah pada frame verifikasi")

        face = faces[0]
        candidate_embedding = self._embedding_from_face(face)
        similarity = self.cosine_similarity(reference_embedding, candidate_embedding)
        return FaceAnalysisResult(
            embedding=candidate_embedding,
            similarity=similarity,
            liveness_score=self._liveness_score(image, len(faces)),
            quality_score=quality,
            face_count=len(faces),
            used_fallback=False,
        )


face_service = FaceService()

