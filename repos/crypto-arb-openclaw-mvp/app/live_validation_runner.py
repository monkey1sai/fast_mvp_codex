from __future__ import annotations

from dataclasses import asdict
import time
from typing import Any

from app.live_guard import evaluate_live_order
from app.models import KillSwitchState, LiveTradingConfig, OrderBookTop, PositionState
from app.quote_engine import build_quote_intents


def _extract_order_payload(place_result: dict[str, Any]) -> dict[str, Any]:
    data = place_result.get("data", {})
    if isinstance(data, list):
        return data[0] if data else {}
    if isinstance(data, dict):
        return data
    return {}


def _is_open_status(status: str) -> bool:
    normalized = status.lower()
    return normalized in {"resting", "live", "partially_filled", "partially-filled"}


def _is_terminal_status(status: str) -> bool:
    normalized = status.lower()
    return normalized in {"filled", "canceled", "cancelled"}


def _trace(stage: str, **payload: Any) -> dict[str, Any]:
    return {"stage": stage, **payload}


def run_live_validation_cycle(
    book: OrderBookTop,
    kill_switch: KillSwitchState,
    execution: Any,
    live_config: LiveTradingConfig,
    explicit_confirmation: bool,
    daily_loss_usd: float,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    if kill_switch.triggered or kill_switch.mode == "halt":
        return {
            "mode": "halt",
            "placed_orders": 0,
            "cancelled_orders": 0,
            "cancel_after_ms": live_config.auto_cancel_after_ms,
            "reason": kill_switch.reason,
            "quotes": [],
            "events": [
                _trace(
                    "kill_switch_halt",
                    mode=kill_switch.mode,
                    reason=kill_switch.reason,
                )
            ],
        }

    position = execution.get_position(book.symbol)
    events.append(
        _trace(
            "position_snapshot",
            symbol=position.symbol,
            base_qty=position.base_qty,
            quote_value_usd=position.quote_value_usd,
            open_orders=position.open_orders,
        )
    )
    quotes = build_quote_intents(
        book=book,
        position=position,
        kill_switch=kill_switch,
        max_notional_usd=live_config.max_notional_per_order_usd,
        quote_refresh_ms=live_config.auto_cancel_after_ms,
    )
    events.append(
        _trace(
            "quote_candidates",
            count=len(quotes),
            quotes=[asdict(quote) for quote in quotes],
        )
    )

    approved_quote = None
    guard_decision = None
    min_notional_usd = 0.0
    if hasattr(execution, "get_symbol_constraints"):
        constraints = execution.get_symbol_constraints(book.symbol)
        min_notional_usd = float(constraints.get("minAmount", 0.0) or 0.0)
        events.append(
            _trace(
                "symbol_constraints",
                symbol=book.symbol,
                constraints=constraints,
            )
        )
    for quote in quotes:
        decision = evaluate_live_order(
            quote=quote,
            config=live_config,
            daily_loss_usd=daily_loss_usd,
            explicit_confirmation=explicit_confirmation,
            min_notional_usd=min_notional_usd,
            available_quote_usd=position.available_quote_usd,
            available_base_qty=position.base_qty,
        )
        events.append(
            _trace(
                "guard_decision",
                side=quote.side,
                price=quote.price,
                size_usd=quote.size_usd,
                approved=decision.approved,
                reasons=decision.reasons,
                capped_notional_usd=decision.capped_notional_usd,
            )
        )
        if decision.approved:
            approved_quote = quote
            guard_decision = decision
            break

    if approved_quote is None or guard_decision is None:
        return {
            "mode": kill_switch.mode,
            "placed_orders": 0,
            "cancelled_orders": 0,
            "cancel_after_ms": live_config.auto_cancel_after_ms,
            "reason": "no quote passed live guard",
            "min_notional_usd": min_notional_usd,
            "quotes": [asdict(quote) for quote in quotes],
            "events": events,
        }

    events.append(
        _trace(
            "place_order_request",
            side=approved_quote.side,
            price=approved_quote.price,
            size_usd=approved_quote.size_usd,
            ttl_ms=approved_quote.ttl_ms,
            rationale=approved_quote.rationale,
        )
    )
    place_result = execution.place_order(approved_quote, book)
    events.append(_trace("place_order_result", result=place_result))
    cancelled_orders = 0
    order_payload = _extract_order_payload(place_result)
    order_id = str(order_payload.get("orderId", order_payload.get("ordId", "")))
    status = str(
        place_result.get("status", order_payload.get("status", order_payload.get("state", "")))
    ).lower()
    if order_id and not _is_terminal_status(status):
        time.sleep(max(live_config.auto_cancel_after_ms, 0) / 1000)
        final_status = status
        if hasattr(execution, "get_order"):
            order_lookup = execution.get_order(book.symbol, order_id)
            events.append(_trace("get_order_result", order_id=order_id, result=order_lookup))
            final_payload = _extract_order_payload(order_lookup)
            final_status = str(
                order_lookup.get("status", final_payload.get("status", final_payload.get("state", final_status)))
            ).lower()
        if _is_open_status(final_status):
            cancel_result = execution.cancel_order(book.symbol, order_id)
            events.append(_trace("cancel_order_result", order_id=order_id, result=cancel_result))
            cancelled_orders = 1

    return {
        "mode": kill_switch.mode,
        "placed_orders": 1,
        "cancelled_orders": cancelled_orders,
        "cancel_after_ms": live_config.auto_cancel_after_ms,
        "quote": asdict(approved_quote),
        "guard": {
            "approved": guard_decision.approved,
            "capped_notional_usd": guard_decision.capped_notional_usd,
            "reasons": guard_decision.reasons,
        },
        "result": place_result,
        "events": events,
    }
