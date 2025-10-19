# CogniSpike: SNN Protocol Dashboard

[![License](https://img.shields.io/badge/License-Custom-red.svg)](LICENSE)

An interactive web dashboard demonstrating Spiking Neural Network (SNN) principles. Built with Flask, snnTorch, and love ❤️.

## Features

This project showcases several aspects of SNNs through an interactive, futuristic UI:

1.  **Digit Classifier:** Upload a handwritten digit image (0-9) and see the SNN predict the number based on spike patterns.
2.  **Spike Visualizer:** Upload an image and view a static raster plot showing how the image is encoded into spikes over time.
3.  **Live Encoder:** Upload an image to generate an animated GIF visualizing the spike encoding process dynamically.
4.  **Guide:** An informational section explaining the basics of SNNs and spike encoding.

## Tech Stack

* **Backend:** Python, Flask, snnTorch, PyTorch, Pillow, Matplotlib
* **Frontend:** HTML, CSS, JavaScript
* **Core Concept:** Spiking Neural Networks (SNNs), Rate Encoding

## Setup & Running

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/the-spike-neural-networkPROTOCOL-byBROCCOLI.git](https://github.com/YOUR_USERNAME/the-spike-neural-networkPROTOCOL-byBROCCOLI.git)
    cd the-spike-neural-networkPROTOCOL-byBROCCOLI
    ```

2.  **Install dependencies:**
    ```bash
    pip install flask torch torchvision snntorch matplotlib flask-cors Pillow
    ```
    * *(Optional but recommended: Use a Python virtual environment (`venv`))*
    * *You might also need the [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) on Windows for PyTorch.*

3.  **Train the SNN Model (if needed):**
    * A pre-trained model (`snn_mnist_model.pth`) is included.
    * To retrain, run:
        ```bash
        python trainer.py
        ```

4.  **Run the Flask application:**
    ```bash
    python app.py
    ```

5.  **Access the dashboard:** Open your web browser and go to `http://127.0.0.1:5500` (or the address shown in the terminal).

## Project Structure
snn_project/ ├── app.py # Main Flask application
             ├── trainer.py # Script to train the SNN model 
             ├── snn_mnist_model.pth # Pre-trained SNN model file 
             ├── templates/ 
             │  └── index.html # Main HTML structure 
             └── static/ 
             |       ├── style.css # CSS styling 
             |       ├── script.js # JavaScript for interactivity 
             |       └── assets/ # Images, icons, etc. 
             ├── .gitignore # Files for Git to ignore 
             ├── LICENSE # Project license 
             └── README.md # This file



## License

This project is under a custom license. Please see the [LICENSE](LICENSE) file for details. **Commercial use, redistribution, or publication without explicit permission is prohibited.**

---
*Created by BROCCOLI*


