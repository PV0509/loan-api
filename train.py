import sys, numpy as np, joblib, os
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
out = sys.argv[1]
rng = np.random.default_rng(42)
n = 5000
income = rng.normal(1200, 500, n).clip(200, 5000)          # monthly USD
loan = rng.normal(8000, 4000, n).clip(500, 30000)
term = rng.choice([12, 24, 36, 48, 60], n)
credit = rng.normal(650, 70, n).clip(300, 850)
years = rng.integers(0, 30, n)
X = np.column_stack([income, loan, term, credit, years])
pay = loan / term
logit = -4 + 0.012*(credit-600) + 3*(income/pay > 3) + 0.05*years - 0.00005*loan
y = (rng.random(n) < 1/(1+np.exp(-logit))).astype(int)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=0)
for ver, clf in [("1.0.0", LogisticRegression(max_iter=1000)),
                 ("1.1.0", RandomForestClassifier(n_estimators=60, max_depth=8, random_state=0))]:
    p = Pipeline([("scale", StandardScaler()), ("clf", clf)]).fit(Xtr, ytr)
    d = os.path.join(out, "model" if ver == "1.0.0" else "models")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"loan_model_{ver}.joblib")
    joblib.dump(p, f, compress=3)
    print(ver, round(p.score(Xte, yte), 3), os.path.getsize(f))
