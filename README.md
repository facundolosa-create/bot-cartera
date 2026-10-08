# Bot de Cartera — Etapa 1

Bot de Telegram que analiza las posiciones de tu cartera y devuelve:

- COMPRAR / COMPRAR-ACUMULAR / MANTENER / REDUCIR / VENDER
- Score 0–100
- Precio actual
- RSI(14)
- MA20 / MA50 / MA200
- MACD
- Momentum 20 días
- Stop técnico basado en ATR
- Objetivo técnico basado en ATR
- Factores que explican la señal

## Activos configurados

SPY, TQQQ, GOOGL, BTC, GLD, PEPE, USDx y NEXO.

Las cantidades iniciales fueron tomadas de la captura enviada. Se editan en `config.py`.

## 1. Crear el bot de Telegram

En Telegram abrí `@BotFather`, usá `/newbot` y seguí los pasos.
Telegram entrega un token que debe mantenerse secreto.

## 2. Instalar Python

Se recomienda Python 3.11 o superior.

## 3. Instalar dependencias

```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Luego:

```bash
pip install -r requirements.txt
```

## 4. Configurar el token

Copiá `.env.example` como `.env`:

```bash
cp .env.example .env
```

En Windows podés simplemente duplicar el archivo manualmente.

Pegá el token:

```text
TELEGRAM_BOT_TOKEN=123456:ABC...
```

También podés poner tu `ALLOWED_USER_ID`.

Para conocer tu ID, una opción sencilla es escribirle temporalmente al bot o usar un bot de consulta de ID. En una versión posterior podemos agregar un comando seguro para configurarlo.

## 5. Ejecutar

```bash
python bot.py
```

Después abrí tu bot en Telegram y escribí:

```text
/start
```

y luego:

```text
/analizar
```

También:

```text
/ticker BTC-USD
/ticker GOOGL
/posiciones
```

## Importante

Esta primera versión NO ejecuta compras ni ventas. Solo genera señales.

Los precios e históricos se obtienen mediante `yfinance`, que accede a datos públicos de Yahoo Finance. Es una solución práctica para un prototipo, pero no debe considerarse una fuente institucional de ejecución o cotización garantizada en tiempo real.

Antes de usar dinero real, conviene hacer backtesting y agregar controles de riesgo.
