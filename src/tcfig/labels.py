"""Consistent scientific text labels."""

from __future__ import annotations


def quantity_label(
    quantity: str | None = None,
    symbol: str | None = None,
    unit: str | None = None,
) -> str:
    """Format an axis label as ``Quantity, symbol (unit)``.

    ``quantity`` or ``symbol`` is required. Dimensionless quantities should
    omit ``unit`` rather than use an artificial placeholder.
    """

    quantity_text = _clean_optional(quantity, "quantity")
    symbol_text = _clean_optional(symbol, "symbol")
    unit_text = _clean_optional(unit, "unit")
    if quantity_text is None and symbol_text is None:
        raise ValueError("quantity_label requires a quantity or symbol.")

    stem = ", ".join(value for value in (quantity_text, symbol_text) if value is not None)
    return f"{stem} ({unit_text})" if unit_text is not None else stem


def _clean_optional(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        raise ValueError(f"{name} must not be empty.")
    return cleaned
