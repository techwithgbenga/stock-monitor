# Real-Time Stock Price Monitor & Alert System

This project monitors specified stocks in real-time, logging their prices and sending alert emails if significant changes occur. It also generates plots for visual analysis of historical prices.

## Features

- **Live Stock Data Retrieval:** Uses the `yfinance` library.
- **Data Logging:** Saves timestamped stock prices to a CSV file.
- **Percentage Change Alerts:** Configurable thresholds trigger email alerts.
- **Visualization:** Generates and saves stock history plots using `matplotlib`.
- **Scheduling:** Checks stock prices at regular intervals with `schedule`.

## Setup

1. Clone the repository.
2. Install dependencies:

```bash
   pip install -r requirements.txt
 ```
3. Edit config.json:
- Add the stock symbols you wish to monitor.
- Set your desired alert threshold percentage.
- Provide your email configuration for alerts.

```bash
   python stock_monitor.py
 ```
## Future Improvements
- User Interface: A web dashboard to display live charts.
- Advanced Analytics: Incorporate more technical indicators.
- Notifications: Add support for SMS or push notifications.
- Pull requests and suggestions are welcome!

  
---

## Summary

This complete project is designed to be self-contained and is ideal for GitHub as an open-source resource. It not only retrieves and logs real-time stock data but also provides alerts and visualization, making it useful for anyone interested in financial monitoring.

Feel free to expand on this base project by adding new features like web-based dashboards or integrating additional data sources. Would you like to add any extra functionalities (such as SMS notifications, advanced analytics, or a dashboard) to the project?
