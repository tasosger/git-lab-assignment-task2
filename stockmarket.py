from datetime import date
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from st_click_detector import click_detector

# Ideas for improvement:
# 1. Add more stock tickers to the list.  #E
# 2. Allow users to input a custom date range for the stock data. #E
# 3. Allow users to provide their own tickers, with error handling for tickers not in the S&P500. (Remove the ability to click on the icons) #M
# 4. Show information about the stock (e.g., market cap, P/E ratio) alongside the chart. #M
# 5. Investment portfolio tracker: Allow users to input multiple stocks and return their portfolio's current worth. #H
# 6. Add a news section to show the latest news related to the selected stock (you can use the news attribute of yfinance.Ticker). #H

# Create the images as a href elements with tickers as IDs
def show_tickers():
    content = """
        <a href='#' id='MSFT'><img height='60px' width='60px' src='https://banner2.cleanpng.com/20180609/jq/aa8dbj2or.webp'></a>
        <a href='#' id='AAPL'><img height='60px' width='60px' src='https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg'></a>
    """
    return content

# Make the images clickable using st_click_detector
def get_ticker():
    content = show_tickers()
    clicked = click_detector(content)
    return clicked


# Let the user select a start and end date
def get_date_range():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=date(2024, 1, 1), max_value=date.today())
    with col2:
        end_date = st.date_input("End date", value=date.today(), max_value=date.today())

    if start_date >= end_date:
        st.warning("Start date must be before end date.")
        return None, None
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

# Get the stock dataframe for the given ticker using yfinance
def get_dataframe(ticker, start_date, end_date):
    stock_data = yf.Ticker(ticker)
    df = stock_data.history(start=start_date, end=end_date)
    df.reset_index(inplace=True)  # This moves the date from index to a column
    return df

# Create a candlestick chart using plotly
def plot_candlestick(df, ticker):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title=f'{ticker} Stock Price', xaxis_title='Date', yaxis_title='Price (USD)')
    return fig

# Show a plotly chart in Streamlit
def show_plot(fig):
    st.plotly_chart(fig, use_container_width=True)

ticker = get_ticker()

if ticker != "":
    st.write(f"Selected ticker: **{ticker}**")
    start_date, end_date = get_date_range()

    if start_date and end_date:
        df = get_dataframe(ticker, start_date, end_date)
        if df.empty:
            st.error("No data found for the selected date range.")
        else:
            fig = plot_candlestick(df, ticker)
            show_plot(fig)