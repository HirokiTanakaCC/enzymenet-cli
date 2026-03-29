# EnzymeNet CLI

Run EnzymeNet from the command line using Docker.

---

## 🚀 Quick Start

```bash
pip install enzymenet-cli
enzymenet input.fasta output_dir
```

---

## ⚙️ Requirements

* Docker (must be installed and running)
* GPU (optional)

---

## 💻 Usage

```bash
enzymenet input.fasta output_dir
```

With GPU:

```bash
enzymenet input.fasta output_dir --gpu
```

---

## 📂 Input / Output

* Input: FASTA file
* Output: Directory containing results

---



---

## 📦 Model

The model is automatically downloaded on first run:

```
~/.enzymenet/model
```

---

## 🐳 Docker Image

```
tanakahiroki1989/enzymenet:ver1.0
```

---

## 🔗 Source

https://github.com/HirokiTanakaCC/enzymenet-cli
