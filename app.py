import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
import time
import glob
import ta

st.set_page_config(layout="wide")

def calculate_rsi(data, window):
    delta = data.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    average_gain = up.rolling(window).mean()
    average_loss = abs(down.rolling(window).mean())
    rs = average_gain / average_loss
    return (100 - (100 / (1 + rs))).round(2)

def calculate_bollinger_bands(data, window):
    rolling_mean = data.rolling(window).mean()
    rolling_std = data.rolling(window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return upper_band.round(2), lower_band.round(2)

def calculate_macd(data, short_window, long_window):
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line.round(2), signal_line.round(2)

@st.cache_data(ttl=3600)  # cache for 1 hour
def get_stock_data(ticker, period):
    filename = f'DB/{ticker}.parquet'
    
    if os.path.exists(filename):
        data = pd.read_parquet(filename)
        last_date = data.index[-1]
        today = pd.Timestamp.now().normalize()
        if today > last_date:
            new_data = download_data(ticker, period)
            if not new_data.empty:
                data = pd.concat([data, new_data])
                data.index = pd.to_datetime(data.index)
                data = data[~data.index.duplicated(keep='first')]
                data.to_parquet(filename)
    else:
        data = download_data(ticker, period)
        if not data.empty:
            data.to_parquet(filename)

    return data

def download_data(ticker, period):
    with st.spinner("Downloading data..."):
        time.sleep(3)

    data = yf.download(ticker, period=period)
    if data.empty:
        return data
    data['MA50'] = data['Close'].rolling(window=50).mean().round(2)
    data['MA200'] = data['Close'].rolling(window=200).mean().round(2)
    data['RSI'] = calculate_rsi(data['Close'], 14)
    data['UpperBB'], data['LowerBB'] = calculate_bollinger_bands(data['Close'], 20)
    data['MACD'], data['Signal'] = calculate_macd(data['Close'], 12, 26)
    
    data.to_parquet(f'DB/{ticker}.parquet')
    
    return data

def create_charts(data_dict):
    fig = go.Figure()
    for stock_filter, data in data_dict.items():
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name=stock_filter, mode='lines+markers', hovertemplate='Valor: %{y}<br>Data: %{x}<extra></extra>'))
    fig.update_layout(hovermode='x')
    return fig

def create_volume_chart(data_dict):
    fig = go.Figure()
    for stock_filter, data in data_dict.items():
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name=stock_filter, hovertemplate='Volume: %{y}<br>Data: %{x}<extra></extra>'))
    fig.update_layout(hovermode='x')
    return fig

def create_table(data_dict):
    if not data_dict:
        st.error("Nenhum dado para exibir.")
        return
    data = pd.concat(data_dict.values(), keys=data_dict.keys())
    data['Change'] = data['Close'].diff()
    increase_icon = "🔼"
    decrease_icon = "🔽"
    data['Change'] = data['Change'].apply(lambda x: increase_icon if x > 0 else (decrease_icon if x < 0 else ""))
    data[['Abertura', 'Máximo', 'Mínimo', 'Fechamento']] = data[['Open', 'High', 'Low', 'Close']].apply(lambda x: 'R$ ' + x.round(2).astype(str))
    data = data.drop(['Open', 'High', 'Low', 'Close'], axis=1)
    data = data.style.background_gradient(cmap='Greys')
    return data


def create_candlestick_chart(data, indicators):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlestick'), row=1, col=1)
    
    if 'MA50' in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='MA50', line=dict(color='blue')), row=1, col=1)
    
    if 'MA200' in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], mode='lines', name='MA200', line=dict(color='orange')), row=1, col=1)
    
    if 'BB' in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['UpperBB'], mode='lines', name='UpperBB', line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['LowerBB'], mode='lines', name='LowerBB', line=dict(color='red')), row=1, col=1)
    
    if 'RSI' in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')), row=2, col=1)

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (R$)',
        template='plotly_white'
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis2_title='RSI',
        yaxis2_range=[0, 100]
    )

    return fig

