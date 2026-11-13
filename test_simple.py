#!/usr/bin/env python3
"""
Simple test for k2-horizon model
"""

import sys
from pathlib import Path

MODEL_PATH = "/Users/suryaprakashk/.docker/models/bundles/sha256/bb2bef99eba2985e74ad3c15793af104ef6980bda94c188b3c314880e645020f/model"

# Add model directory to path for custom model imports
sys.path.insert(0, MODEL_PATH)

def main():
    print("=== Simple k2-horizon Model Test ===")
    print("")

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install dependencies: pip install transformers torch")
        return

    print("Loading base model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        dtype=torch.float16,
    )

    print("Model loaded successfully")
    print("")

    test_prompts = [
        "User: What are the main types of network switches?",
        "User: Explain RAID configurations for servers",
        "User: What is the difference between SAS and SATA?",
    ]

    print("Testing model...")
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        inputs = tokenizer(prompt, return_tensors="pt")
        # Keep input_ids as Long, attention_mask as Long
        outputs = model.generate(**inputs, max_new_tokens=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Response: {response}")

    print("")
    print("Test complete")

if __name__ == "__main__":
    main()
