import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Dream Catcher AI", layout="wide")
st.title(" Dream Catcher Predictor + Tracker")

# Full Wheel Data
wheel_info = {
    1:  {"label": "1",  "color": " Yellow", "pays": 1,   "type": "number"},
    2:  {"label": "2",  "color": " Blue",  "pays": 2,   "type": "number"},
    5:  {"label": "5",  "color": " Purple", "pays": 5,   "type": "number"},
    10: {"label": "10", "color": " Green", "pays": 10,  "type": "number"},
    20: {"label": "20", "color": " Orange", "pays": 20,  "type": "number"},
    40: {"label": "40", "color": " Red",   "pays": 40,  "type": "number"},
    "X2":{"label": "x2","color": " Black", "pays": 2,    "type": "multiplier"},
    "X7":{"label": "x7","color": " Gold",  "pays": 7,    "type": "multiplier"}
}

possible = list(wheel_info.keys())

if 'history' not in st.session_state:
    st.session_state.history = []
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

# Input Buttons
st.subheader("Tap to Log Last Spin")
cols = st.columns(4)
for i, outcome in enumerate(possible):
    info = wheel_info[outcome]
    with cols[i % 4]:
        if st.button(f"{info['label']} {info['color']}", key=f"btn_{i}", use_container_width=True):
            st.session_state.history.append(outcome)
            st.rerun()

# Controls
col1, col2, col3 = st.columns([2,2,1])
with col1:
    order = st.slider("Markov Order", 1, 3, 2)
with col2:
    alpha = st.slider("Smoothing ()", 0.0, 2.0, 0.5, 0.1)
with col3:
    if st.button("Undo Last"):
        if st.session_state.history: st.session_state.history.pop(); st.rerun()
    if st.button("Clear All"):
        st.session_state.history = []
        st.session_state.predictions = []
        st.rerun()

if st.button(" Predict Next + Update", type="primary"):
    if len(st.session_state.history) < order + 1:
        st.warning("Log more spins first.")
    else:
        h = st.session_state.history
        transitions = defaultdict(lambda: defaultdict(int))
        for i in range(len(h) - order):
            state = tuple(h[i:i+order])
            nxt = h[i + order]
            transitions[state][nxt] += 1

        last_state = tuple(h[-order:])
        counts = transitions[last_state]

        # Bayesian smoothing
        smoothed = {o: alpha for o in possible}
        total = alpha * len(possible)
        for o, c in counts.items():
            smoothed[o] += c
            total += c

        probs = {k: v / total for k, v in smoothed.items()}
        best = max(probs, key=probs.get)

        # EV Calculation (Fixed for multipliers)
        best_info = wheel_info[best]
        if best_info["type"] == "number":
            ev = probs[best] * best_info["pays"] - (1 - probs[best])
        else:
            # For multipliers, EV is more complex (depends on next number)
            ev = "N/A (depends on next number)"

        st.session_state.predictions.append({
            "time": datetime.now().strftime("%H:%M"),
            "predicted": best,
            "prob": round(probs[best], 4),
            "ev": ev
        })

        display_ev = ev if isinstance(ev, str) else f"{ev:.3f}"
        st.success(f"**Best Bet: {best_info['label']} {best_info['color']}**   {probs[best]:.1%} | EV: {display_ev}")

        # Charts
        st.subheader(" Probability Distribution")
        prob_df = pd.DataFrame({
            "Outcome": [wheel_info[o]["label"] for o in possible],
            "Probability": [probs[o] for o in possible]
        })
        fig = px.bar(prob_df, x="Outcome", y="Probability", text_auto='.1%')
        fig.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig, use_container_width=True)

# History
st.subheader("History")
if st.session_state.history:
    display = [wheel_info[x]["label"] for x in st.session_state.history[-20:]]
    st.write("  ".join(display))

st.subheader(" Performance")
if st.session_state.predictions:
    df = pd.DataFrame(st.session_state.predictions)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Gamble responsibly")
