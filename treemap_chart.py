import os
import pandas as pd
import plotly.express as px

data_dir = "./nasdaq_etf_data"
etf_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

summary = []

for file in etf_files:
    path = os.path.join(data_dir, file)
    etf_name = file.split("_")[0]  # 예: XLB

    # 실제 데이터는 4번째 줄부터 시작 (앞 3줄은 헤더 및 라벨)
    df = pd.read_csv(path, skiprows=3, header=None)
    
    # 날짜와 OHLCV 컬럼 붙이기
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    df["Date"] = pd.to_datetime(df["Date"])

    # 최신 데이터 추출
    latest = df.iloc[-1]

    summary.append({
        "ETF": etf_name,
        "Sector": etf_name,
        "Ticker": etf_name,
        "Date": latest["Date"],
        "Price": latest["Close"],
        "Volume": latest["Volume"]
    })

# 요약 테이블
df_summary = pd.DataFrame(summary)
df_summary["Price"] = pd.to_numeric(df_summary["Price"], errors='coerce')
df_summary["Volume"] = pd.to_numeric(df_summary["Volume"], errors='coerce')

# 차트 그리기
fig = px.treemap(
    df_summary,
    path=["Sector", "Ticker"],
    values="Volume",
    color="Price",
    color_continuous_scale="RdYlGn",
    title="ETF별 최신 거래량 및 가격 (Treemap)"
)
fig.update_layout(margin=dict(t=40, l=20, r=20, b=20))
fig.show()
