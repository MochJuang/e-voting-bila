from __future__ import annotations

import base64
import hashlib
import io
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
from app.models.enums import FacePose, LivenessChallenge


@dataclass
class FaceFrameAnalysis:
    """Hasil analisa satu frame wajah."""

    embedding: bytes
    quality_score: int
    liveness_score: float
    face_count: int
    used_fallback: bool
    yaw: float | None = None  # + = menoleh ke kiri layar, - = kanan (mirror kamera depan)
    pitch: float | None = None  # + = menunduk, - = mendongak (perkiraan)
    ear: float | None = None  # eye openness ratio
    smile_ratio: float | None = None  # rasio lebar mulut / jarak antar-mata


@dataclass
class PoseEnrollResult:
    pose: FacePose
    accepted: bool
    quality_score: int
    message: str


class FaceServiceError(RuntimeError):
    pass


class FaceService:
    def __init__(self) -> None:
        self._model = None
        self._model_loaded = False
        self._model_error: str | None = None

    # ------------------------------------------------------------------ #
    # Model & image helpers
    # ------------------------------------------------------------------ #
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
            # Model tidak bisa dimuat (mis. belum ter-download / offline).
            # Degradasi ke mode fallback alih-alih menggagalkan seluruh request.
            self._model = None
            self._model_error = str(exc)
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

    def _base_liveness(self, image: np.ndarray, face_count: int) -> float:
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

    # ------------------------------------------------------------------ #
    # Embedding (multi-pose) packing helpers
    # ------------------------------------------------------------------ #
    _NPY_MAGIC = b"\x93NUMPY"

    @staticmethod
    def pack_embeddings(embeddings: list[np.ndarray]) -> bytes:
        """Simpan beberapa embedding pose sebagai satu blob (matriks N x D)."""
        matrix = np.vstack([np.asarray(e, dtype=np.float32).reshape(1, -1) for e in embeddings])
        buffer = io.BytesIO()
        np.save(buffer, matrix, allow_pickle=False)
        return buffer.getvalue()

    @classmethod
    def unpack_embeddings(cls, blob: bytes) -> np.ndarray:
        """Baca blob embedding menjadi matriks N x D.

        Kompatibel mundur: blob lama (single embedding, raw float32) tetap terbaca.
        """
        if blob[: len(cls._NPY_MAGIC)] == cls._NPY_MAGIC:
            matrix = np.load(io.BytesIO(blob), allow_pickle=False)
            return np.atleast_2d(matrix).astype(np.float32)
        # Format lama: satu vektor float32 mentah
        vector = np.frombuffer(blob, dtype=np.float32)
        return vector.reshape(1, -1) if vector.size else np.zeros((1, 1), dtype=np.float32)

    @staticmethod
    def _cosine(a: np.ndarray, b: np.ndarray) -> float:
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0.0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def best_similarity(self, reference_blob: bytes, candidate_embedding: bytes) -> float:
        """Similarity tertinggi antara kandidat vs semua embedding pose tersimpan."""
        reference = self.unpack_embeddings(reference_blob)
        candidate = np.frombuffer(candidate_embedding, dtype=np.float32)
        if candidate.size == 0:
            return 0.0
        best = 0.0
        for row in reference:
            if row.size != candidate.size:
                continue
            best = max(best, self._cosine(row, candidate))
        return round(best, 3)

    def _fallback_embedding(self, image_bytes: bytes) -> bytes:
        digest = hashlib.sha256(image_bytes).digest()
        return np.frombuffer(digest * 8, dtype=np.uint8).astype(np.float32).tobytes()

    # ------------------------------------------------------------------ #
    # Landmark-derived signals (pose, blink, smile)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _pose_from_face(face) -> tuple[float | None, float | None]:
        pose = getattr(face, "pose", None)
        if pose is None:
            return None, None
        try:
            pitch, yaw = float(pose[0]), float(pose[1])
        except Exception:
            return None, None
        return yaw, pitch

    @staticmethod
    def _cluster_extent(points: np.ndarray, center: np.ndarray, radius: float):
        dist = np.linalg.norm(points - center, axis=1)
        selected = points[dist <= radius]
        if len(selected) < 3:
            return None
        width = float(selected[:, 0].max() - selected[:, 0].min())
        height = float(selected[:, 1].max() - selected[:, 1].min())
        return width, height

    def _blink_smile_from_face(self, face) -> tuple[float | None, float | None]:
        """Perkiraan EAR (kedip) & smile-ratio secara index-agnostic dari landmark_2d_106.

        Memakai keypoint mata/mulut (face.kps) sebagai pusat cluster landmark, sehingga
        tidak bergantung pada nomor index landmark tertentu. Nilai bersifat perkiraan dan
        threshold-nya dapat dikalibrasi lewat konfigurasi.
        """
        landmarks = getattr(face, "landmark_2d_106", None)
        kps = getattr(face, "kps", None)
        if landmarks is None or kps is None or len(kps) < 5:
            return None, None

        landmarks = np.asarray(landmarks, dtype=np.float32)
        kps = np.asarray(kps, dtype=np.float32)
        left_eye, right_eye = kps[0], kps[1]
        left_mouth, right_mouth = kps[3], kps[4]

        interocular = float(np.linalg.norm(left_eye - right_eye)) or 1.0
        eye_radius = interocular * 0.35
        mouth_radius = interocular * 0.6

        ears = []
        for eye_center in (left_eye, right_eye):
            extent = self._cluster_extent(landmarks, eye_center, eye_radius)
            if extent and extent[0] > 0:
                ears.append(extent[1] / extent[0])  # height / width
        ear = float(min(ears)) if ears else None

        mouth_width = float(np.linalg.norm(left_mouth - right_mouth))
        smile_ratio = mouth_width / interocular if interocular else None

        return ear, smile_ratio

    # ------------------------------------------------------------------ #
    # Core analysis
    # ------------------------------------------------------------------ #
    def analyze(self, image_bytes: bytes) -> FaceFrameAnalysis:
        image = self._decode_image(image_bytes)
        quality = self._quality_score(image)
        model = self._ensure_model()

        if model is None:
            return FaceFrameAnalysis(
                embedding=self._fallback_embedding(image_bytes),
                quality_score=quality,
                liveness_score=0.80,
                face_count=1,
                used_fallback=True,
            )

        faces = model.get(image)
        if len(faces) == 0:
            raise FaceServiceError("Wajah tidak terdeteksi pada frame")
        if len(faces) > 1:
            raise FaceServiceError("Terdeteksi lebih dari satu wajah pada frame")

        face = faces[0]
        yaw, pitch = self._pose_from_face(face)
        ear, smile_ratio = self._blink_smile_from_face(face)
        return FaceFrameAnalysis(
            embedding=face.embedding.astype(np.float32).tobytes(),
            quality_score=quality,
            liveness_score=self._base_liveness(image, len(faces)),
            face_count=len(faces),
            used_fallback=False,
            yaw=yaw,
            pitch=pitch,
            ear=ear,
            smile_ratio=smile_ratio,
        )

    # ------------------------------------------------------------------ #
    # Enrollment (multi-pose)
    # ------------------------------------------------------------------ #
    def _pose_matches(self, pose: FacePose, analysis: FaceFrameAnalysis) -> tuple[bool, str]:
        """Validasi arah kepala untuk pose enrollment (hanya saat model tersedia)."""
        if analysis.used_fallback or analysis.yaw is None or analysis.pitch is None:
            return True, "Pose diterima (mode simulasi tanpa validasi arah)."

        yaw, pitch = analysis.yaw, analysis.pitch
        yaw_t = settings.enroll_pose_yaw_threshold
        pitch_t = settings.enroll_pose_pitch_threshold

        if pose == FacePose.CENTER:
            if abs(yaw) <= yaw_t and abs(pitch) <= pitch_t:
                return True, "Pose tengah terdeteksi."
            return False, "Hadapkan wajah lurus ke kamera (tengah)."
        if pose == FacePose.LEFT:
            if yaw >= yaw_t:
                return True, "Pose menghadap kiri terdeteksi."
            return False, "Tolehkan kepala ke kiri lebih jauh."
        if pose == FacePose.RIGHT:
            if yaw <= -yaw_t:
                return True, "Pose menghadap kanan terdeteksi."
            return False, "Tolehkan kepala ke kanan lebih jauh."
        if pose == FacePose.UP:
            if pitch <= -pitch_t:
                return True, "Pose mendongak terdeteksi."
            return False, "Angkat dagu / dongakkan kepala ke atas."
        if pose == FacePose.DOWN:
            if pitch >= pitch_t:
                return True, "Pose menunduk terdeteksi."
            return False, "Tundukkan kepala ke bawah."
        return True, "Pose diterima."

    def enroll_poses(
        self, frames: list[tuple[FacePose, bytes]]
    ) -> tuple[bytes, list[PoseEnrollResult], int, bool]:
        """Analisa semua pose, kembalikan blob embedding + detail per pose."""
        embeddings: list[np.ndarray] = []
        results: list[PoseEnrollResult] = []
        qualities: list[int] = []
        used_fallback = False
        rejected: list[str] = []

        for pose, image_bytes in frames:
            try:
                analysis = self.analyze(image_bytes)
            except FaceServiceError as exc:
                results.append(PoseEnrollResult(pose, False, 0, str(exc)))
                rejected.append(f"{pose.value}: {exc}")
                continue

            used_fallback = used_fallback or analysis.used_fallback
            ok, message = self._pose_matches(pose, analysis)
            # Arah pose bersifat advisory kecuali di-enforce lewat konfigurasi.
            accepted = ok or not settings.enroll_enforce_pose_direction
            qualities.append(analysis.quality_score)
            results.append(PoseEnrollResult(pose, accepted, analysis.quality_score, message))
            if accepted:
                embeddings.append(np.frombuffer(analysis.embedding, dtype=np.float32))
            else:
                rejected.append(f"{pose.value}: {message}")

        if not embeddings:
            raise FaceServiceError(
                "Tidak ada pose yang valid. " + ("; ".join(rejected) if rejected else "")
            )
        if rejected:
            raise FaceServiceError("Sebagian pose belum sesuai: " + "; ".join(rejected))

        blob = self.pack_embeddings(embeddings)
        avg_quality = int(round(sum(qualities) / len(qualities))) if qualities else 0
        return blob, results, avg_quality, used_fallback

    # ------------------------------------------------------------------ #
    # Verification (match + liveness)
    # ------------------------------------------------------------------ #
    def verify_match(self, reference_blob: bytes, image_bytes: bytes) -> tuple[FaceFrameAnalysis, float]:
        analysis = self.analyze(image_bytes)
        if analysis.used_fallback:
            candidate = self._fallback_embedding(image_bytes)
            similarity = self.best_similarity(reference_blob, candidate)
        else:
            similarity = self.best_similarity(reference_blob, analysis.embedding)
        return analysis, similarity

    def evaluate_liveness(
        self, image_bytes: bytes, challenge: LivenessChallenge
    ) -> tuple[bool, FaceFrameAnalysis, str]:
        analysis = self.analyze(image_bytes)

        # Mode fallback / sinyal tidak tersedia: liveness disimulasikan dari kualitas frame.
        if analysis.used_fallback:
            passed = analysis.quality_score >= 60
            return passed, analysis, (
                "Liveness disimulasikan (mode tanpa model)."
                if passed
                else "Kualitas frame kurang, coba lagi dengan pencahayaan lebih baik."
            )

        if challenge == LivenessChallenge.SMILE:
            if analysis.smile_ratio is None:
                return analysis.quality_score >= 60, analysis, "Senyum tidak dapat diukur, memakai kualitas frame."
            passed = analysis.smile_ratio >= settings.liveness_smile_threshold
            return passed, analysis, ("Senyum terdeteksi." if passed else "Tersenyumlah lebih lebar.")

        if challenge == LivenessChallenge.BLINK:
            if analysis.ear is None:
                return analysis.quality_score >= 60, analysis, "Kedipan tidak dapat diukur, memakai kualitas frame."
            passed = analysis.ear <= settings.liveness_ear_threshold
            return passed, analysis, ("Kedipan terdeteksi." if passed else "Kedipkan mata Anda.")

        if challenge in (LivenessChallenge.TURN_LEFT, LivenessChallenge.TURN_RIGHT):
            if analysis.yaw is None:
                return analysis.quality_score >= 60, analysis, "Arah kepala tidak terukur, memakai kualitas frame."
            yaw_t = settings.liveness_yaw_threshold
            if challenge == LivenessChallenge.TURN_LEFT:
                passed = analysis.yaw >= yaw_t
                return passed, analysis, ("Menghadap kiri terdeteksi." if passed else "Hadapkan kepala ke kiri.")
            passed = analysis.yaw <= -yaw_t
            return passed, analysis, ("Menghadap kanan terdeteksi." if passed else "Hadapkan kepala ke kanan.")

        return False, analysis, "Challenge tidak dikenal."


face_service = FaceService()
