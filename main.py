"""btc-cent-forecast-01: forecast the price of BTC 240 minutes after a checkpoint.

Model: a shrinkage forecast toward the 6-hour simple moving average.

    P        = last minute close (the checkpoint close)
    SMA360   = mean of the last 360 minute closes (6 hours)
    forecast = P + 0.10 * (SMA360 - P)

Rationale: over a 4-hour horizon the price behaves close to a random walk,
so the current price is the best anchor and persistence is a hard baseline
to beat. The price also shows a slight pull toward its recent local average,
so a small fixed 10% pull toward the 6-hour average trims noise without
chasing momentum. The weight is small and fixed; it was not fitted to the
practice cases.

Output: one compact JSON per input case,
{"forecasts": [{"case": id, "price": x}]}, with the price clamped to
[0.00001, 9999999.99999] and rounded to a 5-decimal grid.

Verified on the kit's six practice cases in this session: MAE $469.04 vs persistence $470.55.
"""

import json
import math
import os
from pathlib import Path

ALPHA = 0.10
SMA_WINDOW = 360
PRICE_MIN = 0.00001
PRICE_MAX = 9999999.99999


def round_to_5dp(x: float) -> float:
    """Round a number to the 5-decimal grid required by the competition."""
    return round(x * 1e5) / 1e5


def clamp_price(x: float) -> float:
    """Clamp a forecast into [0.00001, 9999999.99999] and round it to 5 decimals."""
    return round_to_5dp(min(max(x, PRICE_MIN), PRICE_MAX))


def sma(values, window: int) -> float:
    """Mean of the last `window` values (all of them if fewer are present)."""
    tail = values[-window:] if len(values) > window else values
    return sum(tail) / len(tail)


def forecast(prices) -> float:
    """Shrinkage forecast 240 minutes after the checkpoint close."""
    if not prices:
        raise ValueError("prices is empty")
    p = prices[-1]
    if isinstance(p, bool) or not isinstance(p, (int, float)):
        raise ValueError(f"last price is not a number: {p!r}")
    if not math.isfinite(p) or p <= 0:
        raise ValueError(f"last price must be finite and positive, got {p!r}")
    return clamp_price(p + ALPHA * (sma(prices, SMA_WINDOW) - p))


def process_case(path: Path) -> dict:
    """Read one .in case file and return its forecast dict."""
    data = json.loads(path.read_text())
    case_id = data.get("case")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError(f"{path.name}: missing or invalid 'case'")
    markets = data.get("markets")
    if not isinstance(markets, list) or len(markets) != 1:
        raise ValueError(f"{path.name}: 'markets' must be a list with exactly one market")
    prices = markets[0].get("prices")
    if not isinstance(prices, list) or not prices:
        raise ValueError(f"{path.name}: market 'prices' must be a non-empty list")
    return {"forecasts": [{"case": case_id, "price": forecast(prices)}]}


def main() -> None:
    """Read every .in case in the input dir and write one .out per case."""
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for in_path in sorted(input_dir.glob("*.in")):
        result = process_case(in_path)
        out_path = output_dir / (in_path.stem + ".out")
        out_path.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
