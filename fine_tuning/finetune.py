from ultralytics import YOLO
import torch
import os


#print("CUDA available:", torch.cuda.is_available())
#print("Using device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

# Load pre-trained model
model = YOLO("models/yolo11s.pt")

# Train (fine-tune) on custom dataset
model.train(
    data=os.path.abspath("./gardenSniper_dataset/data.yaml"),
    epochs=100,
    imgsz=480,
    device=0  # GPU if available
)
