# backend/models/train_price_model.py

import pandas as pd
import numpy as np
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
from catboost import CatBoostRegressor


# PATHS

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "../data/processed/mandi_prices.csv")
MODEL_PATH = os.path.join(BASE_DIR, "agrichain_price_model.cbm")


# STEP 1 — LOAD

print("=" * 50)
print("  AgriChain — CatBoost Price Model Training")
print("=" * 50)

print("\n[1/7] Loading data...")
df = pd.read_csv(DATA_PATH)
print(f"      Loaded: {len(df):,} rows")


# STEP 2 — CLEAN

print("\n[2/7] Cleaning...")

df = df.dropna(subset=[
    "State", "District", "Market", "Commodity",
    "Variety", "Grade", "Arrival_Date", "Modal_Price"
])

df["Modal_Price"] = pd.to_numeric(df["Modal_Price"], errors="coerce")
df["Min_Price"]   = pd.to_numeric(df["Min_Price"],   errors="coerce")
df["Max_Price"]   = pd.to_numeric(df["Max_Price"],   errors="coerce")
df = df.dropna(subset=["Modal_Price"])

# Remove outliers
df = df[df["Modal_Price"] > 0]
df = df[df["Modal_Price"] < 500000]

print(f"      After cleaning: {len(df):,} rows")


# STEP 3 — FEATURE ENGINEERING

print("\n[3/7] Engineering features...")

df["Arrival_Date"] = pd.to_datetime(df["Arrival_Date"], errors="coerce")
df = df.dropna(subset=["Arrival_Date"])

df["year"]  = df["Arrival_Date"].dt.year
df["month"] = df["Arrival_Date"].dt.month
df["week"]  = df["Arrival_Date"].dt.isocalendar().week.astype(int)
df["season"] = df["month"].map({
    12: "winter",       1: "winter",        2: "winter",
    3:  "summer",       4: "summer",        5: "summer",
    6:  "monsoon",      7: "monsoon",       8: "monsoon",
    9:  "monsoon",      10: "post_monsoon", 11: "post_monsoon"
})

# Price spread feature — captures market volatility
df["price_spread"] = df["Max_Price"] - df["Min_Price"]

print(f"      Features created: year, month, week, season, price_spread")


# STEP 4 — DEFINE FEATURES

features = [
    "State",        # categorical
    "District",     # categorical
    "Market",       # categorical
    "Commodity",    # categorical
    "Variety",      # categorical
    "Grade",        # categorical
    "season",       # categorical
    "year",         # numeric
    "month",        # numeric
    "week",         # numeric
    "price_spread"  # numeric
]

# Indices of categorical columns in features list
cat_features = [0, 1, 2, 3, 4, 5, 6]   # State, District, Market, Commodity, Variety, Grade, Season

X = df[features]
y = df["Modal_Price"]

print(f"      Feature set: {features}")
print(f"      Cat features: {[features[i] for i in cat_features]}")


# STEP 5 — TIME BASED SPLIT
# Never random split on time series data

print("\n[4/7] Splitting data (time-based)...")

df_sorted  = df.sort_values("Arrival_Date").reset_index(drop=True)
split_idx  = int(len(df_sorted) * 0.80)

train_df   = df_sorted.iloc[:split_idx]
test_df    = df_sorted.iloc[split_idx:]

X_train, y_train = train_df[features], train_df["Modal_Price"]
X_test,  y_test  = test_df[features],  test_df["Modal_Price"]

train_start = train_df["Arrival_Date"].min().date()
train_end   = train_df["Arrival_Date"].max().date()
test_start  = test_df["Arrival_Date"].min().date()
test_end    = test_df["Arrival_Date"].max().date()

print(f"      Train: {len(X_train):,} rows ({train_start} → {train_end})")
print(f"      Test : {len(X_test):,}  rows ({test_start} → {test_end})")


# STEP 6 — TRAIN

print("\n[5/7] Training CatBoost model...")
print("      This will take ~15-20 minutes...\n")

model = CatBoostRegressor(
    iterations          = 1000,
    learning_rate       = 0.05,
    depth               = 8,
    loss_function       = "MAE",
    eval_metric         = "MAE",
    early_stopping_rounds = 50,
    verbose             = 100
)

model.fit(
    X_train, y_train,
    cat_features = cat_features,
    eval_set     = (X_test, y_test)
)


# STEP 7 — EVALUATE

print("\n[6/7] Evaluating...")

pred = model.predict(X_test)
mae  = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))
mape = np.mean(np.abs((y_test.values - pred) / y_test.values)) * 100

print("\n" + "=" * 40)
print("       MODEL PERFORMANCE")
print("=" * 40)
print(f"  MAE  : ₹{mae:.2f}  per quintal")
print(f"  RMSE : ₹{rmse:.2f} per quintal")
print(f"  MAPE : {mape:.2f}%")
print("=" * 40)

# Interpret MAE for the team
if mae < 200:
    print("  ✅ Excellent — ready for production")
elif mae < 400:
    print("  ✅ Good — solid for hackathon demo")
elif mae < 600:
    print("  ⚠️  Acceptable — demo will work")
else:
    print("  ❌ High error — check data quality")

# Feature importance
print("\n  Top Feature Importances:")
importance = pd.Series(
    model.get_feature_importance(),
    index=features
).sort_values(ascending=False)
for feat, score in importance.items():
    bar = "█" * int(score / 3)
    print(f"  {feat:<15} {score:5.1f}  {bar}")


# STEP 8 — SAVE

print(f"\n[7/7] Saving model...")
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
model.save_model(MODEL_PATH)
print(f"      ✅ Model saved → {MODEL_PATH}")
print("\n  Training complete! Run predict_price.py to test predictions.")
print("=" * 50)