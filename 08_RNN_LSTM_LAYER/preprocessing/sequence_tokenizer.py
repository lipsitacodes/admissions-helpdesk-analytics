"""Phase 9: Sequence Tokenizer for Conversational Turns.

Prepares turn sequences into tensor batches for RNN/LSTM models.
"""

import re
from typing import Dict, List, Tuple
import torch


class DialogueSequenceTokenizer:
    """Tokenizes conversational turn strings into sequence tensors."""

    def __init__(self, vocab_size: int = 1000, max_seq_len: int = 20):
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.vocab = {"<PAD>": 0, "<UNK>": 1, "<EOS>": 2}
        self.inv_vocab = {0: "<PAD>", 1: "<UNK>", 2: "<EOS>"}

    def fit(self, texts: List[str]):
        for text in texts:
            words = re.findall(r"\b\w+\b", text.lower())
            for w in words:
                if w not in self.vocab and len(self.vocab) < self.vocab_size:
                    idx = len(self.vocab)
                    self.vocab[w] = idx
                    self.inv_vocab[idx] = w

    def encode(self, text: str) -> torch.Tensor:
        words = re.findall(r"\b\w+\b", text.lower())
        indices = [self.vocab.get(w, 1) for w in words][: self.max_seq_len]
        # Pad
        if len(indices) < self.max_seq_len:
            indices += [0] * (self.max_seq_len - len(indices))
        return torch.tensor(indices, dtype=torch.long)