def display_metrics(data):
    if data.shape[0] < 2:
        st.error("Not enough data to display metrics.")
        return

    current_value = data['Close'].iloc[-1]
    closing_value = data['Close'].iloc[-2]
    max_value = data['High'].iloc[-1]
    min_value = data['Low'].iloc[-1]
    movement = (current_value - closing_value) / closing_value * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Valor Atual", value=f"R$ {current_value:.2f}")
    with col2:
        st.metric(label="Fechamento", value=f"R$ {closing_value:.2f}")
    with col3:
        st.metric(label="Máximo", value=f"R$ {max_value:.2f}")
    with col4:
        st.metric(label="Mínimo", value=f"R$ {min_value:.2f}")
    with col5:
        st.metric(label="Movimentação", value=f"{movement:.2f}%", delta_color="inverse" if movement < 0 else "normal")

def combine_parquet_files():
    parquet_files = glob.glob('DB/*.parquet')
    combined_data = pd.DataFrame()
    for file in parquet_files:
        data = pd.read_parquet(file)
        combined_data = pd.concat([combined_data, data])
    combined_data.to_parquet('DB/all_data.parquet')

def main():
    st.sidebar.image("Imagens/dks__3_-removebg-preview.png")
    st.sidebar.title("Análise de Ações, Criptomoedas e Forex")
    page = st.sidebar.selectbox("Escolha uma página", ["Ações", "Criptomoedas", "Forex"])

    if page == "Ações":
        options = ['PETR4.SA', 'BRKM5.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'B3SA3.SA', 'BRML3.SA', 'WEGE3.SA', 'SUZB3.SA', 'CSNA3.SA', 'ABEV3.SA', 'BBAS3.SA', 'BRAP4.SA', 'CIEL3.SA', 'CMIG4.SA', 'CPFE3.SA', 'CPLE6.SA', 'CSAN3.SA', 'CYRE3.SA']
    elif page == "Criptomoedas":
        options = ['BTC-USD', 'ETH-USD', 'LTC-USD', 'BCH-USD']
    else:
        options = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCAD=X', 'USDCHF=X', 'AUDUSD=X']

    selected_options = st.sidebar.multiselect("Ações, Criptomoedas ou Pares de Moedas", options)
    time_filter = st.sidebar.selectbox("Período", ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '3y', '4y', '5y'])

    indicators = st.sidebar.multiselect("Indicadores Técnicos", ['MA50', 'MA200', 'BB', 'RSI', 'MACD'])

    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button('Atualizar Dados'):
            for stock_filter in selected_options:
                get_stock_data(stock_filter, time_filter)
            st.write("Dados atualizados com sucesso!")
    with col2:
        if st.button('Limpar Cache'):
            st.cache_data.clear()

    data_dict = {}
    for stock_filter in selected_options:
        data = get_stock_data(stock_filter, time_filter)
        if data is None or data.empty:
            st.error(f"Erro ao carregar dados para {stock_filter}. Tente novamente.")
        else:
            data.index = pd.to_datetime(data.index).strftime("%d/%m/%Y")
            data_dict[stock_filter] = data
            st.header(f"Ticket escolhido {stock_filter}.")
            display_metrics(data)

            tab1, tab2, tab3, tab4 = st.tabs(["Candlestick", "Linha", "Volume","Tabela"])

            with tab1:
                with st.container(border=True):
                    st.header("Gráfico de Candlestick")
                    fig = create_candlestick_chart(data, indicators)
                    st.plotly_chart(fig, use_container_width=True, height=800)

            with tab2:
                with st.container(border=True):
                    st.header("Gráficos de Linha")
                    fig = create_charts(data_dict)
                    st.plotly_chart(fig, use_container_width=True, height=800)

            with tab3:
                with st.container(border=True):
                    st.header("Gráficos de Volume")
                    fig = create_volume_chart(data_dict)
                    st.plotly_chart(fig, use_container_width=True, height=800)
 
            with tab4:
                with st.container(border=True):
                    st.header("Tabela de Dados")
                    table = create_table(data_dict)
                    st.dataframe(table, use_container_width=True, hide_index=None)
                

    combine_parquet_files()

if __name__ == "__main__":
    main()
