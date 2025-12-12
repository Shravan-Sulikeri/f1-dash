"""
OpenF1 Streamlit Dashboard (Broadcast-Style)

This is a self-contained Streamlit app that mirrors the "OpenF1 Platform"
experience with mock data. Run with:
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# ----------------------------
# Mock Data
# ----------------------------

@dataclass
class Driver:
    id: str
    name: str
    team: str
    number: int
    color: str
    points: int
    country: str
    image: str
    career_wins: int
    titles: int
    poles: int
    podiums: int
    fastest_laps: int
    grand_prix: int


@dataclass
class Team:
    id: str
    name: str
    full_name: str
    points: int
    color: str
    base: str
    chief: str
    power: str
    titles: int
    drivers: List[str]
    future: bool = False


@dataclass
class Race:
    season: int
    round: int
    name: str
    circuit: str
    date: str
    laps: int
    length: str
    rain: int
    track_id: str
    image: str


# Drivers (subset for brevity, but styled)
DRIVERS: Dict[str, Driver] = {
    "verstappen": Driver(
        "verstappen",
        "Max Verstappen",
        "Red Bull Racing",
        1,
        "#3671C6",
        305,
        "NED",
        "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/2col/image.png",
        61,
        3,
        40,
        107,
        32,
        197,
    ),
    "norris": Driver(
        "norris",
        "Lando Norris",
        "McLaren",
        4,
        "#FF8000",
        268,
        "GBR",
        "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/2col/image.png",
        2,
        0,
        5,
        21,
        8,
        118,
    ),
    "leclerc": Driver(
        "leclerc",
        "Charles Leclerc",
        "Ferrari",
        16,
        "#E8002D",
        245,
        "MON",
        "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/2col/image.png",
        7,
        0,
        26,
        36,
        9,
        137,
    ),
    "hamilton": Driver(
        "hamilton",
        "Lewis Hamilton",
        "Ferrari",
        44,
        "#E8002D",
        190,
        "GBR",
        "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/2col/image.png",
        105,
        7,
        104,
        200,
        67,
        346,
    ),
}

TEAMS: List[Team] = [
    Team("redbull", "Red Bull", "Oracle Red Bull Racing", 480, "#3671C6", "Milton Keynes, UK", "Christian Horner", "Honda RBPT", 6, ["verstappen", "perez"]),
    Team("mclaren", "McLaren", "McLaren Formula 1 Team", 453, "#FF8000", "Woking, UK", "Andrea Stella", "Mercedes", 8, ["norris", "piastri"]),
    Team("ferrari", "Ferrari", "Scuderia Ferrari HP", 420, "#E8002D", "Maranello, Italy", "Fred Vasseur", "Ferrari", 16, ["leclerc", "hamilton"]),
    Team("mercedes", "Mercedes", "Mercedes-AMG PETRONAS F1 Team", 340, "#00D2BE", "Brackley, UK", "Toto Wolff", "Mercedes", 8, ["russell", "antonelli"]),
]

RACES: List[Race] = [
    Race(2025, 16, "Italian Grand Prix", "Monza", "Sep 5-7", 53, "5.793 km", 15, "monza", "https://images.unsplash.com/photo-1516216628259-222f7f4758f0?q=80&w=2070&auto=format&fit=crop"),
    Race(2025, 15, "Dutch Grand Prix", "Zandvoort", "Aug 29-31", 72, "4.259 km", 40, "monza", "https://images.unsplash.com/photo-1597587886659-cbce1d670c26?q=80&w=2070&auto=format&fit=crop"),
    Race(2025, 14, "Hungarian Grand Prix", "Hungaroring", "Aug 1-3", 70, "4.381 km", 20, "monza", "https://images.unsplash.com/photo-1622329707954-47408890000d?q=80&w=2070&auto=format&fit=crop"),
]

# Simple track map library (Monza default)
TRACK_LAYOUTS: Dict[str, Dict[str, object]] = {
    "monza": {
        "path": "M 40 120 L 140 120 Q 180 120 180 90 L 175 60 L 165 55 L 175 50 L 165 45 L 150 40 Q 130 20 100 30 L 60 40 Q 20 50 20 90 L 20 100 L 25 105 L 20 110 Q 20 120 40 120 Z",
        "viewBox": "0 0 200 150",
        "sectors": [
            {"id": "S1", "x": 40, "y": 100},
            {"id": "S2", "x": 160, "y": 30},
            {"id": "S3", "x": 100, "y": 130},
        ],
    }
}

# Predictions mock (per race)
def mock_predictions(race: Race) -> pd.DataFrame:
    base = [
        ("VER", "Max Verstappen", "Red Bull", 1, 0.58),
        ("NOR", "Lando Norris", "McLaren", 4, 0.22),
        ("LEC", "Charles Leclerc", "Ferrari", 16, 0.12),
        ("HAM", "Lewis Hamilton", "Ferrari", 44, 0.08),
    ]
    data = []
    for code, name, team, num, p in base:
        data.append(
            {
                "season": race.season,
                "round": race.round,
                "grand_prix": race.name,
                "driver_code": code,
                "driver_name": name,
                "team_name": team,
                "driver_number": num,
                "grid_position": max(1, math.ceil((1 - p) * 8)),
                "pred_win_proba": p,
                "pred_win_proba_softmax": p / sum(x[4] for x in base),
            }
        )
    return pd.DataFrame(data)


# ----------------------------
# Helpers
# ----------------------------

def set_page() -> None:
    st.set_page_config(
        page_title="OpenF1 Platform",
        page_icon="🏎️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        body { background: #020617 !important; }
        .main { background: radial-gradient(circle at 20% 20%, rgba(255,255,255,0.02), transparent 25%), #020617; }
        .card {
            background: rgba(10,12,26,0.8);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
            padding: 18px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(20px);
        }
        .card::before {
            content: '';
            position: absolute;
            top: -40px; right: -40px;
            width: 160px; height: 160px;
            background: radial-gradient(circle, rgba(59,130,246,0.12), transparent 60%);
            transform: rotate(20deg);
        }
        .card .accent-tl {
            position: absolute;
            top: 10px; right: 10px;
            width: 10px; height: 10px;
            border-top: 2px solid rgba(255,255,255,0.5);
            border-right: 2px solid rgba(255,255,255,0.5);
        }
        .card .accent-bl {
            position: absolute;
            bottom: 10px; left: 10px;
            width: 10px; height: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.5);
            border-left: 2px solid rgba(255,255,255,0.5);
        }
        .title { font-weight: 900; letter-spacing: 0.18em; text-transform: uppercase; color: #94a3b8; font-size: 11px; }
        .heading { font-weight: 900; letter-spacing: -0.04em; text-transform: uppercase; font-style: italic; }
        .pill { padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08); background: rgba(148,163,184,0.08); font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
        .skew { transform: skewX(-10deg); }
        .btn { padding: 10px 16px; border-radius: 6px; font-weight: 900; letter-spacing: 0.14em; text-transform: uppercase; border: 1px solid transparent; }
        .btn-primary { background: white; color: black; }
        .btn-primary:hover { background: #ef4444; color: white; border-color: rgba(255,255,255,0.2); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, badge: str = "") -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"<div class='heading' style='font-size:48px; color:white;'>{title}</div>"
            "<div style='color:#94a3b8; font-size:12px; letter-spacing:0.2em;'>Live Telemetry Feed // Lakehouse Connection Active</div>",
            unsafe_allow_html=True,
        )
    with col2:
        if badge:
            st.markdown(f"<div class='pill' style='text-align:right; float:right; background: rgba(239,68,68,0.15); color:#fca5a5;'>{badge}</div>", unsafe_allow_html=True)


def card(title: str, body: str, glow: str = "red") -> None:
    st.markdown(
        f"""
        <div class="card" style="box-shadow: 0 0 24px rgba(239,68,68,0.12);" >
          <div class="accent-tl"></div><div class="accent-bl"></div>
          <div class="title">{title}</div>
          <div style="color:white; font-size:28px; font-weight:900; font-style:italic; margin-top:8px;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(race: Race) -> None:
    track = TRACK_LAYOUTS.get(race.track_id) or TRACK_LAYOUTS["monza"]
    st.markdown(
        f"""
        <div class="card" style="height:100%; padding:24px; border-color: rgba(239,68,68,0.25);">
          <div class="accent-tl"></div><div class="accent-bl"></div>
          <div style="position:relative; z-index:2;">
            <div class="title" style="color:#f87171;">Next Grand Prix</div>
            <div style="display:flex; justify-content:space-between; gap:16px; align-items:flex-end; flex-wrap:wrap;">
              <div>
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px; color:#ef4444; font-weight:800; letter-spacing:0.16em; text-transform:uppercase; font-size:12px;">
                  <span class="heading" style="color:white; font-size:22px;">{race.name}</span>
                </div>
                <div class="heading" style="color:white; font-size:62px; line-height:1; margin-bottom:6px;">{race.circuit.upper()}</div>
                <div style="color:#cbd5e1; font-size:12px; letter-spacing:0.14em; font-weight:800; text-transform:uppercase; display:flex; gap:14px; flex-wrap:wrap;">
                  <span style="display:flex; align-items:center; gap:6px;"><span style="color:#ef4444;">●</span> {race.date}</span>
                  <span style="display:flex; align-items:center; gap:6px;"><span style="color:#ef4444;">↺</span> {race.length}</span>
                  <span style="display:flex; align-items:center; gap:6px;"><span style="color:#22d3ee;">☔</span> {race.rain}% rain</span>
                </div>
              </div>
              <div style="display:flex; gap:12px;">
                <div style="background:rgba(0,0,0,0.5); border-left:2px solid #ef4444; padding:14px 18px; min-width:110px; text-align:center;">
                  <div class="heading" style="color:white; font-size:28px;">{race.laps}</div>
                  <div class="title" style="color:#94a3b8;">Laps</div>
                </div>
                <div style="background:rgba(0,0,0,0.5); border-left:2px solid #22d3ee; padding:14px 18px; min-width:110px; text-align:center;">
                  <div class="heading" style="color:white; font-size:28px;">{race.rain}%</div>
                  <div class="title" style="color:#94a3b8;">Rain</div>
                </div>
              </div>
            </div>
          </div>
          <div style="position:absolute; inset:0; opacity:0.45; background-image:url('{race.image}'); background-size:cover; background-position:center; filter:saturate(0.9);"></div>
          <svg style="position:absolute; right:8%; top:10%; height:220px; width:320px; opacity:0.18;" viewBox="{track['viewBox']}" fill="none" stroke="currentColor">
            <path d="{track['path']}" stroke-width="4" class="text-white"></path>
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def predictions_panel(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="card" style="height:100%; border-color: rgba(59,130,246,0.25);">
          <div class="accent-tl"></div><div class="accent-bl"></div>
          <div class="title">Predictive AI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if df.empty:
        st.info("No prediction data.")
        return
    df = df.sort_values("pred_win_proba_softmax", ascending=False)
    for _, row in df.iterrows():
        prob = row.pred_win_proba_softmax * 100
        color = "#22d3ee" if prob > 50 else "#f97316" if prob > 20 else "#ef4444"
        st.markdown(
            f"""
            <div style="margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center; font-weight:900; color:white; font-style:italic; letter-spacing:-0.03em;">
                <span style="display:flex; gap:10px; align-items:center;">
                  <span style="width:6px; height:18px; background:{color}; display:inline-block; transform:skewX(-10deg);"></span>
                  {row.driver_name} ({row.driver_code})
                </span>
                <span style="font-family:monospace; color:{color};">{prob:.1f}%</span>
              </div>
              <div style="position:relative; height:8px; background:#0f172a; border-radius:3px; overflow:hidden; transform:skewX(-10deg);">
                <div style="position:absolute; inset:0; width:{prob}%; background:linear-gradient(90deg, rgba(34,211,238,0.9), rgba(59,130,246,0.7)); box-shadow:0 0 12px rgba(34,211,238,0.6);"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def standings_section(drivers: Dict[str, Driver]) -> None:
    cards = []
    for drv in sorted(drivers.values(), key=lambda d: d.points, reverse=True):
        cards.append(
            f"""
            <div class="card" style="padding:16px; border-color: rgba(34,197,94,0.2);">
              <div class="accent-tl"></div><div class="accent-bl"></div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div class="heading" style="color:white; font-size:20px;">{drv.name}</div>
                  <div class="title" style="color:#94a3b8;">{drv.team}</div>
                </div>
                <div class="heading" style="color:{drv.color}; font-size:26px;">{drv.points} pts</div>
              </div>
              <div style="margin-top:10px; color:#cbd5e1; font-size:12px;">Wins: {drv.career_wins} · Poles: {drv.poles} · Podiums: {drv.podiums}</div>
            </div>
            """
        )
    st.markdown("<div style='display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px;'>", unsafe_allow_html=True)
    for c in cards:
        st.markdown(c, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# App
# ----------------------------

def main() -> None:
    set_page()

    # UI State
    seasons = sorted({r.season for r in RACES})
    round_map = {r.round: r for r in RACES}

    col_top = st.columns([1, 1, 1])
    with col_top[0]:
        st.markdown("<div class='heading' style='font-size:34px; color:white;'>OpenF1 Platform</div>", unsafe_allow_html=True)
        st.markdown("<div class='title'>Futuristic F1 Telemetry & Analytics</div>", unsafe_allow_html=True)
    with col_top[2]:
        st.markdown(
            "<div style='text-align:right;'><span class='pill' style='background:rgba(14,165,233,0.18); color:#7dd3fc;'>DATA STREAMING</span></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        season = st.selectbox("Season", seasons, index=len(seasons) - 1, format_func=lambda x: f"Season {x}")
    with c2:
        valid_rounds = [r.round for r in RACES if r.season == season]
        round_choice = st.selectbox("Round", valid_rounds, index=len(valid_rounds) - 1, format_func=lambda x: f"Round {x}")
    with c3:
        st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
        st.button("Refresh", use_container_width=True)

    race = round_map.get(round_choice, RACES[0])
    preds = mock_predictions(race)

    # Hero + Predictions
    col_hero, col_pred = st.columns([2, 1])
    with col_hero:
        hero(race)
    with col_pred:
        predictions_panel(preds)

    # Quick stats
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        card("Status", "<div style='color:#34d399;'>GREEN</div>")
    with qc2:
        card("Air", "<div style='color:#e2e8f0;'>24°C</div>")
    with qc3:
        card("Track", "<div style='color:#fb923c;'>38°C</div>")
    with qc4:
        card("Defending", "<div style='color:#facc15;'>VER</div>")

    st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
    header("Standings", "")
    standings_section(DRIVERS)


if __name__ == "__main__":
    main()
