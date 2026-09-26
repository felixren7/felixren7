#!/usr/bin/env python3
"""Create a dependency-free SVG card for a GitHub profile README."""

import argparse
import datetime as dt
import html
import json
import random
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parents[1] / "assets" / "daily-card.svg"
try:
    SINGAPORE = ZoneInfo("Asia/Singapore")
except KeyError:  # no system tzdata; Singapore has no DST, so a fixed offset is exact
    SINGAPORE = dt.timezone(dt.timedelta(hours=8), "SGT")

# WMO 4677 weather codes as returned by Open-Meteo.
WMO_LABELS = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Violent showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
}
THOUGHTS = (
    "Make it work, measure it, then make it better.",
    "A good interface makes the hard part easier to reason about.",
    "Reliable systems are built one failure mode at a time.",
    "The simplest useful test is the one you will actually run.",
    "Keep the feedback loop short and the assumptions visible.",
    "Performance begins with knowing where the time goes.",
    "Small, readable changes make debugging kinder.",
    "Trace the data before guessing at the bug.",
    "Design for recovery as carefully as for success.",
    "Build the smallest thing that answers the real question.",
)


def observed_at(raw):
    """Render Open-Meteo's ISO timestamp in the card's own format."""
    try:
        moment = dt.datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return str(raw)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=SINGAPORE)
    return moment.astimezone(SINGAPORE).strftime("%d %b %Y, %H:%M SGT")


def weather():
    params = urlencode({
        "latitude": 1.3521, "longitude": 103.8198,
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        "timezone": "Asia/Singapore",
    })
    with urlopen("https://api.open-meteo.com/v1/forecast?" + params, timeout=15) as response:
        current = json.load(response)["current"]
    code = int(current["weather_code"])
    label = WMO_LABELS.get(code, "Unclassified conditions")
    temp = float(current["temperature_2m"])
    humidity = int(current["relative_humidity_2m"])
    return f"{temp:.1f}°C · {label} · Humidity {humidity}%", observed_at(current["time"])


def render(condition, observed, now):
    thought = random.choice(THOUGHTS)
    updated = now.strftime("%d %b %Y, %H:%M SGT")
    def esc(value):
        return html.escape(value, quote=True)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" viewBox="0 0 900 180" role="img" aria-label="Singapore weather and daily thought">
  <defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0f172a"/><stop offset="1" stop-color="#312e81"/></linearGradient></defs>
  <rect width="900" height="180" rx="20" fill="url(#bg)"/>
  <text x="32" y="36" fill="#a5b4fc" font-family="Arial, sans-serif" font-size="16" font-weight="bold">SINGAPORE WEATHER</text>
  <text x="32" y="76" fill="#ffffff" font-family="Arial, sans-serif" font-size="25">{esc(condition)}</text>
  <text x="32" y="111" fill="#a5b4fc" font-family="Arial, sans-serif" font-size="16" font-weight="bold">TODAY'S THOUGHT</text>
  <text x="32" y="142" fill="#f8fafc" font-family="Arial, sans-serif" font-size="19">{esc(thought)}</text>
  <text x="32" y="165" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="12">Updated {esc(updated)} · Weather observation {esc(observed)} · Open-Meteo</text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Generate a preview without an API call")
    args = parser.parse_args()
    now = dt.datetime.now(SINGAPORE)
    if args.offline:
        condition, observed = "Weather updates after the first workflow run", "pending"
    else:
        try:
            condition, observed = weather()
        except (OSError, ValueError, KeyError, TypeError, TimeoutError) as exc:
            if OUT.exists():
                print(f"Weather unavailable ({exc}); keeping the last generated card")
                return
            condition, observed = "Weather temporarily unavailable", "unavailable"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(condition, observed, now), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
