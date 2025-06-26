import os
import pandas as pd
import plotly.graph_objects as go

data_dir = "./nasdaq_etf_data"
etf_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

dfs = []
for file in etf_files:
    path = os.path.join(data_dir, file)
    etf_name = file.split("_")[0]

    df = pd.read_csv(path, skiprows=3, header=None)
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    df["Date"] = pd.to_datetime(df["Date"])
    df["ETF"] = etf_name
    df["Sector"] = etf_name

    df = df[["Date", "ETF", "Sector", "Close", "Volume"]].rename(columns={"Close": "Price"})
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# 월말 데이터 리샘플링
df_all["YearMonth"] = df_all["Date"].dt.to_period("M")
df_monthly = df_all.groupby(["YearMonth", "ETF", "Sector"]).last().reset_index()
df_monthly["Date"] = df_monthly["YearMonth"].dt.to_timestamp()

# 최근 월말 데이터 선택
latest_month = df_monthly["Date"].max()
df_frame = df_monthly[df_monthly["Date"] == latest_month].copy()

# labels, parents 설정
sectors = df_frame["Sector"].unique().tolist()
labels = sectors + df_frame["ETF"].tolist()
parents = [""] * len(sectors) + df_frame["Sector"].tolist()

values = [0] * len(sectors) + df_frame["Volume"].tolist()
colors = [None] * len(sectors) + df_frame["Price"].tolist()

fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    marker=dict(
        colors=colors,
        colorscale="RdYlGn",
        colorbar=dict(title="Price"),
        cmin=df_monthly["Price"].min(),
        cmax=df_monthly["Price"].max(),
    ),
    branchvalues="total",
))

fig.update_layout(
    title=f"Sunburst Chart for Latest Month: {latest_month.date()}",
    margin=dict(t=50, l=20, r=20, b=20),
)

fig.show()
