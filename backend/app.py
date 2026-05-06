import os
import sys
import traceback
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request, jsonify  # noqa: E402
from flask_cors import CORS  # noqa: E402

from smartfinance.config import get_config  # noqa: E402
from smartfinance.db import init_db, save_transactions, fetch_transactions  # noqa: E402
from smartfinance.etl.pipeline import run_pipeline  # noqa: E402
from smartfinance.ml.predict import predict_overspend  # noqa: E402
from smartfinance.ml.model import train_overspend_model  # noqa: E402
from smartfinance.utils.masking import mask_transactions  # noqa: E402

from plaid.model.link_token_create_request import LinkTokenCreateRequest  # noqa: E402
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser  # noqa: E402
from plaid.model.products import Products  # noqa: E402
from plaid.model.country_code import CountryCode  # noqa: E402
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest  # noqa: E402
from plaid.model.transactions_get_request import TransactionsGetRequest  # noqa: E402
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions  # noqa: E402

from backend.plaid_config import plaid_client  # noqa: E402


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config or get_config())
    CORS(app)

    init_db(app.config["DATABASE_URL"])

    state = {"access_token": None}

    @app.route("/")
    def home():
        return jsonify({"status": "ok", "service": "SmartFinance API"})

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    @app.route("/create_link_token", methods=["POST"])
    def create_link_token():
        try:
            body = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id="user-001"),
                client_name="SmartFinance",
                products=[Products("transactions")],
                country_codes=[CountryCode("US")],
                language="en",
            )
            response = plaid_client.link_token_create(body)
            return jsonify(response.to_dict())
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    @app.route("/exchange_public_token", methods=["POST"])
    def exchange_public_token():
        try:
            public_token = request.json.get("public_token")
            req = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = plaid_client.item_public_token_exchange(req)
            state["access_token"] = response["access_token"]
            return jsonify({
                "access_token": response["access_token"],
                "item_id": response["item_id"],
            })
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    @app.route("/get_transactions", methods=["GET"])
    def get_transactions():
        try:
            if not state["access_token"]:
                return jsonify({"error": "no access token; call /exchange_public_token first"}), 400

            end = date.today()
            start = end - timedelta(days=30)
            req = TransactionsGetRequest(
                access_token=state["access_token"],
                start_date=start,
                end_date=end,
                options=TransactionsGetRequestOptions(count=100, offset=0),
            )
            response = plaid_client.transactions_get(req)
            payload = response.to_dict()
            txns = payload.get("transactions", [])
            save_transactions(txns)
            if app.config.get("MASK_PII", True):
                txns = mask_transactions(txns)
            return jsonify({"transactions": txns, "count": len(txns)})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    @app.route("/transactions", methods=["GET"])
    def list_stored_transactions():
        try:
            limit = int(request.args.get("limit", 100))
            txns = fetch_transactions(limit=limit)
            return jsonify({"transactions": txns, "count": len(txns)})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    @app.route("/etl/run", methods=["POST"])
    def etl_run():
        try:
            default_source = "data/sample_transactions.csv"
            source = request.json.get("source", default_source) if request.is_json else default_source
            summary = run_pipeline(source)
            return jsonify(summary)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    @app.route("/ml/train", methods=["POST"])
    def ml_train():
        try:
            metrics = train_overspend_model()
            return jsonify(metrics)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    @app.route("/ml/predict", methods=["POST"])
    def ml_predict():
        try:
            features = request.json or {}
            result = predict_overspend(features)
            return jsonify(result)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e)}), 400

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "1") == "1")
