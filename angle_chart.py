import os
import glob
import pandas as pd
import plotly.graph_objects as go

def load_etf_csv(filepath):
    etf_name = os.path.basename(filepath).split('_')[0]
    columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

    df_raw = pd.read_csv(filepath, skiprows=3, header=None, names=columns)
    df_raw['Date'] = pd.to_datetime(df_raw['Date'], errors='coerce')
    df_raw = df_raw[df_raw['Date'].notnull()]

    df = df_raw[['Date', 'Close', 'Volume']].copy()
    df.rename(columns={
        'Close': f'{etf_name}_Close',
        'Volume': f'{etf_name}_Volume'
    }, inplace=True)

    return df

def load_all_etfs(data_dir):
    file_pattern = os.path.join(data_dir, '*_1d.csv')
    file_list = glob.glob(file_pattern)

    df_merged = None
    for f in file_list:
        df = load_etf_csv(f)
        if df_merged is None:
            df_merged = df
        else:
            df_merged = pd.merge(df_merged, df, on='Date', how='outer')

    df_merged.sort_values('Date', inplace=True)
    df_merged.reset_index(drop=True, inplace=True)
    df_merged.set_index('Date', inplace=True)
    df_merged.fillna(method='ffill', inplace=True)

    return df_merged

def prepare_sunburst_values_colors(df_snapshot, etf_names):
    values = []
    colors = []

    for etf in etf_names:
        vol_col = f'{etf}_Volume'
        close_col = f'{etf}_Close'
        volume = df_snapshot.get(vol_col, 0)
        close = df_snapshot.get(close_col, 0)
        values.append(volume)
        colors.append(close)

    total_volume = sum(values)
    weighted_avg_close = (sum(v*c for v,c in zip(values, colors))/total_volume) if total_volume > 0 else 0

    values = [total_volume] + values
    colors = [weighted_avg_close] + colors

    return values, colors

def plot_sunburst_timeseries_monthly_fixed_order(df_all):
    # 월별 대표 거래일 추출
    monthly_dates = df_all.index.to_series().resample('MS').first().dropna().tolist()
    monthly_dates = [d for d in monthly_dates if d in df_all.index]

    # etf_names 고정 (정렬된 상태)
    sample_snapshot = df_all.loc[monthly_dates[0]]
    etf_names = sorted(set([col.split('_')[0] for col in sample_snapshot.index if '_' in col and col.endswith('Volume')]))

    # labels, parents 고정 (Market 루트, 그 밑 ETF들)
    labels = ['Market'] + etf_names
    parents = [''] + ['Market'] * len(etf_names)

    # 첫 프레임 값 준비
    values, colors = prepare_sunburst_values_colors(sample_snapshot, etf_names)

    fig = go.Figure(
        data=[go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            sort=False,  # 입력 순서대로 고정 배치 시도
            marker=dict(
                colors=colors,
                colorscale='RdYlGn',
                colorbar=dict(title='Close Price'),
                reversescale=False,
                showscale=True,
            ),
            branchvalues='total',
            maxdepth=2,
            insidetextorientation='radial',
        )],
        layout=go.Layout(
            title="ETF 시장 구조 - 거래량(크기), 종가(색상) 기반 Sunburst (월별, 위치 고정 순서)",
            margin=dict(t=40, l=0, r=0, b=0),
            updatemenus=[dict(
                type="buttons",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 800, "redraw": True},
                                      "fromcurrent": True}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}])
                ],
                direction="left",
                pad={"r": 10, "t": 70},
                showactive=True,
                x=0.1,
                y=0,
                xanchor="right",
                yanchor="top"
            )]
        ),
        frames=[]
    )

    # 월별 각 날짜에 대해 values, colors 업데이트하며 프레임 생성
    frames = []
    for date in monthly_dates:
        snapshot = df_all.loc[date]
        values_f, colors_f = prepare_sunburst_values_colors(snapshot, etf_names)
        frames.append(go.Frame(
            data=[go.Sunburst(
                labels=labels,      # 고정된 순서
                parents=parents,    # 고정된 순서
                values=values_f,
                sort=False,
                marker=dict(
                    colors=colors_f,
                    colorscale='RdYlGn',
                    reversescale=False,
                    showscale=False,
                ),
                branchvalues='total',
                maxdepth=2,
                insidetextorientation='radial',
            )],
            name=str(date.date())
        ))

    fig.frames = frames

    # 슬라이더 설정
    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Date: ", "visible": True, "xanchor": "right"},
        pad={"b": 10, "t": 50},
        steps=[dict(
            method="animate",
            args=[[str(date.date())],
                  {"mode": "immediate",
                   "frame": {"duration": 0, "redraw": True},
                   "transition": {"duration": 0}}],
            label=str(date.date())
        ) for date in monthly_dates]
    )]

    fig.update_layout(sliders=sliders)

    fig.show()

if __name__ == '__main__':
    data_dir = './nasdaq_etf_data'  # 실제 데이터 경로로 바꾸세요
    df_all = load_all_etfs(data_dir)
    print("데이터 샘플:")
    print(df_all.head())
    plot_sunburst_timeseries_monthly_fixed_order(df_all)
