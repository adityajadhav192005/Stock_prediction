📈 Stock Prediction Web App

This project is a Stock Price Prediction Web Application built using Deep Learning (LSTM) and integrated with a Django backend.
It focuses on learning patterns from historical stock prices and evaluating prediction performance using known past data.

🔍 What the Application Does

Fetches historical stock data using Yahoo Finance

Calculates 100-day and 200-day moving averages

Trains an LSTM-based neural network on time-series price data

Predicts prices on a test portion of historical data

Visualizes actual vs predicted stock prices

⚠️ Disclaimer
This project does not predict future dates (next day/week/month).
Instead, it evaluates model performance by predicting the last portion of historical data, which provides a controlled and measurable evaluation of accuracy.

🛠️ Technologies Used

Python

Django (Backend API)

TensorFlow / Keras

LSTM (Recurrent Neural Network)

yfinance

Pandas, NumPy

Matplotlib

🧠 Why LSTM?

Stock market data is time-series data, where price movements depend on historical trends.
LSTM models are designed to retain long-term dependencies, making them more suitable than traditional regression techniques for modeling stock price behavior.

🔄 Prediction Workflow
1️⃣ Data Collection

Historical stock data (10 years) is downloaded using yfinance.

<p align="center"> <img src="https://i.postimg.cc/MpqQmpm0/Screenshot-2025-07-10-at-12-26-44-AM.png" height="400" width="500"> </p>
2️⃣ Data Visualization

Stock closing prices are plotted to understand overall trends.

<p align="center"> <img src="https://i.postimg.cc/cJ7k5Hps/Screenshot-2025-07-10-at-12-34-21-AM.png" height="400" width="500"> </p>
3️⃣ Feature Engineering

100-day moving average

200-day moving average

Percentage price change

<p align="center"> <img src="https://i.postimg.cc/x8x9K3vh/Screenshot-2025-07-10-at-3-30-13-PM.png" height="400" width="500"> </p> <p align="center"> <img src="https://i.postimg.cc/MGMtx63Q/Screenshot-2025-07-10-at-3-30-30-PM.png" height="400" width="500"> </p>
4️⃣ Data Preprocessing

Prices are scaled between 0 and 1

Scaling improves training stability and convergence for LSTM models

5️⃣ Model Architecture
Input (100 timesteps)
   ↓
LSTM (128 units)
   ↓
LSTM (64 units)
   ↓
Dense (25 neurons)
   ↓
Dense (1 output)

6️⃣ Model Training

Optimizer: Adam

Loss function: Mean Squared Error

Trained for multiple epochs to learn temporal patterns

<p align="center"> <img src="https://i.postimg.cc/28ZDvgwY/Screenshot-2025-07-11-at-12-09-28-PM.png" height="400" width="500"> </p>
7️⃣ Prediction & Evaluation

Predictions are inverse-scaled to original price values

Model performance is evaluated using:

Mean Squared Error (MSE)

Root Mean Squared Error (RMSE)

R² Score

<p align="center"> <img src="https://i.postimg.cc/RZWRRWCJ/Screenshot-2025-07-12-at-12-18-22-AM.png" height="400" width="500"> </p>
📌 Project Objective

This project is built for educational and analytical purposes, demonstrating how deep learning models can be applied to financial time-series data and deployed through a full-stack web application.
