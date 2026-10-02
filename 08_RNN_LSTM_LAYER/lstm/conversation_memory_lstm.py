"""Phase 9: Long Short-Term Memory (LSTM) for Persistent Conversation Memory.

Rule 9: LSTM -> longer conversation memory.
Tracks conversational slots across multiple turns:
- active_course
- active_campus
- active_intents
Enables resolution of elliptical follow-ups like 'Aur hostel?' -> 'BSc Agriculture hostel information'.
"""

from typing import Any, Dict, List, Optional
import torch
import torch.nn as nn


class ConversationMemoryLSTM(nn.Module):
    """LSTM module to maintain multi-turn context vectors and track slot persistence."""

    def __init__(self, vocab_size: int = 1000, embed_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        # Projection to course slot retention score
        self.course_retention_head = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor, state: Optional[tuple] = None):
        """Forward pass through LSTM cells."""
        embeds = self.embedding(x)
        out, (h_n, c_n) = self.lstm(embeds, state)
        last_out = out[:, -1, :]
        retention_score = torch.sigmoid(self.course_retention_head(last_out))
        return retention_score, (h_n, c_n)
