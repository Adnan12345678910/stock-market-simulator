st.set_page_config(layout="wide", page_title="Classroom Market Simulator")

# ---------------- SESSION VARIABLES ----------------
if "session_started" not in st.session_state:
    st.session_state.session_started=False

if "start_time" not in st.session_state:
    st.session_state.start_time=None

if "session_ended" not in st.session_state:
    st.session_state.session_ended=False

STATE_FILE="market_state.pkl"
SESSION_DURATION=21*60
INITIAL_CASH=314000

groups=["Group 1","Group 2","Group 3","Group 4","Group 5","Group 6"]
ai_traders=["ChatGPT","Gemini"]

assets=[
"Tesla","Apple","Nvidia",
"Gold","Silver","Crude Oil",
"Bitcoin","Ethereum"
]

TRANSACTION_FEE=0.005


# ---------------- SAVE STATE ----------------
def save_state():

    data=dict(st.session_state)

    if "refresh" in data:
        del data["refresh"]

    with open(STATE_FILE,"wb") as f:
        pickle.dump(data,f)


# ---------------- LOAD STATE ----------------
def load_state():

    if os.path.exists(STATE_FILE):

        with open(STATE_FILE,"rb") as f:

            data=pickle.load(f)

            for k,v in data.items():

                if k!="refresh":
                    st.session_state[k]=v


if "initialized" not in st.session_state:

    load_state()
    st.session_state.initialized=True


# ---------------- CRYPTO PRICE ----------------
def get_crypto():

    try:

        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

        data=requests.get(url).json()

        return data["bitcoin"]["usd"],data["ethereum"]["usd"]

    except:

        return 45000,3000


# ---------------- RESET GAME ----------------
def reset_game():

    btc,eth=get_crypto()

    st.session_state.prices={
    "Tesla":200,
    "Apple":150,
    "Nvidia":220,
    "Gold":2000,
    "Silver":25,
    "Crude Oil":80,
    "Bitcoin":btc,
    "Ethereum":eth
    }

    st.session_state.players={}

    for p in groups+ai_traders:

        st.session_state.players[p]={
        "cash":INITIAL_CASH,
        "portfolio":{a:0.0 for a in assets},
        "invested":False
        }


if "prices" not in st.session_state:

    reset_game()


for ai in ai_traders:

    if ai not in st.session_state.players:

        st.session_state.players[ai]={
        "cash":INITIAL_CASH,
        "portfolio":{a:0.0 for a in assets},
        "invested":False
        }


# ---------------- NAVIGATION ----------------
page=st.sidebar.radio(
"Navigation",
["Home","Trading Desk","Live Market","Portfolios"]
)


# ---------------- AUTO REFRESH ----------------
if page not in ["Trading Desk","Home"]:
    st_autorefresh(interval=1000,key="refresh")


# ---------------- TIMER ----------------
def remaining_time():

    if not st.session_state.session_started:
        return None

    elapsed=time.time()-st.session_state.start_time

    return max(0,SESSION_DURATION-int(elapsed))


remain=remaining_time()

if remain is None:

    timer_text="SESSION NOT STARTED"

else:

    mins=remain//60
    secs=remain%60

    timer_text=f"{mins}m {secs}s"


st.markdown(f"""
<div style="
position:fixed;
top:20px;
right:30px;
background:#111;
color:#FFD700;
padding:15px 25px;
font-size:22px;
font-weight:bold;
border-radius:12px;
border:3px solid #FFD700;
z-index:999999;">
⏱ TIME LEFT: {timer_text}
</div>
""",unsafe_allow_html=True)


# ---------------- MARKET ENGINE ----------------
def update_market():

    for a in st.session_state.prices:

        p=st.session_state.prices[a]

        if a in ["Tesla","Apple","Nvidia"]:
            change=random.gauss(0,2)

        elif a=="Gold":
            change=random.gauss(0,0.6)

        elif a=="Silver":
            change=random.gauss(0,3)

        elif a=="Crude Oil":

            if random.random()<0.1:
                change=random.uniform(-15,20)
            else:
                change=random.uniform(-2,2)

        elif a in ["Bitcoin","Ethereum"]:
            change=random.gauss(0,150)

        st.session_state.prices[a]=round(max(1,p+change),2)


