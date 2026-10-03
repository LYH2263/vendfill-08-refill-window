import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Lane, Location, RefillOrder
from app.services.fill_engine import build_fill_lines, summarize
from app.services.window import REASON_OUTSIDE_WINDOW, is_window_open

router = APIRouter(prefix="/refills", tags=["refills"])


def _get_location(db: Session, location_id: int) -> Location:
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(404, "点位不存在")
    return loc


def _generate(db: Session, location_id: int) -> dict:
    """生成补货单的唯一入口：先按点位时段窗放行，再按现网规则（缺口）算量。"""
    loc = _get_location(db, location_id)
    if not is_window_open(loc.window_start_min, loc.window_end_min):
        # 窗外：失败原因只写“不在补货时段”，不落任何补货单
        raise HTTPException(400, REASON_OUTSIDE_WINDOW)
    lanes = db.scalars(select(Lane).where(Lane.location_id == location_id).order_by(Lane.slot_no)).all()
    payload = [{"id": l.id, "slot_no": l.slot_no, "sku_name": l.sku_name,
                "capacity": l.capacity, "stock": l.stock, "in_transit": l.in_transit} for l in lanes]
    summary = summarize(build_fill_lines(payload))
    order = RefillOrder(location_id=location_id, created_at=datetime.utcnow(),
                        lines_json=json.dumps(summary, ensure_ascii=False))
    db.add(order); db.commit(); db.refresh(order)
    return {"id": order.id, "location_id": location_id, **summary}


def _empty_payload(location_id: int, reason: str | None) -> dict:
    return {"id": None, "location_id": location_id, "total_fill": 0,
            "need_fill_count": 0, "full_count": 0, "overbooked_count": 0,
            "lines": [], "reason": reason}


@router.post("/run")
def run_refill(location_id: int = 1, db: Session = Depends(get_db)):
    return _generate(db, location_id)


@router.get("/latest")
def latest(location_id: int = 1, db: Session = Depends(get_db)):
    """最近一次成功单；纯读不生成。无单时返回空壳（窗外带原因），条数不受影响。"""
    loc = _get_location(db, location_id)
    order = db.scalars(select(RefillOrder).where(RefillOrder.location_id == location_id)
                       .order_by(RefillOrder.id.desc())).first()
    if not order:
        reason = None if is_window_open(loc.window_start_min, loc.window_end_min) else REASON_OUTSIDE_WINDOW
        return _empty_payload(location_id, reason)
    data = json.loads(order.lines_json)
    return {"id": order.id, "location_id": location_id, **data}


@router.get("/full")
def full_lanes(location_id: int = 1, db: Session = Depends(get_db)):
    data = latest(location_id=location_id, db=db)
    return {"location_id": location_id, "lanes": [l for l in data["lines"] if l["status"] == "full"]}


@router.get("/summary")
def refill_summary(location_id: int = 1, db: Session = Depends(get_db)):
    data = latest(location_id=location_id, db=db)
    return {
        "location_id": location_id,
        "total_fill": data["total_fill"],
        "need_fill_count": data["need_fill_count"],
        "full_count": data["full_count"],
        "overbooked_count": data["overbooked_count"],
    }
