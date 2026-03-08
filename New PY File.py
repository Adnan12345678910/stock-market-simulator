
# pip install streamlit pandas numpy
import streamlit as st
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Classroom Stock Market", layout="wide")

st.title("📈 Classroom Stock Market Simulation")

# Auto refresh every 3 seconds
st_autorefresh(interval=3000, key="marketrefresh")

students = ["Ali","Sara","John","Ravi","Fatima","Arjun"]

companies = {
    "Apple":150,
    "Google":120,
    "Amazon":100,
    "Tesla":200,
    "Microsoft":180,
    "Nvidia":220,
    "Meta":130,
    "Netflix":140,
    "Adobe":160,
    "Intel":90
}

# Initialize prices
if "prices" not in st.session_state:
    st.session_state.prices = companies.copy()

# Price history for charts
if "price_history" not in st.session_state:
    st.session_state.price_history = {c:[p] for c,p in companies.items()}

# Player accounts
if "players" not in st.session_state:

    st.session_state.players = {}

    for s in students:

        st.session_state.players[s] = {
            "cash":10000,
            "portfolio":{c:0 for c in companies}
        }

# Portfolio value history
if "portfolio_history" not in st.session_state:
    st.session_state.portfolio_history = {s:[10000] for s in students}


# MARKET UPDATE FUNCTION
def update_market():

    for c in st.session_state.prices:

        change = random.uniform(-3,3)

        st.session_state.prices[c] += change
        st.session_state.prices[c] = round(st.session_state.prices[c],2)

        st.session_state.price_history[c].append(st.session_state.prices[c])


    for s in students:

        p = st.session_state.players[s]

        val = 0

        for c in p["portfolio"]:
            val += p["portfolio"][c] * st.session_state.prices[c]

        total = val + p["cash"]

        st.session_state.portfolio_history[s].append(total)


update_market()


# MARKET TABLE
st.subheader("🏢 Market Prices")

price_df = pd.DataFrame(
    st.session_state.prices.items(),
    columns=["Company","Price"]
)

st.dataframe(price_df, use_container_width=True)


# STOCK CHART
st.subheader("📈 Stock Price Charts")

for company in companies:

    chart_data = pd.DataFrame(
        st.session_state.price_history[company],
        columns=[company]
    )

    st.line_chart(chart_data)


# TRADING PANEL
st.subheader("💼 Trading")

student = st.selectbox("Select Student", students)

player = st.session_state.players[student]

st.write("💰 Cash Balance:", round(player["cash"],2))


company = st.selectbox("Company", list(companies.keys()))

action = st.radio("Action", ["Buy","Sell"])

qty = st.number_input("Quantity", min_value=1)

price = st.session_state.prices[company]


if st.button("Execute Trade"):

    if action=="Buy":

        cost = price * qty

        if player["cash"] >= cost:

            player["cash"] -= cost
            player["portfolio"][company] += qty

            st.success("Trade Successful")

        else:

            st.error("Not enough cash")


    if action=="Sell":

        if player["portfolio"][company] >= qty:

            player["portfolio"][company] -= qty
            player["cash"] += price * qty

            st.success("Trade Successful")

        else:

            st.error("Not enough shares")


# PORTFOLIO
st.subheader("📦 Portfolio")

portfolio_df = pd.DataFrame(
    player["portfolio"].items(),
    columns=["Company","Shares"]
)

st.table(portfolio_df)


# PORTFOLIO VALUE
value = 0

for c in player["portfolio"]:
    value += player["portfolio"][c] * st.session_state.prices[c]

total = value + player["cash"]

profit = total - 10000


st.subheader("💰 Portfolio Summary")

st.write("Portfolio Value:", round(value,2))
st.write("Total Money:", round(total,2))


if profit > 0:
    st.success(f"Profit: ₹{round(profit,2)}")
else:
    st.error(f"Loss: ₹{round(profit,2)}")


# PORTFOLIO GROWTH GRAPHS
st.subheader("📊 Portfolio Growth (Live Stock Graphs You Own)")

for c in player["portfolio"]:

    if player["portfolio"][c] > 0:

        st.write(f"{c} Shares Owned: {player['portfolio'][c]}")

        chart_data = pd.DataFrame(
            st.session_state.price_history[c],
            columns=[c]
        )

        st.line_chart(chart_data)


# LEADERBOARD
st.subheader("🏆 Leaderboard")

data = []

for s in students:

    p = st.session_state.players[s]

    val = 0

    for c in p["portfolio"]:
        val += p["portfolio"][c] * st.session_state.prices[c]

    total = val + p["cash"]

    data.append([s,total])


leaderboard = pd.DataFrame(data, columns=["Student","Total Value"])

leaderboard = leaderboard.sort_values("Total Value", ascending=False)

st.table(leaderboard)