# ---------------- AI TRADERS ----------------
def ai_trade():

    for ai in ai_traders:

        player=st.session_state.players[ai]

        asset=random.choice(assets)

        price=st.session_state.prices[asset]

        amount=random.randint(5000,20000)

        qty=amount/price

        if player["cash"]>amount:

            player["cash"]-=amount
            player["portfolio"][asset]+=qty
            player["invested"]=True


# ---------------- SESSION ACTIVE ----------------
def session_active():

    if not st.session_state.session_started:
        return False

    elapsed=time.time()-st.session_state.start_time

    if elapsed>=SESSION_DURATION:

        st.session_state.session_started=False
        st.session_state.session_ended=True

        return False

    return True


# ---------------- HOME ----------------
if page=="Home":

    st.title("Classroom Market Simulator")

    st.write("Teachers: **Adnan Sir & Udayan Sir**")

    c1,c2=st.columns(2)

    if c1.button("Start Session"):

        reset_game()

        st.session_state.session_started=True
        st.session_state.session_ended=False
        st.session_state.start_time=time.time()

        save_state()

    if c2.button("Stop Session"):

        reset_game()

        st.session_state.session_started=False
        st.session_state.session_ended=True
        st.session_state.start_time=None

        save_state()


# ---------------- TRADING DESK ----------------
if page=="Trading Desk":

    st.title("Trading Desk")

    trader=st.selectbox("Trader",groups)

    player=st.session_state.players[trader]

    st.write("Cash:",round(player["cash"],2))

    asset=st.selectbox("Asset",assets)

    price=st.session_state.prices[asset]

    st.write("Price:",price)

    action=st.radio("Action",["Buy","Sell"])

    if asset in ["Bitcoin","Ethereum"]:

        amount=st.number_input("Investment Amount ($)",min_value=1000)

        qty=amount/price

        st.write("Crypto Quantity:",round(qty,6))

    else:

        qty=st.number_input("Quantity",min_value=1)

        amount=qty*price


    if st.button("Execute Trade"):

        fee=amount*TRANSACTION_FEE

        if action=="Buy":

            if player["cash"]>=amount+fee:

                player["cash"]-=amount+fee
                player["portfolio"][asset]+=qty
                player["invested"]=True

                st.success("Trade Executed Successfully")

            else:
                st.error("Not enough cash")

        else:

            if player["portfolio"][asset]>=qty:

                player["portfolio"][asset]-=qty
                player["cash"]+=amount-fee

                st.success("Trade Executed Successfully")

        save_state()


# ---------------- LIVE MARKET ----------------
if page=="Live Market":

    if session_active():

        update_market()
        ai_trade()

    df=pd.DataFrame(
        st.session_state.prices.items(),
        columns=["Asset","Price"]
    )

    st.title("Live Market Prices")

    st.dataframe(df,width="stretch")


# ---------------- PORTFOLIOS ----------------
if page=="Portfolios":

    if session_active():

        update_market()
        ai_trade()

    leaderboard=[]

    for p in groups+ai_traders:

        player=st.session_state.players[p]

        value=0

        for a in assets:
            value+=player["portfolio"][a]*st.session_state.prices[a]

        total=value+player["cash"]

        profit=total-INITIAL_CASH

        if player["invested"]:
            leaderboard.append([p,total,profit])


    board=pd.DataFrame(
        leaderboard,
        columns=["Trader","Portfolio Value","Profit/Loss"]
    )

    board=board.sort_values(
        "Portfolio Value",
        ascending=False
    )

    st.title("Live Leaderboard")

    st.dataframe(board,width="stretch")


    if st.session_state.session_ended and len(board)>0:

        winner=board.iloc[0]

        st.success(
        f"SESSION ENDED 🏆 Winner: {winner['Trader']} | Portfolio Value: ${round(winner['Portfolio Value'],2)}"
        )


    st.subheader("All Portfolios")

    for p in groups+ai_traders:

        player=st.session_state.players[p]

        st.write("###",p)

        df=pd.DataFrame(
        player["portfolio"].items(),
        columns=["Asset","Quantity"]
        )

        df["Quantity"]=df["Quantity"].round(6)

        st.table(df)

