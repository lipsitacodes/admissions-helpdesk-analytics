"""Phase 5: ANN Training Pipeline.

Trains PyTorch Multi-Label ANN with BCEWithLogitsLoss on CUTM-derived query dataset.
Saves weights, vectorizer, and label schema.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

from ..dataset.dataset_builder import build_ann_dataset, TARGET_INTENTS
from ..preprocessing.vectorizer import create_vectorizer, save_vectorizer
from ..model.ann_model import MultiLabelANN

logger = logging.getLogger("Phase5_ANNTrainer")
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"


def train_ann_intent_model(epochs: int = 15, batch_size: int = 64, lr: float = 0.003) -> MultiLabelANN:
    """Train the multi-label ANN model."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Dataset
    dataset_file = BASE_DIR / "dataset" / "ann_intent_dataset.json"
    if not dataset_file.exists():
        samples = build_ann_dataset()
    else:
        with open(dataset_file, "r", encoding="utf-8") as f:
            samples = json.load(f)

    texts = [s["text"] for s in samples]
    y = np.array([s["labels"] for s in samples], dtype=np.float32)

    # Train / Test split
    X_train_text, X_val_text, y_train, y_val = train_test_split(
        texts, y, test_size=0.15, random_state=42
    )

    # 2. Vectorize
    vectorizer = create_vectorizer(max_features=2500)
    X_train_vec = vectorizer.fit_transform(X_train_text).toarray()
    X_val_vec = vectorizer.transform(X_val_text).toarray()

    # Save vectorizer
    save_vectorizer(vectorizer, str(MODEL_DIR / "vectorizer.joblib"))

    # 3. Tensors & Loaders
    train_dataset = TensorDataset(
        torch.tensor(X_train_vec, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    val_dataset = TensorDataset(
        torch.tensor(X_val_vec, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.float32),
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 4. Model, Loss, Optimizer
    input_dim = X_train_vec.shape[1]
    output_dim = len(TARGET_INTENTS)
    model = MultiLabelANN(input_dim=input_dim, hidden_dim=128, output_dim=output_dim)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    # 5. Training loop
    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch_x.size(0)

        epoch_loss = total_loss / len(train_dataset)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for vx, vy in val_loader:
                v_logits = model(vx)
                val_loss += criterion(v_logits, vy).item() * vx.size(0)
        val_loss /= len(val_dataset)
        model.train()

        if epoch % 5 == 0 or epoch == epochs:
            logger.info("Epoch %d/%d - Train Loss: %.4f, Val Loss: %.4f", epoch, epochs, epoch_loss, val_loss)

    # Save weights & metadata
    weights_path = MODEL_DIR / "ann_intent_weights.pt"
    torch.save(model.state_dict(), weights_path)

    metadata = {
        "input_dim": input_dim,
        "output_dim": output_dim,
        "classes": TARGET_INTENTS,
    }
    with open(MODEL_DIR / "classes.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Phase 5 ANN Model trained and saved successfully at %s", weights_path)
    return model


if __name__ == "__main__":
    train_ann_intent_model()
