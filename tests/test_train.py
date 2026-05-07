import os
import json
import numpy as np
import pandas as pd
from src.train import train

FEATURE_NAMES = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide", "density",
    "pH", "sulphates", "alcohol", "wine_type",
]


def _make_temp_data(tmp_path):
    """
    Tạo dataset nhỏ với cùng schema Wine Quality để sử dụng trong test.
    pytest cung cấp `tmp_path` là một thư mục tạm thời, tự động được xóa sau khi test kết thúc.
    """
    rng = np.random.default_rng(0)
    n = 200

    # Tạo mảng X ngẫu nhiên và y là nhãn
    X = rng.random((n, len(FEATURE_NAMES)))
    y = rng.integers(0, 3, size=n)

    # Tạo DataFrame
    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["target"] = y

    # Lưu vào file tạm
    train_path = tmp_path / "train.csv"
    eval_path = tmp_path / "eval.csv"
    df.iloc[:160].to_csv(train_path, index=False)
    df.iloc[160:].to_csv(eval_path, index=False)

    return str(train_path), str(eval_path)


def test_train_returns_float(tmp_path):
    """Kiểm tra hàm train() trả về một số thực trong khoảng [0, 1]."""
    train_path, eval_path = _make_temp_data(tmp_path)

    # Gọi hàm train và kiểm tra kết quả
    result = train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path
    )

    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_metrics_file_created(tmp_path):
    """Kiểm tra file outputs/metrics.json được tạo sau khi huấn luyện."""
    train_path, eval_path = _make_temp_data(tmp_path)

    train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )

    # Kiểm tra file metrics
    assert os.path.exists("outputs/metrics.json")
    with open("outputs/metrics.json", "r") as f:
        metrics = json.load(f)
    assert "accuracy" in metrics
    assert "f1_score" in metrics


def test_model_file_created(tmp_path):
    """Kiểm tra file models/model.pkl được tạo sau khi huấn luyện."""
    train_path, eval_path = _make_temp_data(tmp_path)

    train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )

    # Kiểm tra file model
    assert os.path.exists("models/model.pkl")