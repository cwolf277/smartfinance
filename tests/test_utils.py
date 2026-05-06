from smartfinance.utils.masking import mask_account_id, mask_transactions


def test_mask_account_id():
    assert mask_account_id("1234567890") == "******7890"
    assert mask_account_id("12") == "**"
    assert mask_account_id(None) == ""


def test_mask_transactions_strips_address():
    txns = [{
        "account_id": "abcdef1234567890",
        "name": "Coffee",
        "location": {"address": "123 Main", "lat": 40.0, "lon": -74.0, "city": "NYC"},
        "account_owner": "John Doe",
    }]
    out = mask_transactions(txns)
    assert out[0]["account_id"].endswith("7890")
    assert out[0]["account_id"].startswith("*")
    assert "address" not in out[0]["location"]
    assert "lat" not in out[0]["location"]
    assert out[0]["location"]["city"] == "NYC"
    assert out[0]["account_owner"] is None
