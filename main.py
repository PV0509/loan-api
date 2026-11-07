"""Loan prediction API (Module 4)."""
import os
import re
import logging

import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field

log = logging.getLogger("loan-api")

# Model path is configurable: default = model baked into the image
MODEL_PATH = os.getenv("MODEL_PATH", "model/loan_model_1.0.0.joblib")
model = joblib.load(MODEL_PATH)
_m = re.search(r"(\d+\.\d+\.\d+)", os.path.basename(MODEL_PATH))
MODEL_VERSION = os.getenv("MODEL_VERSION", _m.group(1) if _m else "unknown")

# Optional: log predictions to PostgreSQL when DATABASE_URL is set (Compose)
DATABASE_URL = os.getenv("DATABASE_URL")


def save_prediction(data: dict, approved: bool, prob: float) -> None:
    if not DATABASE_URL:
        return
    try:
        import psycopg
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            conn.execute(
                "insert into predictions (income, loan_amount, loan_term, credit_score,"
                " employment_years, approved, probability, model_version)"
                " values (%s,%s,%s,%s,%s,%s,%s,%s)",
                (data["income"], data["loan_amount"], data["loan_term"],
                 data["credit_score"], data["employment_years"],
                 approved, prob, MODEL_VERSION),
            )
    except Exception as e:  # never fail a prediction because of logging
        log.warning("could not save prediction: %s", e)


class LoanApplication(BaseModel):
    income: float = Field(..., gt=0, description="Monthly income (USD)", examples=[1500])
    loan_amount: float = Field(..., gt=0, description="Loan amount (USD)", examples=[6000])
    loan_term: int = Field(..., gt=0, description="Term in months", examples=[36])
    credit_score: float = Field(..., ge=300, le=850, examples=[700])
    employment_years: int = Field(..., ge=0, examples=[5])


app = FastAPI(title="Loan Prediction API", version=MODEL_VERSION)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION, "model_path": MODEL_PATH}


@app.post("/predict")
def predict(app_in: LoanApplication):
    d = app_in.model_dump()
    x = np.array([[d["income"], d["loan_amount"], d["loan_term"],
                   d["credit_score"], d["employment_years"]]])
    prob = float(model.predict_proba(x)[0, 1])
    approved = prob >= 0.5
    save_prediction(d, approved, prob)
    return {"approved": approved, "probability": round(prob, 4), "model_version": MODEL_VERSION}
