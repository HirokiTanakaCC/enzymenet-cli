# 🧬 EnzymeNet CLI

![PyPI](https://img.shields.io/pypi/v/enzymenet-cli)
![Python](https://img.shields.io/pypi/pyversions/enzymenet-cli)
![License](https://img.shields.io/github/license/HirokiTanakaCC/enzymenet-cli)

Run EnzymeNet easily from the command line using Docker.
No complex environment setup is required.

---

## 🚀 Quick Start

```bash
pip install enzymenet-cli
enzymenet input.fasta output_dir
```

---

## ⚙️ Requirements

* Docker (required)
* GPU (optional, for faster inference)

> Docker must be installed and running.

---

## 💻 Usage

### Basic

```bash
enzymenet input.fasta output_dir
```

### With GPU

```bash
enzymenet input.fasta output_dir --gpu
```

---

## 📂 Input / Output

* `input.fasta` : Input FASTA file
* `output_dir/` : Output directory

All results are saved inside `output_dir/`.

---

## 📊 Example Output

When running:

```bash
enzymenet sample.fasta output_dir
```

You may get results like:

| name                                                 | EC_1d | EC_2d | EC_3d | EC_4d_score |
| ---------------------------------------------------- | ----- | ----- | ----- | ----------- |
| bvl:BF3285c1_1877 alcohol dehydrogenase              | 1     | 1.1   | 1.1.1 | 0.999333    |
| cdk:105091729 NNMT; nicotinamide N-methyltransferase | 2     | 1.1   | 1.1.1 | 1.000000    |
| bacu:103011388 CES5A; carboxylesterase 5A            | 3     | 1.1   | 1.1.1 | 1.000000    |
| egu:105038446 pyruvate decarboxylase 1               | 4     | 1.1   | 1.1.1 | 1.000000    |
| cpro:CPRO_12240 alr_1; alanine racemase              | 5     | 1.1   | 1.1.1 | 0.999985    |
| php:PhaeoP97_01130 tyrS; tyrosyl-tRNA synthetase     | 6     | 1.1   | 1.1.1 | 1.000000    |
| nega_No19956 consecutive_substitution                | -     | -     | -     | -           |

---

## 📌 Columns

* **name**: protein identifier and annotation
* **EC_1d ~ EC_3d**: predicted EC hierarchy
* **EC_4d_score**: confidence score (`-` means no prediction)

---

## 🔧 First Run

The model will be automatically downloaded on the first run:

```text
~/.enzymenet/model
```

This may take a few minutes.

---

## 🐳 Docker

This tool internally uses the following Docker image:

```text
tanakahiroki1989/enzymenet:ver1.0
```

---

## ❗ Notes

* Docker must be running
* The input file must exist
* The first run may take time due to model download

---

## 🧑‍💻 Development

```bash
git clone https://github.com/HirokiTanakaCC/enzymenet-cli
cd enzymenet-cli
pip install -e .
```

---

## 📄 License

MIT License
