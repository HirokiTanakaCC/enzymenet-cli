# Use official TensorFlow GPU image
FROM tensorflow/tensorflow:2.1.0-gpu-py3

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
RUN pip install biopython pandas numpy tqdm huggingface_hub

# Copy application code
COPY . /app

RUN pip install .

ENTRYPOINT ["python", "-m", "enzymenet"]

