from enum import Enum

from sqlalchemy import Enum as SQLEnum


class AccessMode(str, Enum):
    MANDIRI = "mandiri"
    ADMIN_ASSISTED = "admin_assisted"


class SessionStatus(str, Enum):
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    VOTING_OPEN = "voting_open"
    CLOSED = "closed"


class VerificationResult(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    LOCKED = "locked"


class FacePose(str, Enum):
    """Pose wajah yang di-scan saat enrollment (registrasi)."""

    CENTER = "center"  # tengah
    UP = "up"  # atas
    RIGHT = "right"  # kanan
    DOWN = "down"  # bawah
    LEFT = "left"  # kiri


class LivenessChallenge(str, Enum):
    """Tantangan liveness acak saat verifikasi realtime."""

    TURN_LEFT = "turn_left"  # hadap kiri
    TURN_RIGHT = "turn_right"  # hadap kanan


class VerifyStage(str, Enum):
    """Tahap verifikasi realtime."""

    MATCH = "match"  # streaming pencocokan wajah
    LIVENESS = "liveness"  # cek liveness setelah wajah cocok


class AssistedSessionResult(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


def sqlalchemy_enum(enum_cls: type[Enum], *, name: str) -> SQLEnum:
    """
    Persist enum values instead of Python member names.

    This keeps database rows compatible with existing lowercase values like
    "mandiri" while still exposing rich Python Enum members in the ORM.
    """

    return SQLEnum(enum_cls, name=name, values_callable=lambda enum: [item.value for item in enum])
