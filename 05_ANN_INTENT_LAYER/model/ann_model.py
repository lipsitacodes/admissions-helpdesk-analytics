"""Phase 5: Artificial Neural Network (ANN) Intent Classifier Model.

PyTorch Multi-Label Dense Neural Network.
Outputs independent Bernoulli probabilities via Sigmoid activation for each intent class:
- fees
- course_information
- faculty
- hostel
- eligibility
- admission
"""

import torch
import torch.nn as nn


class MultiLabelANN(nn.Module):
    """Deep Multi-Layer Perceptron / ANN for multi-label intent detection."""

    def __init__(self, input_dim: int, hidden_dim: int = 128, output_dim: int = 6, dropout_rate: float = 0.2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout_rate)

        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.bn2 = nn.BatchNorm1d(hidden_dim // 2)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout_rate)

        self.out = nn.Linear(hidden_dim // 2, output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute logits."""
        h = self.dropout1(self.relu1(self.bn1(self.fc1(x))))
        h = self.dropout2(self.relu2(self.bn2(self.fc2(h))))
        logits = self.out(h)
        return logits

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Return sigmoid probabilities."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            return torch.sigmoid(logits)
