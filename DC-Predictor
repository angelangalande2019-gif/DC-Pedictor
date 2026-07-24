import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Wheel AI Tracker", layout="wide")
st.title("🎡 Wheel Predictor + Tracker + Charts")

# Wheel data
wheel_info = {
    1: {"color": "🟡 Yellow", "pays": 1},
    2: {"color": "🔵 Blue", "pays": 2},
    5: {"color": "🟣 Purple", "pays": 5},
    10: {"color": "🟢 Green", "pays": 10},
    20: {"color": "🟠 Orange", "pays": 20},
    40: {"color": "🔴 Red", "pays": 40}
}
possible = [1, 2, 5, 10, 20, 40]

# Session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

# Quick Input Buttons
st.subheader("Tap to Log Last Spin")
cols = st.columns(6)
for i, num in enumerate(possible):
    with cols[i]:
        if st.button(f"{num} {wheel_info[num]['color']}", key=f"btn_{num}", use_container_width=True):
            st.session_state.history.append(num)
            st.rerun()

# Controls
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    order = st.slider("Markov Order", 1, 3, 2)
with col2:
    alpha = st.slider("Smoothing (α)", 0.0, 2.0, 0.5, 0.1)
with col3:
    if st.button("Undo Last"):
        if st.session_state.history:
            st.session_state.history.pop()
            st.rerun()
    if st.button("Clear All"):
        st.session_state.history = []
        st.session_state.predictions = []
        st.rerun()

# Predict
if st.button("🔮 Predict Next + Update", type="primary"):
    if len(st.session_state.history) < order + 1:
        st.warning("Add more spins first.")
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
        ev = probs[best] * wheel_info[best]["pays"] - (1 - probs[best])

        st.session_state.predictions.append({
            "time": datetime.now().strftime("%H:%M"),
            "predicted": best,
            "prob": round(probs[best], 4),
            "ev": round(ev, 4)
        })

        st.success(f"**Best Bet: {best} {wheel_info[best]['color']}** — {probs[best]:.1%} | EV: {ev:.3f}")

        # === CHARTS ===
        st.subheader("📊 Probability Visualization")

        # Bar Chart
        prob_df = pd.DataFrame({
            "Number": possible,
            "Probability": [probs[o] for o in possible],
            "Color": [wheel_info[o]["color"] for o in possible]
        })

        fig = px.bar(prob_df, x="Number", y="Probability", 
                     color="Color", text_auto='.1%',
                     title="Next Spin Probability Distribution")
        fig.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig, use_container_width=True)

        # Pie Chart
        fig2 = px.pie(prob_df, names="Number", values="Probability", 
                      title="Probability Breakdown", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

# History & Performance
st.subheader("History")
if st.session_state.history:
    st.write(" → ".join(map(str, st.session_state.history[-30:])))
else:
    st.info("No spins logged yet.")

st.subheader("📈 Performance")
if st.session_state.predictions:
    pred_df = pd.DataFrame(st.session_state.predictions)
    st.dataframe(pred_df, use_container_width=True, hide_index=True)
    st.metric("Total Spins", len(st.session_state.history))

st.caption("Gamble responsibly • Data is stored only during this session")
