from django.urls import path
from . import views


urlpatterns = [
    path('fetch-data/<str:symbol>/', views.fetch_stock_data_view, name='fetch_data'),
    path('backtest/', views.backtest_strategy, name='backtest_strategy'),
    path('predict/<str:symbol>/', views.predict_future_prices, name='predict_future_prices'),
    path('plot/<str:symbol>/', views.stock_price_plot_view, name='stock_price_plot'),
    path('report/<str:symbol>/', views.generate_report_view, name='generate_report'),
]