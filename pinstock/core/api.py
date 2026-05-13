"""네이버 금융 API 호출."""

import requests
from datetime import datetime, timedelta

# ─── 공용 HTTP 세션 (TCP/TLS 연결 재사용으로 호출당 100~300ms 절감) ─────────
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
})


# ─── 네이버 금융 API ───────────────────────────────────────────────────────────
def fetch_stock(code: str) -> dict | None:
    """네이버 금융 모바일 API로 현재가 조회"""
    url = f"https://m.stock.naver.com/api/stock/{code}/basic"
    try:
        r = _SESSION.get(url, timeout=3)
        if r.status_code != 200:
            return None
        d = r.json()
        return {
            "name":         d.get("stockName", code),
            "price":        int(str(d.get("closePrice", "0")).replace(",", "")),
            "change_rate":  float(d.get("fluctuationsRatio", 0)),
            "change_price": int(str(d.get("compareToPreviousClosePrice", "0")).replace(",", "")),
        }
    except Exception as e:
        print(f"[fetch_stock] {code} 오류: {e}")
        return None


# ─── 네이버 금융 분봉 차트 API ───────────────────────────────────────────────
def fetch_minute_chart(code: str) -> dict | None:
    """네이버 금융 분봉 API로 당일 1분봉 시계열 조회.
    반환: {'prices': [float, ...], 'open': float} or None"""
    url = f"https://api.stock.naver.com/chart/domestic/item/{code}/minute"
    try:
        r = _SESSION.get(url, timeout=3)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        return {
            "prices": [float(d["currentPrice"]) for d in data],
            "open":   float(data[0]["openPrice"]),
        }
    except Exception as e:
        print(f"[fetch_minute_chart] {code} 오류: {e}")
        return None


# ─── 네이버 금융 일봉 차트 API (장 외 시간 폴백용) ──────────────────────────
def fetch_daily_chart(code: str, days: int = 45, max_candles: int = 30) -> dict | None:
    """최근 N 캘린더일 일봉 OHLC 시계열 조회.
    분봉이 비어있는 장 외 시간/주말/공휴일에 캔들 차트로 표시할 용도.
    반환: {'candles': [{'open','high','low','close'}, ...]} or None"""
    end = datetime.now()
    start = end - timedelta(days=days)
    url = (
        f"https://api.stock.naver.com/chart/domestic/item/{code}/day"
        f"?startDateTime={start.strftime('%Y%m%d')}"
        f"&endDateTime={end.strftime('%Y%m%d')}"
    )
    try:
        r = _SESSION.get(url, timeout=3)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        candles = [
            {
                "open":  float(d["openPrice"]),
                "high":  float(d["highPrice"]),
                "low":   float(d["lowPrice"]),
                "close": float(d["closePrice"]),
            }
            for d in data
        ]
        if max_candles > 0:
            candles = candles[-max_candles:]
        return {"candles": candles}
    except Exception as e:
        print(f"[fetch_daily_chart] {code} 오류: {e}")
        return None
