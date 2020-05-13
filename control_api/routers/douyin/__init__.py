# coding=utf-8

from fastapi import APIRouter
from .tasks import router as tasks_router

router = APIRouter()

router.include_router(
    tasks_router,
    prefix='/tasks',
    tags=['douyin'],
)