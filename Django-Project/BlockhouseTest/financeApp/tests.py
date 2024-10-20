from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import StockPrice
from datetime import datetime, timedelta

class BacktestStrategyTest(TestCase):
    
    def setUp(self):
        # Create some stock price data for testing
        symbol = 'AAPL'
        self.stock_prices = [
            StockPrice(symbol=symbol, date=timezone.now().date(), open_price=150, high_price=160, low_price=140, close_price=155, volume=1000),
            StockPrice(symbol=symbol, date=timezone.now().date() - timezone.timedelta(days=1), open_price=145, high_price=155, low_price=135, close_price=150, volume=1200),
            StockPrice(symbol=symbol, date=timezone.now().date() - timezone.timedelta(days=2), open_price=140, high_price=150, low_price=130, close_price=145, volume=1100),
        ]
        StockPrice.objects.bulk_create(self.stock_prices)

    def test_backtest_strategy(self):
        # Test the backtest strategy
        url = reverse('backtest_strategy')
        response = self.client.get(url, {'symbol': 'AAPL', 'initial_investment': 1000, 'ma_short': 2, 'ma_long': 3})

        # Assert that the response is OK
        self.assertEqual(response.status_code, 200)

        # Assert that the ROI is in the response
        self.assertIn('roi', response.json())
        self.assertIn('total_trades', response.json())
        self.assertIn('max_drawdown', response.json())
        
        # Check that the response contains valid values
        roi = response.json().get('roi')
        total_trades = response.json().get('total_trades')
        max_drawdown = response.json().get('max_drawdown')
        
        # assertions on the content
        self.assertIsInstance(roi, float)
        self.assertIsInstance(total_trades, int)
        self.assertIsInstance(float(max_drawdown), float)


class PredictStockPricesTestCase(TestCase):
    def setUp(self):
        # Start date for generating stock price data
        start_date = datetime(2024, 1, 1)
        
        # Create mock stock price data for 100 days
        for i in range(100):
            date = start_date + timedelta(days=i)
            StockPrice.objects.create(
                symbol='AAPL',
                date=date.strftime('%Y-%m-%d'),
                open_price=100 + i,
                close_price=100 + i,
                high_price=105 + i,
                low_price=95 + i,
                volume=1000000 + i
            )

    def test_predict_future_prices(self):
        # Simulate a GET request to the predict_future_prices API endpoint
        response = self.client.get(reverse('predict_future_prices', kwargs={'symbol': 'AAPL'}))
        
        # Check the response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains 30 predicted prices
        data = response.json()
        self.assertIn('predictions', data)
        self.assertEqual(len(data['predictions']), 30)