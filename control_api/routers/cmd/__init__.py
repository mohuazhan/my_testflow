# coding=utf-8

from fastapi import APIRouter
from .adb import router as adb_router

router = APIRouter()

router.include_router(
    adb_router,
    prefix='/adb',
    tags=['adb'],
)