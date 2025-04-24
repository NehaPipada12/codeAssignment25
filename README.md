# Expense Analyzer

An intelligent expense tracking web application built with Flask. It allows users to upload CSV files containing expense data, categorizes expenses using semantic similarity powered by a lightweight SentenceTransformer model, and visualizes the results through interactive charts.

## Features

- CSV Upload: Users can upload CSV files containing expense data.

- Semantic Categorization: Utilizes the all-MiniLM-L6-v2 SentenceTransformer model to categorize expenses based on the semantic similarity of descriptions.

- Interactive Visualizations: Displays expenses through interactive bar and pie charts using Chart.js.

- Top Categories Display: Highlights the top 3 expense categories based on total amounts.

