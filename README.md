# loan-api

Loan prediction API (FastAPI + scikit-learn), packaged for production with Docker.

- `model/loan_model_1.0.0.joblib`: default model, baked into the image
- `models/loan_model_1.1.0.joblib`: newer model, mounted at run time with `MODEL_PATH`
- `train.py`: retrains both models: `python train.py .`

Run the stack: `docker compose up -d --build` → API http://localhost:8000/docs, Adminer http://localhost:8080 (server `db`, user `loan`).
