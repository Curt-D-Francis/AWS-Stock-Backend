import numpy as np
from sklearn.linear_model import LinearRegression

def predict_stock_prices(closing_prices):
    # Generate training data (e.g., days since start)
    X_train = np.arange(len(closing_prices)).reshape(-1, 1)
    y_train = np.array(closing_prices).reshape(-1, 1)

    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict prices for the next 30 days
    future_days = np.arange(len(closing_prices), len(closing_prices) + 30).reshape(-1, 1)
    predicted_prices = model.predict(future_days)

    return predicted_prices.flatten()  # Return the predictions as a flat list