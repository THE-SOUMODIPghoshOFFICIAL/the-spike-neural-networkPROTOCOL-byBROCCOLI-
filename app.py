# To run this Python code, you need the following libraries:
# pip install Flask Pillow torch torchvision snntorch flask-cors matplotlib
import os
import numpy as np
import io
import base64
import torch
import torch.nn as nn
import snntorch as snn
from snntorch import spikegen
from snntorch import spikeplot as splt
from torchvision import transforms
from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- 1. Define the Spiking Neural Network Model Architecture ---
class SpikingNet(nn.Module):
    def __init__(self):
        super(SpikingNet, self).__init__()
        beta = 0.95
        self.fc1 = nn.Linear(28*28, 1000)
        self.lif1 = snn.Leaky(beta=beta)
        self.fc2 = nn.Linear(1000, 10)
        self.lif2 = snn.Leaky(beta=beta)

    def forward(self, x):
        mem1 = self.lif1.init_leaky()
        mem2 = self.lif2.init_leaky()
        spk_rec = []
        mem_rec = []
        num_steps = x.size(0)
        for step in range(num_steps):
            cur1 = self.fc1(x[step].view(x[step].size(0), -1))
            spk1, mem1 = self.lif1(cur1, mem1)
            cur2 = self.fc2(spk1)
            spk2, mem2 = self.lif2(cur2, mem2)
            spk_rec.append(spk2)
            mem_rec.append(mem2)
        return torch.stack(spk_rec, dim=0), torch.stack(mem_rec, dim=0)

# --- 2. Load the Trained Model ---
model_path = 'snn_mnist_model.pth'
snn_model = None
if os.path.exists(model_path):
    try:
        snn_model = SpikingNet()
        snn_model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        snn_model.to('cpu')
        snn_model.eval()
        print("SNN model loaded successfully.")
    except Exception as e:
        print(f"❌ An error occurred while loading the model: {str(e)}")
else:
    print(f"⚠️ Model file '{model_path}' not found. Please train the model first by running trainer.py.")

# --- 3. Define Image Transformations ---
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.Grayscale(),
    transforms.ToTensor(),
    transforms.Normalize((0,), (1,))
])

def preprocess_image(image_file):
    """Helper function to preprocess an uploaded image."""
    pil_image = Image.open(io.BytesIO(image_file.read())).convert('L')
    image_tensor = transform(pil_image).unsqueeze(0).to('cpu')
    return image_tensor

# --- 4. API Endpoints ---
@app.route('/')
def home():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/evaluate-image', methods=['POST'])
def evaluate_image():
    if snn_model is None:
        return jsonify({'error': 'Model not loaded.'}), 500
    if 'image' not in request.files:
        return jsonify({'error': 'No image file part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image_tensor = preprocess_image(file)
        num_steps = 25
        data_spikes = spikegen.rate(image_tensor, num_steps=num_steps)
        
        with torch.no_grad():
            spk_out, _ = snn_model(data_spikes)
        
        _, predicted_class = torch.sum(spk_out, dim=0).max(1)
        predicted_digit = predicted_class.item()
        
        return jsonify({
            'message': f'Model prediction: The digit is {predicted_digit}.',
            'prediction': predicted_digit
        })
    except Exception as e:
        print(f"Error in /evaluate-image: {str(e)}")
        return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

@app.route('/visualize', methods=['POST'])
def visualize_spikes():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image_tensor = preprocess_image(file)
        num_steps = 100
        spike_data = spikegen.rate(image_tensor, num_steps=num_steps)
        
        # Generate raster plot
        fig, ax = plt.subplots(figsize=(10, 5))
        splt.raster(spike_data.squeeze(1), ax, s=1.5, c='black')
        ax.set_title('Spike Raster Plot')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Neuron Index')
        plt.tight_layout()

        # Save plot to a bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        # Encode image to base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        raster_plot_url = f'data:image/png;base64,{img_base64}'

        return jsonify({'raster_plot_url': raster_plot_url})
    except Exception as e:
        print(f"Error in /visualize: {str(e)}")
        return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

@app.route('/live-encoder', methods=['POST'])
def live_encoder():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image_tensor = preprocess_image(file)
        num_steps = 100
        spike_data = spikegen.rate(image_tensor, num_steps=num_steps)

        # Generate animation
        fig, ax = plt.subplots(figsize=(5, 5))
        anim = splt.animator(spike_data.squeeze(1), fig, ax)
        
        # Save animation to a bytes buffer as a GIF
        buf = io.BytesIO()
        anim.save(buf, writer='pillow', format='gif', fps=10)
        plt.close(fig)
        buf.seek(0)
        
        # Encode GIF to base64
        gif_base64 = base64.b64encode(buf.read()).decode('utf-8')
        spike_gif_url = f'data:image/gif;base64,{gif_base64}'

        return jsonify({'spike_gif_url': spike_gif_url})
    except Exception as e:
        print(f"Error in /live-encoder: {str(e)}")
        return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5500)