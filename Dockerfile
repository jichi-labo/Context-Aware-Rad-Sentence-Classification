FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and necessary system packages
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python
RUN ln -s /usr/bin/python3.10 /usr/local/bin/python && \
    ln -s /usr/bin/pip3 /usr/local/bin/pip

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /workspace

# Copy requirements file
COPY requirements.txt /workspace/requirements.txt

# Install Python packages (PyTorch is fetched from the CUDA 12.1 wheel index)
RUN pip install -r /workspace/requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121

# Set environment variables for CUDA
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Copy project files
COPY . /workspace

CMD ["/bin/bash"]
