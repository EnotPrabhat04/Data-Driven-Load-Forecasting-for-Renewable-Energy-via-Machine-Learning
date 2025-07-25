# Data-Driven-Load-Forecasting-for-Renewable-Energy-via-Machine-Learning
Forecasting solar power using LSTM-based machine learning. Combines IMD GHI data with actual MW output, handles missing data, scales features, and predicts short-term solar load. Built with Python, TensorFlow, and Scikit-learn for smart renewable energy planning.

**Tools & Technologies**

Python (Google Colab)

Pandas, NumPy – data manipulation & preprocessing

Scikit-learn – feature scaling, performance metrics

TensorFlow (Keras) – LSTM model architecture

Matplotlib – visualization

Excel (openpyxl) – data input/output


**Workflow Overview**

**Data Compilation**

Extracted and combined daily station-wise GHI data and corresponding solar MW generation data

Unified timestamps and handled inconsistent station naming using IMD_mapping.xlsx

Ensured a 96-slot time grid for every day (5-min resolution)

**Data Preprocessing**

Handled missing values using lag and 3-day interpolation

Engineered features: Hour, Minute, Lag, and Rolling Average

Applied MinMax Scaling for LSTM readiness

**Model Architecture**

Built an LSTM model with Dropout and Dense layers

Used a sliding time-window approach (TIME_STEPS = 3) to capture temporal dependencies

Trained using 80-20 train-test split and validated using MAE, RMSE, and R² Score

**Model Evaluation & Results**

Visualized actual vs predicted MW output

Achieved promising R² and low MAE, indicating strong model performance

Exported future solar MW predictions into Excel

**Key Insights**
Temporal alignment and preprocessing were critical for accurate forecasting

The model generalizes well on unseen data, proving LSTM’s strength in time-series forecasting

The approach is modular, making it easy to extend to other stations or weather datasets

