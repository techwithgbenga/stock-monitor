import yfinance as yf
import smtplib
import ssl
import json
import logging
import csv
import os
import schedule
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt

# Load configuration
with open("config.json") as f:
    config = json.load(f)

STOCKS = config["stocks"]             # list of stock symbols (e.g., ["AAPL", "GOOGL"])
ALERT_THRESHOLD = config["threshold"]   # percentage change for triggering alerts
EMAIL_CONFIG = config["email"]
CSV_FILE = config.get("csv_file", "stock_prices.csv")
PLOT_FOLDER = config.get("plot_folder", "plots")

# Logging setup
logging.basicConfig(filename="stock_monitor.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def send_email_alert(subject, body):
    """Send an email alert using SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_CONFIG["sender"]
        msg["To"] = EMAIL_CONFIG["receiver"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["port"], context=context) as server:
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
        logging.info("Alert email sent.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def log_stock_data(timestamp, symbol, price):
    """Append the latest stock price to a CSV file."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Symbol", "Price"])
        writer.writerow([timestamp, symbol, price])

def plot_stock(symbol):
    """Plot stock price history from the CSV file and save the figure."""
    timestamps = []
    prices = []
    try:
        with open(CSV_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Symbol"] == symbol:
                    timestamps.append(datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S"))
                    prices.append(float(row["Price"]))
        if timestamps and prices:
            plt.figure(figsize=(10, 5))
            plt.plot(timestamps, prices, marker="o", linestyle="-")
            plt.title(f"{symbol} Price History")
            plt.xlabel("Time")
            plt.ylabel("Price")
            plt.grid(True)
            os.makedirs(PLOT_FOLDER, exist_ok=True)
            plot_file = os.path.join(PLOT_FOLDER, f"{symbol}_history.png")
            plt.savefig(plot_file)
            plt.close()
            logging.info(f"Plot saved for {symbol} at {plot_file}")
    except Exception as e:
        logging.error(f"Error plotting stock {symbol}: {e}")

def check_stock(symbol):
    """Check current stock price and compare it against thresholds."""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="1m")
        if data.empty:
            logging.warning(f"No data received for {symbol}")
            return

        current_price = data["Close"].iloc[-1]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_stock_data(timestamp, symbol, current_price)
        logging.info(f"{symbol}: ${current_price:.2f} at {timestamp}")

        # Retrieve previous record for threshold comparison (if any)
        previous_price = None
        with open(CSV_FILE, mode='r') as file:
            reader = list(csv.DictReader(file))
            # find the last entry for the symbol before the current timestamp if available
            for row in reversed(reader):
                if row["Symbol"] == symbol:
                    previous_price = float(row["Price"])
                    break

        if previous_price is not None:
            percent_change = ((current_price - previous_price) / previous_price) * 100.0
            logging.info(f"{symbol} changed by {percent_change:.2f}% from last recorded price")
            if abs(percent_change) >= ALERT_THRESHOLD:
                send_email_alert(
                    subject=f"Stock Alert: {symbol}",
                    body=f"{symbol} price changed by {percent_change:.2f}%.\nCurrent Price: ${current_price:.2f}"
                )
        # Update the plot for this stock.
        plot_stock(symbol)
    except Exception as e:
        logging.error(f"Error checking stock {symbol}: {e}")

def monitor_stocks():
    """Iterate over all tracked stocks and check their prices."""
    logging.info("Starting new stock check cycle...")
    for symbol in STOCKS:
        check_stock(symbol)

# Schedule the monitoring every minute (adjustable per config or need)
schedule.every(1).minutes.do(monitor_stocks)

if __name__ == "__main__":
    logging.info("Starting Real-Time Stock Price Monitor...")
    monitor_stocks()  # Run immediately once at start
    while True:
        schedule.run_pending()
        time.sleep(1)
