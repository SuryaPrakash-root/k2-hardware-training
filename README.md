# k2-horizon Technology Training

Train the k2-horizon model on comprehensive technology knowledge including hardware, networking, cloud, IoT, cybersecurity, and more.

## What This Trains

The model will learn about:
- **Hardware**: Servers, storage, networking equipment, components
- **Networking**: Switches, routers, firewalls, cables, protocols, wireless
- **Cloud Computing**: AWS, Azure, Google Cloud, serverless, containers
- **IoT**: Protocols (MQTT, CoAP), edge computing, device management
- **Cybersecurity**: Threats, defense, zero trust, SIEM, compliance
- **Programming**: Clean code, microservices, CI/CD, testing
- **AI/ML**: Neural networks, deep learning, NLP, computer vision
- **Databases**: SQL, NoSQL, sharding, replication, optimization
- **Operating Systems**: Linux, Windows, virtualization, containers
- **Blockchain**: Smart contracts, DeFi, consensus mechanisms
- **Mobile/Wireless**: 5G, Wi-Fi, Bluetooth, mobile development
- **DevOps**: CI/CD, IaC, monitoring, SRE, platform engineering

## RAG (Retrieval-Augmented Generation)

The platform now supports RAG — ask questions against your uploaded documents **without retraining**:

```
Upload → chunk → embed (all-MiniLM-L6-v2) → FAISS vector index
Query  → embed query → cosine top-k search → context prompt → grounded answer
```

### How it works

1. **Auto-indexing**: Every upload (file, batch, or URL) is automatically embedded and added to a FAISS index (`rag_index/`)
2. **Retrieval**: At query time, the question is embedded and the top-K most similar chunks are retrieved by cosine similarity
3. **Generation**: Retrieved chunks are injected into the prompt as context; the model answers only from that context and cites sources
4. **UI**: New **RAG** tab shows the vector index status, top-K slider, answer, and retrieved sources with similarity scores

### RAG API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rag/status` | Index stats (vectors, sources, model) |
| POST | `/api/rag/query` | `{question, top_k}` → answer + sources |
| POST | `/api/rag/reindex` | Rebuild index from all uploaded docs |
| DELETE | `/api/rag/index` | Clear the index |

### RAG vs fine-tuning

| | Fine-tuning (Train tab) | RAG (RAG tab) |
|---|---|---|
| Knowledge source | Baked into weights | Retrieved at query time |
| New documents | Requires retraining | Instantly indexed |
| Source citation | No | Yes (with similarity score) |
| Best for | Style/behavior adaptation | Document Q&A |

## Quick Start

```bash
# 1. Install dependencies
./install.sh

# 2. Activate environment
source ~/k2-hardware-training/venv/bin/activate

# 3. Train the model
python train_lora.py

# 4. Test the model
python test.py
```

## Training Options

| Method | Command | Speed | Quality |
|--------|---------|-------|---------|
| **LoRA** | `python train_lora.py` | Fast | Good |
| **Unsloth** | `python train_unsloth.py` | Fastest | Good |
| **Full** | `python train.py` | Slow | Best |

## Dataset

The dataset contains **262+ Q&A pairs** covering comprehensive technology topics:

### Hardware & Networking (50+ examples)
- Network switches, routers, firewalls
- Server form factors, specifications, RAID
- Storage systems (NAS, SAN, SAS, SATA)
- Network cables, topologies, PoE
- Data center infrastructure

### IoT & Embedded Systems (25+ examples)
- IoT communication protocols (MQTT, CoAP, Zigbee)
- Edge computing and fog computing
- IoT device management and security
- Industrial IoT (IIoT) applications

### Cloud Technologies (25+ examples)
- Cloud service models (IaaS, PaaS, SaaS)
- AWS, Azure, Google Cloud services
- Serverless computing, containers, Kubernetes
- Cloud security and cost optimization

### Cybersecurity (25+ examples)
- Cyber attack types and defense strategies
- Zero trust security, SIEM, incident response
- Compliance frameworks (NIST, ISO 27001)
- Penetration testing and vulnerability management

### Programming & DevOps (25+ examples)
- Clean code principles, design patterns
- CI/CD pipelines, version control
- Microservices architecture
- Test-driven development, code review

### AI/ML & Data Science (25+ examples)
- Machine learning types and algorithms
- Neural network architectures (CNN, RNN, Transformer)
- Deep learning applications
- NLP, computer vision, reinforcement learning

### Databases (25+ examples)
- SQL vs NoSQL databases
- Database indexing and optimization
- Sharding, replication, ACID properties
- Graph databases, time-series databases

### Operating Systems (25+ examples)
- Linux vs Windows
- Virtualization and containerization
- Real-time operating systems (RTOS)
- System administration and monitoring

### Blockchain & Web3 (15+ examples)
- Blockchain technology and consensus mechanisms
- Smart contracts and DeFi
- NFTs and supply chain applications

### Mobile & Wireless (15+ examples)
- 5G technology and applications
- Mobile app development approaches
- Wireless networking standards

### DevOps & Automation (20+ examples)
- CI/CD pipeline components
- Infrastructure as Code (IaC)
- Monitoring, observability, SRE
- Platform engineering and GitOps

## Adding More Training Data

Add more Q&A pairs to the dataset:

```bash
# Edit the dataset
nano ~/k2-hardware-training/data/hardware_knowledge_base.jsonl

# Add lines in this format:
{"text": "User: Your question here\nAssistant: Your detailed answer here"}
```

## Training Tips

1. **Comprehensive Dataset**: We've expanded from 50 to 262+ examples covering all technology domains
2. **Quality Matters**: Focus on accurate, detailed answers
3. **Test Often**: Run test.py after training to evaluate across all topics
4. **Save Checkpoints**: Training saves models automatically
5. **Add More Data**: You can expand to 500+ examples for even better results

## Model Output

After training, models are saved to:
- LoRA: `~/k2-hardware-training/models/hardware-lora/`
- Unsloth: `~/k2-hardware-training/models/hardware-unsloth/`

## Testing

Test your trained model:

```bash
# Test with sample hardware questions
python test.py

# Or test interactively
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('~/k2-hardware-training/models/hardware-lora')
tokenizer = AutoTokenizer.from_pretrained('~/k2-hardware-training/models/hardware-lora')
prompt = 'User: What is the difference between a router and a switch?'
inputs = tokenizer(prompt, return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0]))
"
```

## Resources

- [MLX Documentation](https://ml-explore.github.io/mlx/)
- [Unsloth Documentation](https://unsloth.ai/)
- [Hugging Face Training](https://huggingface.co/docs/transformers/training)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)

## Files

- `install.sh` - Install dependencies
- `train.py` - Basic training
- `train_lora.py` - LoRA training (recommended)
- `train_unsloth.py` - Unsloth training (fastest)
- `test.py` - Test trained model
- `data/hardware_knowledge_base.jsonl` - Training dataset
- `README.md` - This file
