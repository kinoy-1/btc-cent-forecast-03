# btc-cent-forecast

Forecast the price of Bitcoin 240 minutes after each checkpoint, for the
[make.fun](https://make.fun) `btc-cent-forecast-01` bounty.

## Model

A shrinkage forecast toward the 6-hour simple moving average:

```
P        = last minute close (the checkpoint close)
SMA360   = mean of the last 360 minute closes (6 hours)
forecast = P + 0.10 * (SMA360 - P)
```

Over a 4-hour horizon the price behaves close to a random walk, so the
current price is the anchor. A small fixed 10% pull toward the 6-hour
average trims noise without chasing momentum.

## Run

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Reads every `<id>.in` case from the input directory and writes one
`<id>.out` file per case with `{"forecasts": [{"case": id, "price": x}]}`.
Python 3, standard library only, no network access.
