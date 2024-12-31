import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Title and Ticker Input
st.title("Historical Stock Price and Forward Projections")

st.markdown(
    "This dashboard displays the stock price on a logarithmic scale along with a trendline and a projection of the future stock price over the next 10 years. The projection is calculated using the historical trendline to model future price growth. Hover over the chart to view the stock price in actual dollars."
)

ticker = st.text_input("Enter Stock Ticker", value="AMZN", max_chars=5)

if ticker:
    try:
        # Fetch stock price data
        start_date = (datetime.now() - timedelta(days=20 * 365)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        history = yf.download(ticker, start=start_date, end=end_date)

        if history.empty:
            st.error("No stock price data available for the given ticker. Try a different one.")
        else:
            # Flatten MultiIndex columns (if present)
            if isinstance(history.columns, pd.MultiIndex):
                history.columns = history.columns.get_level_values(0)

            # Ensure 'Close' is numeric and drop missing values
            history = history.reset_index()
            history["Close"] = pd.to_numeric(history["Close"], errors="coerce")
            history = history.dropna(subset=["Close"])

            # Calculate logarithmic stock price for trendline
            x = np.arange(len(history))  # Use index as independent variable
            y = np.log(history["Close"])  # Log of stock prices

            # Fit a trendline
            coef = np.polyfit(x, y, 1)  # Linear fit
            trendline = coef[0] * x + coef[1]

            # Use historical trendline to project future values (10 years)
            future_x = np.arange(len(history), len(history) + 3650)  # 10 years (approx.)
            future_trendline = coef[0] * future_x + coef[1]
            projected_dates = pd.date_range(start=history["Date"].iloc[-1], periods=3650, freq="D")
            projected_prices = np.exp(future_trendline)  # Convert back to dollar scale

            # Calculate forward CAGR
            initial_price = float(history["Close"].iloc[-1])  # Ensure numeric value
            final_price = float(projected_prices[-1])  # Ensure numeric value
            years = 10
            cagr = ((final_price / initial_price) ** (1 / years) - 1) * 100

            # Callout for forward CAGR
            st.markdown(
                f"<div style='border: 1px solid #d3d3d3; padding: 10px; background-color: #f9f9f9; font-size: 1.2em; text-align: center;'>"
                f"Forward CAGR Projection: <b>{cagr:.2f}% per year</b>"
                f"</div>",
                unsafe_allow_html=True
            )

            # Plotting stock price and projections using Plotly
            st.write("### Stock Price Over Time with Historical Trendline-Based Projections")

            fig = go.Figure()

            # Plot actual stock price
            fig.add_trace(go.Scatter(
                x=history["Date"],
                y=history["Close"],
                mode="lines",
                name="Stock Price",
                line=dict(color="blue")
            ))

            # Plot historical trendline
            fig.add_trace(go.Scatter(
                x=history["Date"],
                y=np.exp(trendline),
                mode="lines",
                name="Trendline",
                line=dict(color="orange", dash="dash")
            ))

            # Plot projected values based on historical trendline
            fig.add_trace(go.Scatter(
                x=projected_dates,
                y=projected_prices,
                mode="lines",
                name="Projection (10 years)",
                line=dict(color="green", dash="dash")
            ))

            # Update layout for interactivity and display
            fig.update_layout(
                title=f"{ticker} - Stock Price, Historical Trendline, and 10-Year Projection",
                xaxis_title="Date",
                yaxis_title="Stock Price (Log Scale)",
                hovermode="x unified",
                yaxis=dict(type="log"),
                xaxis=dict(type="date")
            )

            st.plotly_chart(fig)

            # Historical and projected annual prices
            st.write("### Historical and Projected Annual Prices")
            annual_prices = {
                "Year": list(history["Date"].dt.year.unique()) + list(range(history["Date"].dt.year.max() + 1, history["Date"].dt.year.max() + 11)),
                "Price": list(history.groupby(history["Date"].dt.year)["Close"].mean()) + [projected_prices[i * 365] for i in range(10)]
            }
            annual_prices_df = pd.DataFrame(annual_prices)

            bar_fig = px.bar(annual_prices_df, x="Year", y="Price", title="Annual Historical and Projected Prices", labels={"Price": "Stock Price ($)", "Year": "Year"})
            st.plotly_chart(bar_fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")
