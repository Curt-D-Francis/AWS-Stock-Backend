from django.db import models

class StockPrice(models.Model):
    symbol = models.CharField(max_length=10, db_index=True)
    date = models.DateField(db_index=True)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ('symbol', 'date') # Ensure each stock has only one entry per date
        ordering = ['-date']   # Default ordering by date in descending order
        db_table = 'stock_price'  # Custom table name
        verbose_name = 'Stock Price'  # Human-readable name
    def __str__(self):
        return f"{self.symbol} - {self.date}"
    
    
#ML Prediction
class StockPrediction(models.Model):
    symbol = models.CharField(max_length=10)
    prediction_date = models.DateField()
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.symbol} - {self.prediction_date} - Predicted: {self.predicted_price}"