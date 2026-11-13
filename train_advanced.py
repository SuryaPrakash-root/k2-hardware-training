#!/usr/bin/env python3
"""
Advanced LoRA Training with QLoRA, Cosine Scheduler, Multi-turn, and Hyperparameter Search
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

MODEL_DIR = "/Users/suryaprakashk/.docker/models/bundles/sha256/bb2bef99eba2985e74ad3c15793af104ef6980bda94c188b3c314880e645020f/model"
sys.path.insert(0, MODEL_DIR)


def load_dataset(path: str, multi_turn: bool = False):
    data = []
    with open(path, 'r') as f:
        for line in f:
            if line.strip():
                example = json.loads(line)
                if multi_turn and 'conversations' in example:
                    data.append(example)
                elif not multi_turn and 'text' in example:
                    data.append(example)
    return data


def prepare_multiturn_data(data):
    formatted = []
    for item in data:
        if 'conversations' in item:
            text = ""
            for turn in item['conversations']:
                role = turn.get('from', turn.get('role', 'user'))
                content = turn.get('value', turn.get('content', ''))
                if role in ['user', 'human']:
                    text += f"User: {content}\n"
                elif role in ['assistant', 'gpt', 'bot']:
                    text += f"Assistant: {content}\n"
            formatted.append({"text": text.strip()})
        elif 'text' in item:
            formatted.append(item)
    return formatted


def filter_low_quality(data, min_length=50, max_length=2000):
    filtered = []
    for item in data:
        text = item.get('text', '')
        if len(text) < min_length or len(text) > max_length:
            continue
        if text.count('User:') == 0 or text.count('Assistant:') == 0:
            continue
        if len(text.split()) < 10:
            continue
        filtered.append(item)
    return filtered


def main():
    parser = argparse.ArgumentParser(description='Advanced K2 Training')
    parser.add_argument('--qlora', action='store_true', help='Enable QLoRA (4-bit quantization)')
    parser.add_argument('--cosine', action='store_true', help='Use cosine learning rate scheduler')
    parser.add_argument('--multiturn', action='store_true', help='Enable multi-turn conversation training')
    parser.add_argument('--filter', action='store_true', help='Apply data quality filter')
    parser.add_argument('--epochs', type=int, default=3, help='Number of epochs')
    parser.add_argument('--lr', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--batch_size', type=int, default=2, help='Batch size')
    parser.add_argument('--lora_rank', type=int, default=8, help='LoRA rank')
    parser.add_argument('--max_length', type=int, default=256, help='Max sequence length')
    parser.add_argument('--dataset', type=str, default='data/hardware_knowledge_base.jsonl', help='Dataset path')
    parser.add_argument('--output', type=str, default='models/hardware-lora-advanced', help='Output directory')
    args = parser.parse_args()

    print("=== Advanced K2 Training ===")
    print(f"QLoRA: {args.qlora}")
    print(f"Cosine Scheduler: {args.cosine}")
    print(f"Multi-turn: {args.multiturn}")
    print(f"Data Filter: {args.filter}")
    print(f"Epochs: {args.epochs}")
    print(f"Learning Rate: {args.lr}")
    print(f"LoRA Rank: {args.lora_rank}")
    print("")

    try:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            Trainer,
            DataCollatorForLanguageModeling,
            BitsAndBytesConfig,
        )
        from datasets import Dataset
        import torch
        from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install: pip install transformers datasets torch peft bitsandbytes")
        return

    print("Loading dataset...")
    dataset = load_dataset(args.dataset, args.multiturn)
    print(f"Loaded {len(dataset)} examples")

    if args.multiturn:
        dataset = prepare_multiturn_data(dataset)
        print(f"Prepared {len(dataset)} multi-turn examples")

    if args.filter:
        original_count = len(dataset)
        dataset = filter_low_quality(dataset)
        print(f"Filtered: {original_count} -> {len(dataset)} examples (removed {original_count - len(dataset)} low-quality)")

    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

    if args.qlora:
        print("Loading model with QLoRA (4-bit)...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            quantization_config=bnb_config,
            device_map="auto",
        )
        model = prepare_model_for_kbit_training(model)
    else:
        print("Loading model in full precision...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        )

    print("Model loaded successfully")

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_rank,
        lora_alpha=args.lora_rank * 2,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=args.max_length,
        )

    dataset_obj = Dataset.from_list(dataset)
    tokenized_dataset = dataset_obj.map(tokenize_function, batched=True)

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    if args.cosine:
        scheduler_type = "cosine"
        warmup_ratio = 0.1
    else:
        scheduler_type = "linear"
        warmup_ratio = 0.05

    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=args.lr,
        weight_decay=0.01,
        max_grad_norm=1.0,
        warmup_ratio=warmup_ratio,
        lr_scheduler_type=scheduler_type,
        logging_steps=10,
        save_strategy="epoch",
        fp16=False,
        bf16=True,
        report_to="none",
        remove_unused_columns=False,
        dataloader_num_workers=2,
        optim="adamw_torch",
        group_by_length=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    print("")
    print("Starting training...")
    start_time = datetime.now()

    trainer.train()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("")
    print(f"Training complete! Duration: {duration:.1f}s")

    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Model saved to: {args.output}")

    metrics = {
        "train_runtime": f"{duration:.1f}",
        "train_loss": f"{trainer.state.log_history[-1].get('train_loss', 0):.4f}" if trainer.state.log_history else "0",
        "epochs": args.epochs,
        "qlora": args.qlora,
        "cosine": args.cosine,
        "multiturn": args.multiturn,
        "filtered": args.filter,
    }
    print(f"Metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    main()
