from django.shortcuts import render
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse, HttpResponse, FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import utils
from decouple import config
import requests
import io
from .models import StockPrice
from .models import StockPrediction
import matplotlib.pyplot as plt
import pandas as pd
from .ml_utils import predict_stock_prices

def fetch_stock_data_view(request, symbol):
    fetch_stock_data(symbol)
    return JsonResponse({'status': f'Data for {symbol} fetched successfully!'})

def fetch_stock_data(symbol):
    API_KEY = config("ADVTG_API_KEY")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    try:
        # Make the request to Alpha Vantage API
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError
        
        # Convert the response to JSON format
        data = response.json()
        
        # Check if 'Time Series (Daily)' exists in the response
        if 'Time Series (Daily)' in data:
            for date, daily_data in data['Time Series (Daily)'].items():
                # Check if a record already exists for this symbol and date
                stock_price, created = StockPrice.objects.update_or_create(
                    symbol=symbol,
                    date=date,
                    defaults={
                        'open_price': daily_data.get('1. open'),
                        'high_price': daily_data.get('2. high'),
                        'low_price': daily_data.get('3. low'),
                        'close_price': daily_data.get('4. close'),
                        'volume': daily_data.get('5. volume')
                    }
                )
                if created:
                    print(f"New record created for {symbol} on {date}")
                else:
                    print(f"Record updated for {symbol} on {date}")
        else:
            # Handle the case where the time series data is not present
            print(f"Error fetching data for {symbol}: 'Time Series (Daily)' not found in the response.")
    
    except requests.exceptions.RequestException as e:
        # Handle exceptions related to the request itself
        print(f"Error fetching data from Alpha Vantage: {e}")
        
#===================================================================================================================================================================#

# Backtesting Implementation
def backtest_strategy(request=None, symbol='AAPL', initial_investment=1000, ma_short=50, ma_long=200):
    # If called via an HTTP request, get parameters from the request
    if request:
        symbol = request.GET.get('symbol', 'AAPL')
        initial_investment = float(request.GET.get('initial_investment', 1000))
        ma_short = int(request.GET.get('ma_short', 50))
        ma_long = int(request.GET.get('ma_long', 200))

    # Fetch historical stock data from the database
    stock_prices = StockPrice.objects.filter(symbol=symbol).order_by('date')

    # Convert to a DataFrame for easier manipulation
    data = pd.DataFrame(list(stock_prices.values('date', 'close_price')))
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    data['close_price'] = data['close_price'].astype(float)

    # Calculate the moving averages
    data['ma_short'] = data['close_price'].rolling(window=ma_short).mean()
    data['ma_long'] = data['close_price'].rolling(window=ma_long).mean()

    # Initialize variables for tracking the backtest
    cash = initial_investment
    holdings = 0
    total_trades = 0
    max_drawdown = 0
    peak_portfolio_value = initial_investment
    portfolio_values = []
    
    # Loop through the data and apply the buy/sell strategy
    for index, row in data.iterrows():
        portfolio_value = cash + holdings * row['close_price']
        portfolio_values.append(portfolio_value)

        # Track peak portfolio value for max drawdown calculation
        peak_portfolio_value = max(peak_portfolio_value, portfolio_value)
        drawdown = (peak_portfolio_value - portfolio_value) / peak_portfolio_value
        max_drawdown = max(max_drawdown, drawdown)

        # Buy if the price dips below the 50-day moving average
        if row['close_price'] < row['ma_short'] and cash > 0:
            holdings = cash / row['close_price']
            cash = 0
            total_trades += 1

        # Sell if the price rises above the 200-day moving average
        elif row['close_price'] > row['ma_long'] and holdings > 0:
            cash = holdings * row['close_price']
            holdings = 0
            total_trades += 1

    # Final portfolio value after the last trade
    final_portfolio_value = cash + holdings * data.iloc[-1]['close_price']

    # Calculate the return on investment (ROI)
    roi = (final_portfolio_value - initial_investment) / initial_investment * 100

    # Compile backtest results
    backtest_results = {
        'initial_investment': initial_investment,
        'final_portfolio_value': final_portfolio_value,
        'roi': roi,
        'total_trades': total_trades,
        'max_drawdown': max_drawdown,
    }

    # If called via an HTTP request, return a JsonResponse
    if request:
        return JsonResponse(backtest_results)

    # Otherwise, return the results as a dictionary
    return backtest_results

    
#====================================================================================================================================================================

