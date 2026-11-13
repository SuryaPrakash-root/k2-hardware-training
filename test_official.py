#!/usr/bin/env python3
"""
Test the k2-horizon model with proper generation settings
"""

import sys
from pathlib import Path

MODEL_PATH = "/Users/suryaprakashk/.docker/models/bundles/sha256/bb2bef99eba2985e74ad3c15793af104ef6980bda94c188b3c314880e645020f/model"

# Add model directory to path for custom model imports
sys.path.insert(0, MODEL_PATH)

def main():
    print("=== k2-horizon Model Test (Official) ===")
    print("")

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install dependencies: pip install transformers torch")
        return

    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        device_map="auto",
    )

    print("Model loaded successfully")
    print("")

    test_prompts = [
        "Explain the main types of network switches.",
        "What are RAID configurations for servers?",
        "What is the difference between SAS and SATA?",
    ]

    print("Testing model with proper generation settings...")
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        
        # Use chat template format
        messages = [{"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(
            messages, 
            tokenize=True, 
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        )
        
        # Generate with recommended settings
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.6,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
        
        # Decode only the new tokens
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        print(f"Response: {response}")

    print("")
    print("Test complete")

if __name__ == "__main__":
    main()
