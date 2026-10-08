# Cartera inicial tomada de la captura enviada.
# Modificá quantity cuando cambien tus tenencias.
#
# Tickers de Yahoo Finance:
# SPY, TQQQ, GOOGL, GLD
# BTC-USD, PEPE-USD, NEXO-USD
#
# USDx se trata como efectivo/stablecoin sin señal técnica.

PORTFOLIO = [
    {
        "name": "SPY",
        "ticker": "SPY",
        "quantity": 2.26802032,
        "type": "etf",
    },
    {
        "name": "TQQQ",
        "ticker": "TQQQ",
        "quantity": 13.65247994,
        "type": "leveraged_etf",
    },
    {
        "name": "GOOGL",
        "ticker": "GOOGL",
        "quantity": 2.94489036,
        "type": "stock",
    },
    {
        "name": "BTC",
        "ticker": "BTC-USD",
        "quantity": 0.00452228,
        "type": "crypto",
    },
    {
        "name": "GLD",
        "ticker": "GLD",
        "quantity": 0.1322397,
        "type": "etf",
    },
    {
        "name": "PEPE",
        "ticker": "PEPE-USD",
        "quantity": 3422529.57,
        "type": "crypto",
    },
    {
        "name": "USDx",
        "ticker": None,
        "quantity": 9.81,
        "type": "cash",
    },
    {
        "name": "NEXO",
        "ticker": "NEXO-USD",
        "quantity": 0.02353066,
        "type": "crypto",
    },
]
