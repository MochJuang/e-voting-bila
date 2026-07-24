from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, election, face, health, voters, voting

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(face.router, prefix="/face", tags=["face"])
api_router.include_router(voters.router, prefix="/voters", tags=["voters"])
api_router.include_router(voting.router, prefix="/votes", tags=["votes"])
api_router.include_router(election.router, prefix="/election", tags=["election"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

