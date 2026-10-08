import math
import numpy as np
import pandas as pd
import yfinance as yf

BUY = "🟢 COMPRAR"
HOLD = "🟡 MANTENER"
REDUCE = "🟠 REDUCIR"
SELL = "🔴 VENDER"

def ema(s, span):
    return s.ewm(span=span, adjust=False).mean()

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50)

def atr(df, period=14):
    prev_close = df["Close"].shift(1)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - prev_close).abs(),
        (df["Low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

def macd(close):
    fast = ema(close, 12)
    slow = ema(close, 26)
    line = fast - slow
    signal = ema(line, 9)
    hist = line - signal
    return line, signal, hist

def safe_float(x, default=float("nan")):
    try:
        return float(x)
    except Exception:
        return default

def download_data(ticker):
    df = yf.download(
        ticker,
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if df is None or df.empty:
        raise ValueError(f"No hay datos disponibles para {ticker}")

    # yfinance puede devolver MultiIndex incluso para un ticker.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    needed = ["Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in needed if c in df.columns]].dropna(subset=["Close"])
    if len(df) < 220:
        raise ValueError(f"Histórico insuficiente para {ticker}: {len(df)} ruedas/días")
    return df

def score_signal(df, asset_type):
    close = df["Close"]
    volume = df["Volume"] if "Volume" in df else pd.Series(index=df.index, dtype=float)

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    r = rsi(close)
    macd_line, macd_signal, macd_hist = macd(close)
    a = atr(df)

    p = safe_float(close.iloc[-1])
    m20 = safe_float(ma20.iloc[-1])
    m50 = safe_float(ma50.iloc[-1])
    m200 = safe_float(ma200.iloc[-1])
    rv = safe_float(r.iloc[-1])
    mh = safe_float(macd_hist.iloc[-1])
    mh_prev = safe_float(macd_hist.iloc[-2])
    av = safe_float(a.iloc[-1])

    score = 50.0
    reasons = []

    # Tendencia larga: 0-20
    if p > m200:
        score += 10
        reasons.append("precio > MA200")
    else:
        score -= 10
        reasons.append("precio < MA200")

    if m50 > m200:
        score += 5
        reasons.append("MA50 > MA200")
    else:
        score -= 5
        reasons.append("MA50 < MA200")

    if m20 > m50:
        score += 5
        reasons.append("MA20 > MA50")
    else:
        score -= 5
        reasons.append("MA20 < MA50")

    # RSI
    if 50 <= rv <= 68:
        score += 8
        reasons.append("RSI favorable")
    elif rv > 75:
        score -= 7
        reasons.append("RSI sobrecomprado")
    elif rv < 30:
        score += 2
        reasons.append("RSI muy bajo: posible rebote")
    elif rv < 45:
        score -= 5
        reasons.append("RSI débil")
    else:
        score += 2

    # MACD
    if mh > 0:
        score += 8
        reasons.append("MACD positivo")
    else:
        score -= 8
        reasons.append("MACD negativo")

    if mh > mh_prev:
        score += 4
        reasons.append("momentum MACD mejorando")
    else:
        score -= 4
        reasons.append("momentum MACD deteriorando")

    # Momentum 20 días
    mom20 = safe_float(close.iloc[-1] / close.iloc[-21] - 1)
    if mom20 > 0.05:
        score += 5
    elif mom20 < -0.05:
        score -= 5

    # Volumen relativo, si existe
    try:
        vr = safe_float(volume.iloc[-1] / volume.rolling(20).mean().iloc[-1])
        if vr > 1.2 and mom20 > 0:
            score += 3
            reasons.append("volumen acompaña")
        elif vr > 1.5 and mom20 < 0:
            score -= 3
            reasons.append("volumen acompaña caída")
    except Exception:
        vr = float("nan")

    # TQQQ: penalización de riesgo por apalancamiento
    if asset_type == "leveraged_etf":
        score -= 4
        reasons.append("penalización por apalancamiento")

    score = max(0, min(100, round(score)))

    if score >= 80:
        signal = BUY
    elif score >= 65:
        signal = "🟢 COMPRAR / ACUMULAR"
    elif score >= 45:
        signal = HOLD
    elif score >= 30:
        signal = REDUCE
    else:
        signal = SELL

    stop = p - 2.0 * av if math.isfinite(av) else float("nan")
    target = p + 3.0 * av if math.isfinite(av) else float("nan")

    return {
        "price": p,
        "score": score,
        "signal": signal,
        "ma20": m20,
        "ma50": m50,
        "ma200": m200,
        "rsi": rv,
        "macd_hist": mh,
        "momentum20": mom20,
        "volume_ratio": vr,
        "atr": av,
        "stop": stop,
        "target": target,
        "reasons": reasons,
    }

def analyze_one(position):
    if position["type"] == "cash":
        return {
            **position,
            "price": 1.0,
            "value": position["quantity"],
            "score": None,
            "signal": HOLD,
            "note": "Efectivo/stablecoin: no se aplica análisis técnico.",
        }

    df = download_data(position["ticker"])
    metrics = score_signal(df, position["type"])
    return {
        **position,
        **metrics,
        "value": metrics["price"] * position["quantity"],
    }

def analyze_portfolio(portfolio):
    results = []
    for p in portfolio:
        try:
            results.append(analyze_one(p))
        except Exception as e:
            results.append({
                **p,
                "price": float("nan"),
                "value": float("nan"),
                "score": None,
                "signal": "⚪ SIN DATOS",
                "note": str(e),
            })
    return results

def money(x):
    if x is None or not math.isfinite(safe_float(x)):
        return "N/D"
    return f"US${x:,.2f}"

def pct(x):
    if x is None or not math.isfinite(safe_float(x)):
        return "N/D"
    return f"{x*100:+.1f}%"

def format_single_report(r):
    lines = [
        f"📊 {r['name']} ({r['ticker'] or 'cash'})",
        f"Señal: {r['signal']}",
        f"Score: {r.get('score', 'N/D')}/100",
        f"Precio: {money(r.get('price'))}",
        f"Valor posición: {money(r.get('value'))}",
    ]
    if r.get("score") is None:
        lines.append(r.get("note", "Sin análisis técnico."))
        return "\n".join(lines)

    lines += [
        "",
        f"RSI(14): {r['rsi']:.1f}",
        f"MA20: {money(r['ma20'])}",
        f"MA50: {money(r['ma50'])}",
        f"MA200: {money(r['ma200'])}",
        f"Momentum 20d: {pct(r['momentum20'])}",
        f"Stop técnico: {money(r['stop'])}",
        f"Objetivo técnico: {money(r['target'])}",
        "",
        "Factores: " + ", ".join(r["reasons"][:7]),
    ]
    return "\n".join(lines)

def format_portfolio_report(results):
    valid_values = [r["value"] for r in results if math.isfinite(safe_float(r.get("value")))]
    total = sum(valid_values)

    lines = [
        "🤖 ANÁLISIS DE CARTERA — ETAPA 1",
        "━━━━━━━━━━━━━━━━━━━━",
        f"Valor analizado: {money(total)}",
        "",
    ]

    for r in results:
        value = money(r.get("value"))
        score = r.get("score")
        score_text = f"{score}/100" if score is not None else "N/D"
        lines.append(
            f"{r['signal']}  {r['name']}  | Score {score_text} | {value}"
        )

    lines += ["", "📌 DETALLE", "━━━━━━━━━━━━━━━━━━━━"]

    for r in results:
        lines.append("")
        lines.append(format_single_report(r))

    lines += [
        "",
        "⚠️ Nota: son señales cuantitativas/educativas, no una recomendación "
        "personalizada ni una garantía de rendimiento. No ejecuta operaciones."
    ]
    return "\n".join(lines)