def predict_future_prices(request, symbol):
    # Fetch historical stock data from the database
    stock_prices = StockPrice.objects.filter(symbol=symbol).order_by('date')
    
    # Check if we have any historical data for the symbol
    if not stock_prices.exists():
        return JsonResponse({'error': f'No historical data found for symbol: {symbol}'}, status=404)

    # Extract the closing prices from the data
    closing_prices = list(stock_prices.values_list('close_price', flat=True))
    
    # Predict the next 30 days' prices using the predict_stock_prices function
    predicted_prices = predict_stock_prices(closing_prices)

    # Store predictions in the database and prepare the response
    predictions = []
    for i, price in enumerate(predicted_prices):
        prediction_date = now().date() + timedelta(days=i + 1)
        predictions.append({'day': i + 1, 'predicted_price': price})

        # Save the predictions in the database
        prediction, created = StockPrediction.objects.update_or_create(
            symbol=symbol,
            prediction_date=prediction_date,
            defaults={'predicted_price': price}
        )

    # Return predictions as JSON response
    return JsonResponse({'symbol': symbol, 'predictions': predictions})

#===================================================================================================================================================================#

def plot_stock_price(symbol, backtest_data=None):
    # Fetch the stock data for the symbol
    stock_prices = StockPrice.objects.filter(symbol=symbol).order_by('date')
    
    if not stock_prices.exists():
        return None
    
    # Convert the data into a DataFrame
    data = pd.DataFrame(list(stock_prices.values('date', 'close_price')))
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['close_price'], label=f"{symbol} Closing Prices")
    plt.title(f"{symbol} Stock Price Trend")
    plt.xlabel('Date')
    plt.ylabel('Closing Price')

    # Plot buy and sell signals from the backtest data
    if backtest_data:
        buy_signals = backtest_data.get('buy_signals', [])
        sell_signals = backtest_data.get('sell_signals', [])
        
        for buy_date, buy_price in buy_signals:
            plt.plot(buy_date, buy_price, 'go', label='Buy')  # 'go' = green circles for buys
        for sell_date, sell_price in sell_signals:
            plt.plot(sell_date, sell_price, 'ro', label='Sell')  # 'ro' = red circles for sells

    plt.legend()

    # Save plot to a BytesIO object and return as HTTP response
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    return buffer


def stock_price_plot_view(request, symbol):
    # Get the backtest data using the modified backtest_strategy function
    backtest_results = backtest_strategy(symbol=symbol)
    buffer = plot_stock_price(symbol, backtest_results)
    
    if buffer is None:
        return HttpResponse(f"No data found for symbol {symbol}", content_type='text/plain')
    
    return HttpResponse(buffer, content_type='image/png')


#=====================================================================================================================================================================#

def generate_pdf_report(symbol, backtest_results, predictions):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Write the title and backtest results
    p.drawString(100, 750, f"{symbol} Stock Backtest Report")
    p.drawString(100, 730, f"Final Portfolio Value: ${backtest_results['final_portfolio_value']:.2f}")
    p.drawString(100, 710, f"ROI: {backtest_results['roi']:.2f}%")
    p.drawString(100, 690, f"Total Trades: {backtest_results['total_trades']}")
    p.drawString(100, 670, f"Max Drawdown: {backtest_results['max_drawdown']:.2f}")

    # Display the predictions in the report
    p.drawString(100, 640, "Predicted Stock Prices (Next 30 Days):")
    y_position = 620
    for prediction in predictions:
        p.drawString(100, y_position, f"Day {prediction['day']}: ${prediction['predicted_price']:.2f}")
        y_position -= 15  # Move down for the next prediction

    # Ensure there's enough space for the plot
    if y_position < 150:
        p.showPage()  # Start a new page if there's not enough space

    # Generate the stock price plot and save it to a buffer
    plot_buffer = plot_stock_price(symbol, backtest_results)
    
    if plot_buffer:
        # Move the plot buffer to the beginning
        plot_buffer.seek(0)

        # Convert the BytesIO object to a readable image for ReportLab
        image = utils.ImageReader(plot_buffer)

        # Add the plot image to the PDF
        p.drawImage(image, inch, 2 * inch, width=6 * inch, height=3 * inch)

    # Finalize and save the PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

def generate_report_view(request, symbol):
    # Get the backtest results
    backtest_results = backtest_strategy(symbol=symbol)

    # Get the predictions
    predictions = StockPrediction.objects.filter(symbol=symbol).order_by('prediction_date')
    predictions = [{'day': i + 1, 'predicted_price': pred.predicted_price} for i, pred in enumerate(predictions)]

    # Check if the user wants a JSON response
    report_format = request.GET.get('format', 'pdf')

    if report_format == 'json':
        # Return the backtest results and predictions as a JSON response
        return JsonResponse({
            'symbol': symbol,
            'backtest_results': backtest_results,
            'predictions': predictions
        })

    # Otherwise, return the PDF report
    pdf_buffer = generate_pdf_report(symbol, backtest_results, predictions)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f'{symbol}_backtest_report.pdf')