"""Phase 9: Recurrent Neural Network (RNN) for Sequential Context Transition.

Rule 9: RNN -> sequential context.
Processes sequential query representations to classify conversational transition state:
- CONTINUATION (follow-up query referencing active topic)
- NEW_TOPIC (user switched to a new course/discipline)
- CLARIFICATION (user asking for refinement/specifics)
"""

import torch
import torch.nn as nn


class SequentialContextRNN(nn.Module):
    """Standard Elman Recurrent Neural Network for utterance transition classification."""

    def __init__(self, vocab_size: int = 1000, embed_dim: int = 64, hidden_dim: int = 64, num_classes: int = 3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True, nonlinearity="relu")
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor, h_0: torch.Tensor = None) -> torch.Tensor:
        """Process sequence tensor and return transition logits."""
        # x: (batch_size, seq_len)
        embeds = self.embedding(x)
        out, h_n = self.rnn(embeds, h_0)
        # Take last time step
        last_hidden = out[:, -1, :]
        logits = self.fc(last_hidden)
        return logits
