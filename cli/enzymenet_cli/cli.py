import argparse
import subprocess
import os
import shutil
import sys

IMAGE = "tanakahiroki1989/enzymenet:ver1.0"
MODEL_DIR = os.path.expanduser("~/.enzymenet/model")

def check_docker():
    if not shutil.which("docker"):
        print("Docker is required")
        sys.exit(1)

def ensure_model():
    if os.path.exists(MODEL_DIR):
        return

    os.makedirs(MODEL_DIR, exist_ok=True)

    subprocess.run([
        "git", "clone",
        "https://huggingface.co/nao653137/EnzymeNet_base",
        MODEL_DIR
    ])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output")
    parser.add_argument("--gpu", action="store_true")

    args = parser.parse_args()

    check_docker()
    ensure_model()

    input_path = os.path.abspath(args.input_file)
    output_path = os.path.abspath(args.output)

    gpu_flag = ["--gpus", "all"] if args.gpu else []

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.dirname(input_path)}:/app",
        "-v", f"{MODEL_DIR}:/root/.enzymenet/model",
        *gpu_flag,
        IMAGE,
        "/app/" + os.path.basename(input_path),
        "/app/" + os.path.basename(output_path),
    ]

    subprocess.run(cmd)