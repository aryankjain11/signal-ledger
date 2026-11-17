"""Paper-trade persistence. SQLite by default; any SQLAlchemy URL (e.g. hosted Postgres) via DATABASE_URL.

Plan columns are written once (insert) and never updated. Only the evaluation columns and the
void flag change afterwards, so the recorded decision stays exactly as it was made.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import (Boolean, Column, Float, Integer, MetaData, String, Table, Text, UniqueConstraint, create_engine,
                        insert, select, update)
from sqlalchemy.exc import IntegrityError

from .paper import IST, PaperPlan

metadata = MetaData()
paper_trades = Table(
    "paper_trades", metadata,
    Column("id", String(24), primary_key=True),
    Column("ledger", String(60), nullable=False, index=True),
    Column("created_at", String(32), nullable=False),
    Column("symbol", String(40), nullable=False), Column("provider_symbol", String(40), nullable=False),
    Column("exchange", String(16)), Column("source", String(40)), Column("pattern", String(200)),
    Column("signal_date", String(10), nullable=False), Column("signal_close", Float, nullable=False),
    Column("atr", Float, nullable=False), Column("stop_atr", Float), Column("reward_risk", Float),
    Column("max_hold", Integer), Column("fee_bps", Float), Column("slippage_bps", Float),
    Column("note", Text), Column("snapshot", Text),
    # evaluation (refreshable)
    Column("status", String(32)), Column("entry_date", String(10)), Column("entry_price", Float),
    Column("stop", Float), Column("target", Float), Column("exit_date", String(10)), Column("exit_price", Float),
    Column("reason", String(60)), Column("r_multiple", Float), Column("unrealized_r", Float),
    Column("mfe_r", Float), Column("mae_r", Float), Column("sessions", Integer),
    Column("checked_through", String(10)), Column("evaluated_at", String(32)),
    Column("voided", Boolean, default=False), Column("void_reason", Text), Column("voided_at", String(32)),
    UniqueConstraint("ledger", "provider_symbol", "signal_date", "source", "pattern", name="one_plan_per_setup"),
)
PLAN_FIELDS = [f for f in PaperPlan.__dataclass_fields__]
EVAL_FIELDS = ["status", "entry_date", "entry_price", "stop", "target", "exit_date", "exit_price", "reason", "r_multiple",
               "unrealized_r", "mfe_r", "mae_r", "sessions", "checked_through"]


def database_url(root: Path) -> tuple[str, str]:
    """(url, human description). Streamlit secret or environment DATABASE_URL wins; else a local SQLite file."""
    url = os.environ.get("DATABASE_URL")
    try:
        import streamlit as st
        url = st.secrets.get("DATABASE_URL", url)
    except Exception:
        pass
    if url:
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        return url, "Hosted database (persists across restarts)"
    path = root / "data" / "paper_trades.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}", "Local file on this server (a hosted app loses it on restart)"


class PaperStore:
    def __init__(self, url: str):
        self.engine = create_engine(url, pool_pre_ping=True)
        metadata.create_all(self.engine)

    def add(self, plan: PaperPlan) -> bool:
        """Insert a new plan. Returns False if this exact setup is already recorded in the ledger."""
        row = plan.as_row()
        row["snapshot"] = json.dumps(row["snapshot"], default=str)
        try:
            with self.engine.begin() as conn:
                conn.execute(insert(paper_trades).values(**row, voided=False))
        except IntegrityError:
            return False
        return True

    def load(self, ledger: str) -> pd.DataFrame:
        with self.engine.connect() as conn:
            rows = conn.execute(select(paper_trades).where(paper_trades.c.ledger == ledger)
                                .order_by(paper_trades.c.created_at.desc())).mappings().all()
        frame = pd.DataFrame([dict(r) for r in rows], columns=[c.name for c in paper_trades.columns])
        if not frame.empty:
            frame["snapshot"] = frame.snapshot.map(lambda s: json.loads(s) if s else {})
        return frame

    def plan(self, row) -> PaperPlan:
        values = {k: row[k] for k in PLAN_FIELDS}
        values["snapshot"] = row["snapshot"] if isinstance(row["snapshot"], dict) else json.loads(row["snapshot"] or "{}")
        return PaperPlan(**values)

    def save_evaluation(self, trade_id: str, result: dict) -> None:
        values = {k: result.get(k) for k in EVAL_FIELDS}
        values["evaluated_at"] = datetime.now(IST).isoformat(timespec="seconds")
        with self.engine.begin() as conn:
            conn.execute(update(paper_trades).where(paper_trades.c.id == trade_id).values(**values))

    def void(self, trade_id: str, reason: str) -> None:
        if not reason.strip():
            raise ValueError("A reason is required to void a paper trade.")
        with self.engine.begin() as conn:
            conn.execute(update(paper_trades).where(paper_trades.c.id == trade_id)
                         .values(voided=True, void_reason=reason.strip(), voided_at=datetime.now(IST).isoformat(timespec="seconds")))
