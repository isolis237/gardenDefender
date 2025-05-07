from ultralytics import YOLO
import torch
import os


#print("CUDA available:", torch.cuda.is_available())
#print("Using device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

# Load pre-trained model
model = YOLO("models/yolo11s.pt")

# Train (fine-tune) on custom dataset
model.train(
    data=os.path.abspath("./fine_tuning/gardenSniper_dataset_basic_aug/data.yaml"),
    epochs=125,
    imgsz=640,
    device=0,
    batch=25,
    workers=4,
    optimizer="AdamW",
    lr0=160e-6,
    lrf=0.01,
    warmup_epochs=8,
    dropout=0.175,
    patience=35,
    close_mosaic=55,
    val=True,
    save=True,
    save_period=10,
    # Augmentations
    hsv_h=0.012,
    hsv_s=0.75,
    hsv_v=0.45,
    degrees=14.5,
    translate=0.1,
    scale=0.4,
    shear=3.5,
    perspective=0.001,
    flipud=0.0,
    fliplr=0.5,
    mosaic=0.375,
    mixup=0.08
)