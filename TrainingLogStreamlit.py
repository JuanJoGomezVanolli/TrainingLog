import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import timedelta
import matplotlib.pyplot as plt


SPREADSHEET_ID = "1J8m4QyDDnrdxqjIvDZFEZTPdSLYBnO-GLAzgMPBc8DA"
GID = "916514716"          # e.g., "0"
url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
df = pd.read_csv(url)          # Add options like sep=";", decimal="," if needed



################# Training Hours by last Day/Week/Month code and logic
st.title("Training Hours Overview 🥋🏋️") #Titulo
st.caption("Filter to view total training hours over the last day, week, or month.") # texto en pantalla


df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", dayfirst=True) # Formateamos la columna del DF a un formato valido

anchor_date = df["Date"].max()

range_choice = st.radio(
    "Select range (relative to latest date in data):",
    ["Last Day", "Last Week", "Last Month"],
    horizontal=True
)

if range_choice == "Last Day":
    start_date = anchor_date
elif range_choice == "Last Week":
    start_date = anchor_date - timedelta(days=6)  # 7 days inclusive (anchor_date minus 6)
else:  # "Last Month"
    # 30-day lookback inclusive
    start_date = anchor_date - timedelta(days=29)

mask = (df["Date"] >= start_date) & (df["Date"] <= anchor_date)
df_period = df.loc[mask].copy()

daily_hours = (
    df_period.groupby("Date", as_index=False)["Cuantos Minutos"]
    .sum()
    .rename(columns={"Cuantos Minutos": "Total Minutos"})
)
daily_hours["Total Horas"] = daily_hours["Total Minutos"] / 60.0

# Fill missing days with 0 for nicer charts
all_days = pd.date_range(start=start_date, end=anchor_date, freq="D")
daily_hours = (
    pd.DataFrame({"Date": all_days})
    .merge(daily_hours[["Date", "Total Horas"]], on="Date", how="left")
    .fillna({"Total Horas": 0})
)

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Total Training Hours by Day")
with col2:
    total_hours = daily_hours["Total Horas"].sum()
    st.metric("Total Hours (Selected Range)", f"{total_hours:.2f}")

st.caption(
    f"Window: {start_date.strftime('%d/%m/%Y')} ➜ {anchor_date.strftime('%d/%m/%Y')} "
    f"({range_choice})"
)

chart_df = daily_hours.set_index("Date")["Total Horas"]
st.bar_chart(chart_df)

#################





################# Training Hours by Type Logic
st.subheader("Activity Mix by Type (Hours)")

if df_period.empty:
    st.info("No data in the selected window to display the activity mix.")
else:
    activity_hours = (
        df_period.groupby("Activity Type", as_index=False)["Cuantos Minutos"]
        .sum()
        .rename(columns={"Cuantos Minutos": "Total Minutos"})
    )
    activity_hours["Total Horas"] = activity_hours["Total Minutos"] / 60.0

    if activity_hours["Total Horas"].sum() == 0:
        st.info("All activities have 0 hours in the selected window.")
    else:
        fig, ax = plt.subplots(facecolor="#0f1116")
        ax.set_facecolor("#0f1116")  # ensure axes area is also white

        

        ax.pie(
            activity_hours["Total Horas"],
            labels=activity_hours["Activity Type"],
            autopct=lambda p: f"{p:.0f}%" if p >= 1 else "",
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.10},  # donut look; remove for full pie
            textprops={"color": "white", "fontfamily": "Source Sans"}
        )

        ax.axis("equal")
        st.pyplot(fig)








####### Section to Show Entire Data Frame, or basically all the entries
st.title("Training Log")
st.write("Below are all entries")
st.dataframe(df) 

