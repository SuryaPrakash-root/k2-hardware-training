#!/usr/bin/env python3
"""
Fine-tune k2-horizon model for technology knowledge using LoRA
"""

import os
import sys
import json
from pathlib import Path

# Use the correct K2-Horizon base model
MODEL_PATH = "IFM/K2-Horizon-0.9B"
DATASET_PATH = "/Users/suryaprakashk/k2-hardware-training/data/hardware_knowledge_base.jsonl"
OUTPUT_DIR = "/Users/suryaprakashk/k2-hardware-training/models/hardware-lora"

def load_dataset():
    """Load the hardware knowledge dataset"""
    data = []
    with open(DATASET_PATH, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def main():
    print("=== k2-horizon Technology LoRA Training ===")
    print("")

    try:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            Trainer,
            DataCollatorForLanguageModeling,
        )
        from datasets import Dataset
        import torch
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install dependencies: pip install transformers datasets torch peft")
        return

    print(f"Model path: {MODEL_PATH}")
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")

    if not Path(DATASET_PATH).exists():
        print(f"Dataset not found at {DATASET_PATH}")
        return

    print("Loading dataset...")
    dataset = load_dataset()
    print(f"Dataset loaded with {len(dataset)} examples")

    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    print("Model loaded successfully")

    # LoRA configuration for K2-Horizon
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = Dataset.from_list(dataset)

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        weight_decay=0.01,
        save_strategy="epoch",
        logging_steps=10,
        fp16=True,
        warmup_steps=50,
        max_grad_norm=1.0,
        dataloader_num_workers=2,
        report_to="none",
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    print("")
    print("Starting LoRA training...")
    print("This will train the model on comprehensive technology knowledge.")
    print("")

    trainer.train()

    print("")
    print("Training complete!")
    print(f"Model saved to: {OUTPUT_DIR}")
    
    # Save tokenizer
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Tokenizer saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
