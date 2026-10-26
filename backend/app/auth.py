"""管理员登录与令牌校验。默认账号可由环境变量覆盖。"""

from __future__ import annotations

import hashlib
import hmac
import os
import time

from fastapi import Header, HTTPException

ADMIN_USER = os.getenv("ADMIN_USER", "changxy")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changxy")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "night-passage-admin-secret")
TOKEN_TTL_SECONDS = int(os.getenv("ADMIN_TOKEN_TTL", str(60 * 60 * 24 * 7)))


def issue_token(username: str) -> str:
    exp = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f"{username}:{exp}"
    sig = hmac.new(ADMIN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_token(token: str) -> str:
    try:
        username, exp_raw, sig = token.rsplit(":", 2)
        exp = int(exp_raw)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="登录已失效") from exc
    payload = f"{username}:{exp}"
    expected = hmac.new(ADMIN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=401, detail="登录已失效")
    if exp < int(time.time()):
        raise HTTPException(status_code=401, detail="登录已过期")
    if username != ADMIN_USER:
        raise HTTPException(status_code=401, detail="登录已失效")
    return username


def authenticate(username: str, password: str) -> str:
    user_ok = hmac.compare_digest(username, ADMIN_USER)
    pass_ok = hmac.compare_digest(password, ADMIN_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="账号或密码不对")
    return issue_token(username)


def require_admin(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="需要先登录管理员")
    return verify_token(authorization.split(" ", 1)[1].strip())
