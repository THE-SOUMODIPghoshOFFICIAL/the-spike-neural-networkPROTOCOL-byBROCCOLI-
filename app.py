# To run this Python code, you need the following libraries:
# pip install Flask Pillow torch torchvision snntorch flask-cors

import os
import numpy as np
import io
import torch
import torch.nn as nn
import snntorch as snn
from snntorch import spikegen
from torchvision import transforms
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS # Import CORS
from PIL import Image

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- 1. Define the Spiking Neural Network Model Architecture ---
# This class must be identical to the one in your trainer.py file
class SpikingNet(nn.Module):
    def __init__(self):
        super(SpikingNet, self).__init__()

        # Define the spiking neuron model: Leaky Integrate-and-Fire (LIF)
        beta = 0.95 # Neuron decay rate
        
        # Layer 1: Fully-connected layer followed by a LIF neuron
        self.fc1 = nn.Linear(28*28, 1000)
        self.lif1 = snn.Leaky(beta=beta)

        # Layer 2: Fully-connected layer followed by a LIF neuron
        self.fc2 = nn.Linear(1000, 10)
        self.lif2 = snn.Leaky(beta=beta)

    def forward(self, x):
        # Initialize membrane potentials and outputs for each layer
        mem1 = self.lif1.init_leaky()
        mem2 = self.lif2.init_leaky()

        # Create empty lists to store outputs from the spiking layers
        spk_rec = []
        mem_rec = []
        
        num_steps = x.size(0)

        # Loop over each time step
        for step in range(num_steps):
            # Input to the first layer at the current time step
            cur1 = self.fc1(x[step].view(x[step].size(0), -1))
            spk1, mem1 = self.lif1(cur1, mem1)

            # Input to the second layer
            cur2 = self.fc2(spk1)
            spk2, mem2 = self.lif2(cur2, mem2)

            # Record the outputs
            spk_rec.append(spk2)
            mem_rec.append(mem2)

        return torch.stack(spk_rec, dim=0), torch.stack(mem_rec, dim=0)

# --- 2. Load the Trained Model ---
# This will be run once when the server starts
model_path = 'snn_mnist_model.pth'

if not os.path.exists(model_path):
    print("⚠️  Train your model first by running: python trainer.py")

try:
    snn_model = SpikingNet()
    # Map the model to CPU to avoid issues with GPU-trained models on CPU-only machines
    snn_model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    snn_model.to('cpu')  # Ensure the model is on the CPU
    snn_model.eval() # Set the model to evaluation mode
    print("SNN model loaded successfully.")
except FileNotFoundError:
    snn_model = None
    print(f"Error: Model file '{model_path}' not found. Please train the model first by running trainer.py.")
except Exception as e:
    snn_model = None
    print(f"An error occurred while loading the model: {str(e)}")

# --- 3. Define Image Transformations ---
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0,), (1,))
])

# --- 4. API Endpoint to Evaluate Image ---
@app.route('/evaluate-image', methods=['POST'])
def evaluate_image():
    if snn_model is None:
        return jsonify({'error': 'Model not loaded. Please train the model and restart the server.'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image file part in the request'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            pil_image = Image.open(io.BytesIO(file.read())).convert('L')
            
            # Add a batch dimension and pass the image to the CPU
            image_tensor = transform(pil_image).unsqueeze(0).to('cpu')
            
            # --- Generate the spike train for the model --
            num_steps = 25
            data_spikes = spikegen.rate(image_tensor, num_steps=num_steps)

            # --- Forward pass through the SNN model to get a prediction --
            with torch.no_grad():
                spk_out, mem_out = snn_model(data_spikes)
            
            # The model predicts the digit with the highest total spike count
            _, predicted_class = torch.sum(spk_out, dim=0).max(1)
            predicted_digit = predicted_class.item()
            
            message = f'Image processed successfully! The SNN model predicts the digit is: {predicted_digit}'

            return jsonify({
                'message': message,
                'status': 'success',
                'prediction': predicted_digit
            })
            
        except Exception as e:
            # Add a print statement to the console for debugging
            print(f"An error occurred in the Flask endpoint: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500
@app.route('/')
def home():
    """Serves the main HTML page."""
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, port=5500)