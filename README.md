# Oil Spill Detection System

A deep-learning-based marine pollution monitoring system that uses satellite imagery and U-Net image segmentation to identify, segment, and map oil spill regions.

---

## Features

- **Semantic Segmentation:** Uses U-Net neural network architecture to perform pixel-level classification of satellite imagery.
- **Marine Pollution Monitoring:** Automatically identifies oil slick boundaries against sea surfaces.
- **Git LFS Integration:** Tracks large binary files, including pre-trained weights and deep learning model files (`.h5`, `.pth`, or `.onnx`).

---

## Prerequisites

Ensure your system meets the following requirements before setup:

### System Requirements
- **OS:** Windows 10/11, macOS, or Linux
- **Python:** Python 3.8 or higher
- **Git & Git LFS:** Required for cloning large model files

### Hardware Recommendations
- **CPU:** Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **GPU (Recommended):** NVIDIA GPU with CUDA support for accelerated inference and training

---

## Installation & Setup

### 1. Install Git LFS
Because this repository tracks large model files using [Git LFS](https://git-lfs.github.com/), install Git LFS before cloning:

```bash
git lfs install
2. Clone the Repository
Clone the project locally and navigate into the project directory:

Bash
git clone [https://github.com/Thirniya-08/Oil-Spill-detection.git](https://github.com/Thirniya-08/Oil-Spill-detection.git)
cd Oil-Spill-detection

Pull the LFS tracked files to ensure model weights are completely downloaded:

Bash
git lfs pull

3. Set Up a Virtual Environment (Optional but Recommended)
On Windows:

Bash
python -m venv venv
venv\Scripts\activate
On macOS/Linux:

Bash
python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
Install all required packages:

Bash
pip install -r requirements.txt
If no requirements.txt is present, install the core dependencies directly:

Bash
pip install torch torchvision numpy opencv-python matplotlib pillow flask
Usage
Activate Environment: Ensure your virtual environment is active.

Run Application / Model: Navigate to the source folder and run the primary script or entry point:

Bash
cd "InnoWAH - Pre Finals"
python app.py
View Results: Upload or load satellite images into the interface/pipeline to generate oil spill segmentation masks.



