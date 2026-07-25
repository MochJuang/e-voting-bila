from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "E-Voting Backend"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "e_voting"
    mysql_user: str = "root"
    mysql_password: str = ""

    database_url: str = "mysql+pymysql://root:@127.0.0.1:3306/e_voting"

    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 60

    face_match_threshold: float = 0.35
    face_max_retries: int = 3
    face_model_name: str = "buffalo_l"

    # Enrollment multi-pose: pose yang wajib di-scan (tengah, atas, kanan, bawah, kiri)
    enroll_required_poses: list[str] = ["center", "up", "right", "down", "left"]
    # Toleransi pose (derajat) — seberapa jauh kepala harus menoleh/menunduk agar pose dianggap benar
    enroll_pose_yaw_threshold: float = 15.0
    enroll_pose_pitch_threshold: float = 12.0
    # Jika True, pose dengan arah kepala yang salah ditolak. Default False (advisory) agar
    # enrollment tetap berhasil tanpa perlu kalibrasi tanda sudut model terlebih dahulu.
    enroll_enforce_pose_direction: bool = False

    # Liveness challenge thresholds
    liveness_yaw_threshold: float = 18.0  # derajat menoleh untuk turn_left/turn_right
    liveness_ear_threshold: float = 0.21  # eye openness ratio; di bawah ini = mata terpejam (kedip)
    # rasio lebar mulut / jarak antar-mata; di atas ini = tersenyum.
    # Wajah netral terukur ~1.0; senyum melebarkan mulut. Kalibrasi per-kamera bila perlu.
    liveness_smile_threshold: float = 1.15
    liveness_min_score: float = 0.5

    upload_dir: str = "storage"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

