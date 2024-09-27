# System requirement

## Hardware

### GPU

Running on the CPU is the default option. It is possible to run Docker containers on GPUs using the --gpus option when launching a container. However, be aware that this feature is still experimental and may cause errors.

Nvidia GPU is required for CUDA usage.

- NVIDIA Hopper
  - H100
- NVIDIA Ada Lovelace architecture
  - GeForce RTX 4090
  - GeForce RTX 4080
  - GeForce RTX 4070 Ti
  - GeForce RTX 4070
  - GeForce RTX 4060 Ti
  - GeForce RTX 4060
- NVIDIA Ampere architecture
  - GeForce RTX 3090 Ti
  - GeForce RTX 3090
  - GeForce RTX 3080 Ti
  - GeForce RTX 3080
  - GeForce RTX 3070 Ti
  - GeForce RTX 3070
  - GeForce RTX 3060 Ti
  - GeForce RTX 3060
  - GeForce RTX 3050
  - A100
  - A40
  - A30
  - A10
- NVIDIA Turing
  - GeForce RTX 2080 Ti
  - GeForce RTX 2080 Super
  - GeForce RTX 2080
  - GeForce RTX 2070 Super
  - GeForce RTX 2070
  - GeForce RTX 2060 Super
  - GeForce RTX 2060
  - GeForce GTX 1660 Ti
  - GeForce GTX 1660 Super
  - GeForce GTX 1660
  - GeForce GTX 1650 Super
  - GeForce GTX 1650
  - Quadro RTX 8000
  - Quadro RTX 6000
  - Quadro RTX 5000
- NVIDIA Volta:
  - Tesla V100
  - Titan V

### Memory

- Minimum 8GB RAM (16GB or more recommended)
- Sufficient disk space (minimum 100GB recommended)

## Software

- OS : Linux (based on Ubuntu 22.04)
- NVIDIA driver version : 450.80.02 or later
- Docker : 19.03 or later (with NVIDIA Container Toolkit support)
- NVIDIA Container Toolkit (nvidia-docker2)