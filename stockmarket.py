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
        <a href='#' id='SBUX'><img height='60px' width='60px' src='https://upload.wikimedia.org/wikipedia/el/e/e3/Starbucks_logo.svg'></a>
    """
    return content

# Make the images clickable using st_click_detector
def get_ticker():
    content = show_tickers()
    clicked = click_detector(content)
    return clicked


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


def show_news(ticker):
    stock = yf.Ticker(ticker)
    news_items = stock.news

    if not news_items:
        st.info("No news available for this ticker.")
        return

    st.subheader("📰 Latest News")
    # st.write("Raw news data:", news_items)  # TEMPORARY DEBUG

    for entry in news_items[:5]:
        content = entry.get("content", {})
        title = content.get("title", "No title")
        link = content.get("clickThroughUrl", {}).get("url", "#")
        provider = content.get("provider", {}).get("displayName", "Unknown source")
        content_type = content.get("contentType", "Unknown type")

        st.markdown(f"**[{title}]({link})**")
        st.caption(f"Source: {provider} | Type: {content_type}")
        st.markdown("---")

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

def show_info(ticker):
    stock = yf.Ticker(ticker)
    fast_info = stock.fast_info
    info = stock.info

    if not fast_info:
        st.info("No info available for this ticker.")
        return

    st.subheader("📰 Information")
    # st.write("Raw info data:", fast_info)  # TEMPORARY DEBUG

    col1, col2 = st.columns(2)

    # everything is up to 2 decimals precise
    with col1:
        market_cap = fast_info.get("marketCap")
        st.metric("Market Cap", f"${market_cap:,.2f}" if market_cap else "N/A")

        year_high = fast_info.get("yearHigh")
        st.metric("52-Week High", f"${year_high:,.2f}" if year_high else "N/A")

        year_low = fast_info.get("yearLow")
        st.metric("52-Week Low", f"${year_low:,.2f}" if year_low else "N/A")

        volume = fast_info.get("lastVolume")
        st.metric("Volume", f"{volume:,.2f}" if volume else "N/A")

    with col2:
        pe_ratio = info.get("trailingPE")
        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")

        open_price = fast_info.get("open")
        st.metric("Open", f"${open_price:,.2f}" if open_price else "N/A")

        prev_close = fast_info.get("previousClose")
        st.metric("Previous Close", f"${prev_close:,.2f}" if prev_close else "N/A")

        currency = fast_info.get("currency", "N/A")
        st.metric("Currency", currency)

def show_portfolio():
    st.subheader("📊 Investment Portfolio Tracker")

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {}

    # Input section
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker_input = st.text_input("Stock Ticker (e.g. AAPL)", key="ticker_input")
    with col2:
        shares_input = st.number_input("Shares", min_value=1, step=1, key="shares_input")

    # Button to add to portfolio
    if st.button("➕ Add to Portfolio"):
        ticker = ticker_input.strip().upper()
        shares = int(shares_input)
        if ticker:
            if ticker in st.session_state.portfolio:
                st.session_state.portfolio[ticker] += shares
            else:
                st.session_state.portfolio[ticker] = shares
            st.success(f"Added {shares} shares of {ticker} to your portfolio.")

    # Display the current portfolio
    if st.session_state.portfolio:
        st.markdown("---")
        st.markdown("### 📈 Portfolio Summary")

        total_value = 0
        rows = []

        for ticker, shares in st.session_state.portfolio.items():
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.history(period='1d')['Close'].iloc[-1]
                value = current_price * shares
                total_value += value
                rows.append((ticker, shares, current_price, value))
            except Exception:
                rows.append((ticker, shares, "N/A", "N/A"))

        # Display as table
        # Display as table-style blocks
        for row in rows:
            t, s, price, val = row
            st.write(f"**{t}**")
            st.caption(f"Shares: {s}")
            st.caption(f"Price: ${price:,.2f}" if isinstance(price, (float, int)) else f"Price: {price}")
            st.caption(f"Value: ${val:,.2f}" if isinstance(val, (float, int)) else f"Value: {val}")
            st.markdown("---")  # Optional: adds a divider line between stocks


        st.markdown(f"### 💰 Total Portfolio Value: **${total_value:,.2f}**")

# Main Streamlit app
ticker = get_ticker()

if ticker != "":
    df = get_dataframe(ticker)
    fig = plot_candlestick(df, ticker)
    show_plot(fig)
    st.write(f"Selected ticker: **{ticker}**")
    start_date, end_date = get_date_range()

    if start_date and end_date:
        df = get_dataframe(ticker, start_date, end_date)
        if df.empty:
            st.error("No data found for the selected date range.")
        else:
            fig = plot_candlestick(df, ticker)
            show_plot(fig)
            show_info(ticker)
            st.write("") 
            show_news(ticker)
            st.write("") 
            show_portfolio()
