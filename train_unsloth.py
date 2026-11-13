#!/usr/bin/env python3
"""
Fine-tune k2-horizon model for hardware knowledge using Unsloth
"""

import os
import json
from pathlib import Path

MODEL_PATH = "/Users/suryaprakashk/.docker/models/bundles/sha256/bb2bef99eba2985e74ad3c15793af104ef6980bda94c188b3c314880e645020f/model"
DATASET_PATH = "/Users/suryaprakashk/k2-hardware-training/data/hardware_knowledge_base.jsonl"
OUTPUT_DIR = "/Users/suryaprakashk/k2-hardware-training/models/hardware-unsloth"

def load_dataset():
    """Load the hardware knowledge dataset"""
    data = []
    with open(DATASET_PATH, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def main():
    print("=== k2-horizon Hardware Unsloth Training ===")
    print("")

    try:
        from unsloth import FastLanguageModel
        import torch
        from datasets import Dataset
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install Unsloth:")
        print("  pip install unsloth")
        return

    print(f"Model path: {MODEL_PATH}")
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")

    if not Path(MODEL_PATH).exists():
        print(f"Model not found at {MODEL_PATH}")
        return

    if not Path(DATASET_PATH).exists():
        print(f"Dataset not found at {DATASET_PATH}")
        return

    print("Loading dataset...")
    dataset = load_dataset()
    print(f"Dataset loaded with {len(dataset)} examples")

    print("Loading model with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_PATH,
        max_seq_length=512,
        dtype=None,
        load_in_4bit=True,
    )

    print("Model loaded successfully")

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    print("LoRA adapters added")
    print("")
    print("Ready for training!")
    print("To train, uncomment the training section in this script")
    print("Or prepare your dataset and run this script")

if __name__ == "__main__":
    main()
