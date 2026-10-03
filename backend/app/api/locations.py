from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Location
from app.services.window import is_window_open, validate_window

router = APIRouter(prefix="/locations", tags=["locations"])


class WindowUpdate(BaseModel):
    # 两个键都必须传；值可为 null（皆空 = 不限时段）
    window_start_min: int | None
    window_end_min: int | None


def serialize_location(loc: Location) -> dict:
    return {
        "id": loc.id,
        "code": loc.code,
        "name": loc.name,
        "address": loc.address,
        "window_start_min": loc.window_start_min,
        "window_end_min": loc.window_end_min,
        # 与生成接口同一套放行口径：按当前时刻当场判定
        "window_open": is_window_open(loc.window_start_min, loc.window_end_min),
    }


@router.get("")
def list_locations(db: Session = Depends(get_db)):
    return [serialize_location(r) for r in db.scalars(select(Location).order_by(Location.id)).all()]


@router.put("/{location_id}")
def update_location_window(location_id: int, body: WindowUpdate, db: Session = Depends(get_db)):
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(404, "点位不存在")
    err = validate_window(body.window_start_min, body.window_end_min)
    if err:
        # 非法窗拒绝保存，点位与单据保持改前
        raise HTTPException(400, err)
    loc.window_start_min = body.window_start_min
    loc.window_end_min = body.window_end_min
    db.commit()
    db.refresh(loc)
    return serialize_location(loc)
