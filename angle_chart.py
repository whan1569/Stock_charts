import os
import pandas as pd
import plotly.express as px

data_dir = "./nasdaq_etf_data"
etf_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

summary = []

for file in etf_files:
    path = os.path.join(data_dir, file)
    etf_name = file.split("_")[0]  # 예: XLB

    # CSV 구조가 3줄 헤더이므로, 4번째 줄부터 사용
    df = pd.read_csv(path, skiprows=3, header=None)
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    df["Date"] = pd.to_datetime(df["Date"])

    latest = df.iloc[-1]

    summary.append({
        "Sector": etf_name,      # 임시로 섹터 = ETF
        "ETF": etf_name,
        "Date": latest["Date"],
        "Price": latest["Close"],
        "Volume": latest["Volume"]
    })

# 데이터프레임 생성
df_summary = pd.DataFrame(summary)
df_summary["Price"] = pd.to_numeric(df_summary["Price"], errors='coerce')
df_summary["Volume"] = pd.to_numeric(df_summary["Volume"], errors='coerce')

# ▶️ Sunburst 차트: 다각형 기반 앵글형 계층 시각화
fig = px.sunburst(
    df_summary,
    path=["Sector", "ETF"],
    values="Volume",
    color="Price",
    color_continuous_scale="RdYlGn",
    title="ETF 평면 다각형 기반 계층 시각화 (Sunburst)"
)

fig.update_layout(
    margin=dict(t=50, l=20, r=20, b=20),
    uniformtext=dict(minsize=10, mode='hide')
)
fig.show()
