#!/usr/bin/env python3
"""
Test the hardware-trained k2-horizon model
"""

import os
import sys
from pathlib import Path

MODEL_PATH = "/Users/suryaprakashk/.docker/models/bundles/sha256/bb2bef99eba2985e74ad3c15793af104ef6980bda94c188b3c314880e645020f/model"
FINETUNED_PATH = "/Users/suryaprakashk/k2-hardware-training/models/hardware-lora/checkpoint-99"

# Add model directory to path for custom model imports
sys.path.insert(0, MODEL_PATH)

def main():
    print("=== Testing Hardware-Trained k2-horizon Model ===")
    print("")

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        from peft import PeftModel
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install dependencies: pip install transformers torch peft")
        return

    finetuned_dir = Path(FINETUNED_PATH)
    if finetuned_dir.exists():
        print(f"Loading fine-tuned model from: {FINETUNED_PATH}")
        # Load base model first
        print("Loading base model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        base_model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            dtype=torch.float16,
        )
        
        # Load LoRA adapter
        print("Loading LoRA adapter...")
        model = PeftModel.from_pretrained(base_model, FINETUNED_PATH)
        print("Model loaded successfully")
    else:
        print(f"Fine-tuned model not found at {FINETUNED_PATH}")
        print("Loading base model instead...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            dtype=torch.float16,
        )

    print("")

    test_prompts = [
        # Hardware
        "User: What are the main types of network switches?",
        "User: Explain RAID configurations for servers",
        "User: What is the difference between SAS and SATA?",
        # Networking & Security
        "User: What is the difference between IDS and IPS?",
        "User: Explain VPN protocols and their use cases",
        "User: What are firewall rules and how do they work?",
        # Cloud
        "User: What are the main cloud computing service models?",
        "User: Explain serverless computing and its benefits",
        "User: What is AWS Lambda and when should I use it?",
        # IoT
        "User: What are the main IoT communication protocols?",
        "User: Explain MQTT and how it works",
        "User: What is edge computing in IoT?",
        # Cybersecurity
        "User: What are the main types of cyber attacks?",
        "User: Explain the CIA triad in cybersecurity",
        "User: What is zero trust security?",
        # Programming
        "User: What are the principles of clean code?",
        "User: Explain microservices architecture",
        "User: What is test-driven development (TDD)?",
        # AI/ML
        "User: What are the main types of machine learning?",
        "User: Explain neural network architectures",
        "User: What is deep learning and its applications?",
        # Databases
        "User: What are the main types of databases?",
        "User: Explain SQL vs NoSQL databases",
        "User: What is database sharding?",
        # Operating Systems
        "User: What are the main operating system types?",
        "User: Explain virtualization technologies",
        "User: What is containerization vs virtualization?",
        # Blockchain
        "User: What is blockchain technology?",
        "User: Explain smart contracts",
        "User: What is DeFi (Decentralized Finance)?",
        # Mobile/Wireless
        "User: What are the main mobile communication technologies?",
        "User: Explain 5G technology and its applications",
        "User: What are wireless networking standards?",
        # DevOps
        "User: What is DevOps and its core principles?",
        "User: Explain CI/CD pipeline components",
        "User: What is Infrastructure as Code (IaC)?",
    ]

    print("Testing comprehensive technology knowledge...")
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        inputs = tokenizer(prompt, return_tensors="pt")
        # Move inputs to same dtype as model, but keep input_ids as Long
        inputs = {k: v.to(model.dtype) if hasattr(v, 'to') and v.dtype.is_floating_point else v for k, v in inputs.items()}
        outputs = model.generate(**inputs, max_new_tokens=200)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Response: {response}")

    print("")
    print("Model test complete")

if __name__ == "__main__":
    main()
