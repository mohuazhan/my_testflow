# coding=utf-8

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import cmd, douyin, weibo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    cmd.router,
    prefix="/api/cmd"
)

app.include_router(
    douyin.router,
    prefix="/api/douyin"
)

app.include_router(
    weibo.router,
    prefix="/api/weibo"
)

if __name__ == '__main__':
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=8090)