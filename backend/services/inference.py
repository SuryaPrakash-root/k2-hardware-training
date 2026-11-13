import os
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

IS_DOCKER = os.path.exists("/.dockerenv")

if IS_DOCKER:
    MODEL_PATH = os.environ.get("MODEL_PATH", "/app/model")
    CHECKPOINT_PATH = os.environ.get("CHECKPOINT_PATH", "/app/models/hardware-lora/checkpoint-99")
else:
    MODEL_PATH = str(Path(__file__).parent.parent.parent / "models" / "base-model")
    CHECKPOINT_PATH = str(Path(__file__).parent.parent.parent / "models" / "hardware-lora" / "checkpoint-99")

_model = None
_tokenizer = None
_peft_model = None


def load_model():
    global _model, _tokenizer, _peft_model

    if _model is not None:
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print("Loading base model...")
    _tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
    )

    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        dtype=torch.float16,
        device_map=None,
    )

    print("Loading LoRA adapter...")
    _peft_model = PeftModel.from_pretrained(_model, CHECKPOINT_PATH)
    _peft_model.eval()
    print("Model ready!")


import re


def strip_thinking_tags(text: str) -> str:
    """Remove all thinking/reasoning blocks from model output"""
    if not text or not text.strip():
        return ""
    
    original = text
    
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ifm\|think>.*?</ifm\|think>', '', text, flags=re.DOTALL)
    text = re.sub(r'</ifm\|think>', '', text)
    text = re.sub(r'<ifm\|think>', '', text)
    text = re.sub(r'<\|.*?\|>', '', text)
    text = re.sub(r'\[.*?\]\[.*?\]', '', text)
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return original.strip() if original.strip() else "I couldn't generate a response. Please try again."
    
    if len(lines) == 1:
        text = lines[0]
    else:
        text = '\n'.join(lines[1:])
    
    text = text.strip()
    
    if not text and original.strip():
        return original.strip()
    
    return text if text else "I couldn't generate a response. Please try again."


def generate_response(prompt: str, max_new_tokens: int = 4096) -> str:
    global _model, _tokenizer, _peft_model

    if _peft_model is None:
        load_model()

    import torch

    messages = [
        {"role": "system", "content": "You are K2, a helpful AI assistant. Give direct, concise answers. Do not explain your thinking."},
        {"role": "user", "content": prompt}
    ]
    text = _tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = _tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = _peft_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.6,
            top_p=0.95,
            do_sample=True,
            repetition_penalty=1.1,
        )

    response = _tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )
    return strip_thinking_tags(response)
