from __future__ import annotations

import json
from typing import Any

from app.models import SimulatedTrade


def build_agent_summary(trades: list[SimulatedTrade]) -> dict[str, Any]:
    approved = [trade for trade in trades if trade.risk.approved]
    blocked = [trade for trade in trades if not trade.risk.approved]
    latest_capital = trades[-1].capital_after_usd if trades else 30.0
    blocked_reasons = blocked[0].risk.reasons if blocked else []
    risk_mode = "halt" if blocked_reasons else "normal"
    return {
        "risk_mode": risk_mode,
        "approved_count": len(approved),
        "blocked_count": len(blocked),
        "latest_capital_usd": latest_capital,
        "top_approved": [
            {
                "symbol": trade.opportunity.symbol,
                "net_edge_bps": trade.opportunity.net_edge_bps,
                "expected_pnl_usd": trade.opportunity.expected_pnl_usd,
                "rationale": trade.opportunity.rationale,
            }
            for trade in approved[:3]
        ],
        "blocked_reasons": blocked_reasons,
        "kill_switch_reason": blocked_reasons[0] if blocked_reasons else "",
        "human_review_note": "Widen or halt quotes when exchange/news risk rises." if blocked_reasons else "Maker-only quoting allowed under current regime.",
    }


def build_openclaw_message(summary: dict[str, Any]) -> str:
    return json.dumps(
        {
            "type": "arb_strategy_summary",
            "summary": summary,
            "instruction": "Use this as deterministic context only; do not generate live orders.",
        },
        ensure_ascii=False,
    )
