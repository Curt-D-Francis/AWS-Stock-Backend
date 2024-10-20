Django-Based Financial Data and Backtesting System
Overview
This Django application fetches financial data from Alpha Vantage, performs backtesting strategies using historical data, and integrates a machine learning model for stock price prediction. The system is fully deployable using Docker and AWS, with CI/CD automation for seamless updates.

Project Setup
Prerequisites
Python 3.12
Docker and Docker Compose
AWS Account (for deployment)
Alpha Vantage API Key
Local Setup Instructions
Clone the repository:

Steps:
git clone https://github.com/https://github.com/Curt-D-Francis/AWS-Stock-Backend/.git
cd your-repository
Install dependencies:

Create a virtual environment and install the necessary Python packages.

Steps:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Set environment variables:

Setup a .env and add your Alpha Vantage API key and other environment variables.

Steps:
Update .env with your API keys and database information:
ALPHA_VANTAGE_API_KEY
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD

Run migrations:
Set up the PostgreSQL database and apply the migrations.
Steps:
python manage.py makemigrations
python manage.py migrate
Start the development server:

Run the Django development server.

Steps:
python manage.py runserver
The app will be available at http://127.0.0.1:8000/.

Running Docker Locally
Build and run with Docker Compose:

Use Docker Compose to build the application and run it with PostgreSQL.

Steps:
docker-compose up --build
The application will be available at http://localhost:8000/.

API Endpoints
Fetch Financial Data
URL: /fetch-data/<symbol>/
Method: GET
Description: Fetch historical financial data for the given stock symbol (e.g., AAPL).
Backtesting Module
URL: /backtest/
Method: POST
Description: Perform backtesting with the following parameters:
Initial investment amount
Buy/Sell conditions based on moving averages
Predict Future Prices
URL: /predict/<symbol>/
Method: GET
Description: Predict future prices for the given stock symbol using the machine learning model.
Generate Report
URL: /report/<symbol>/
Method: GET
Description: Generate a performance report with key metrics and visualizations, available as a PDF and JSON.
Backtesting Strategy
The application allows users to perform basic backtesting based on the following rules:

Buy when the stock price dips below the 50-day moving average.
Sell when the stock price rises above the 200-day moving average.
Backtesting calculates key performance metrics, including:

Total return
Maximum drawdown
Number of trades
Users can input the initial investment and get a report of how the strategy would have performed over the selected time period.

Machine Learning Integration
This project includes a simple integration with a pre-trained machine learning model to predict stock prices.

Pre-trained Model
The machine learning model is a simple linear regression model that is dynamically utilized when the function is called.
It uses historical financial data to predict future prices for the next 30 days.
API Endpoint for Predictions
URL: /predict/<symbol>/
This endpoint predicts the stock prices for the given symbol and stores the predictions alongside the actual historical data for later comparison.

Report Generation
The system generates a performance report after running a backtest or making predictions. The report includes:

Key financial metrics from the backtest.
A visual comparison between predicted and actual stock prices using Matplotlib or Plotly.
Output Formats
PDF Report: Downloadable report including visualizations and metrics.
JSON Response: API returns the report in JSON format.
Deployment to AWS
This project is containerized using Docker and deployed to AWS ECS with PostgreSQL hosted on RDS. The CI/CD pipeline automates deployment using GitHub Actions.

Steps for Deployment
Create an RDS PostgreSQL instance:

Set up an AWS RDS instance and note down the connection details (host, database name, username, password).
Set up AWS ECS:

Create an ECS cluster with a service for the Django app.
Use an Elastic Load Balancer for the service.
Configure environment variables:

Store your database credentials and other secrets in the AWS Parameter Store or Secrets Manager.
Deploy the application using Docker:

Build the Docker image and push it to AWS ECR.
ECS will automatically pull and run the containerized application.
CI/CD with GitHub Actions
This project uses GitHub Actions to automate building, testing, and deploying the Django application.

Steps
Trigger the pipeline:

The pipeline runs when changes are pushed to the main branch.
Build and test the project:

The application is built and tested in a Docker container.
Deploy to AWS ECS:

Upon successful build, the Docker image is pushed to AWS ECR.
The ECS service is updated to use the new image.
