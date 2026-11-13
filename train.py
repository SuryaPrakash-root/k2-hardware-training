#!/usr/bin/env python3
"""
Fine-tune k2-horizon model for hardware knowledge
"""

import os
import json
from pathlib import Path

MODEL_PATH = "/Users/suryaprakashk/.docker/models/bundles/sha256/bb2bef99eba2985e74ad3c15793af104ef6980bda94c188b3c314880e645020f/model"
DATASET_PATH = "/Users/suryaprakashk/k2-hardware-training/data/hardware_knowledge_base.jsonl"

def load_dataset():
    """Load the hardware knowledge dataset"""
    data = []
    with open(DATASET_PATH, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def main():
    print("=== k2-horizon Hardware Training ===")
    print("")

    try:
        from mlx_lm import load, generate
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install dependencies: pip install mlx mlx-lm datasets")
        return

    print(f"Model path: {MODEL_PATH}")
    print(f"Dataset path: {DATASET_PATH}")

    if not Path(MODEL_PATH).exists():
        print(f"Model not found at {MODEL_PATH}")
        return

    if not Path(DATASET_PATH).exists():
        print(f"Dataset not found at {DATASET_PATH}")
        return

    print("Loading dataset...")
    dataset = load_dataset()
    print(f"Dataset loaded with {len(dataset)} examples")

    print("Loading model...")
    model, tokenizer = load(MODEL_PATH)
    print("Model loaded successfully")

    print("")
    print("Training configuration:")
    print("  Model: k2-horizon-0.9b")
    print("  Dataset: Hardware knowledge base")
    print("  Method: LoRA fine-tuning")
    print("  Hardware: Apple Silicon (Metal)")
    print("")
    print("To start training, run:")
    print("  python ~/k2-hardware-training/train_lora.py")
    print("")
    print("Or use the Unsloth optimized version:")
    print("  python ~/k2-hardware-training/train_unsloth.py")

if __name__ == "__main__":
    main()
