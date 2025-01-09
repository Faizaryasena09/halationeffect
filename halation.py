import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageFilter, ImageEnhance, ImageTk
import numpy as np
import cv2

def add_halation_effect(image, intensity, blur_radius, opacity):
    image_np = np.array(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    
    # Apply threshold to detect bright areas
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Create a mask with bright areas
    bright_areas = cv2.bitwise_and(image_np, image_np, mask=bright_mask)

    # Add a reddish tint to bright areas
    reddish_areas = bright_areas.copy()
    reddish_areas[:, :, 0] = np.minimum(reddish_areas[:, :, 0] + intensity * 80, 255)  # Increase red channel
    reddish_areas[:, :, 1] = np.minimum(reddish_areas[:, :, 1] - intensity * 20, 255)  # Slightly decrease green channel
    reddish_areas[:, :, 2] = np.minimum(reddish_areas[:, :, 2] - intensity * 20, 255)  # Slightly decrease blue channel

    # Apply Gaussian Blur to the reddish areas
    reddish_image = Image.fromarray(np.uint8(np.clip(reddish_areas, 0, 255)))
    blurred = reddish_image.filter(ImageFilter.GaussianBlur(blur_radius))

    # Convert blurred image back to numpy array
    blurred_np = np.array(blurred)

    # Only blend blurred areas with the original image using opacity
    # Combine original image with the blurred version only in the bright areas
    final_image_np = image_np.copy()
    final_image_np[bright_mask == 255] = (final_image_np[bright_mask == 255] * (1 - opacity) + blurred_np[bright_mask == 255] * opacity).astype(np.uint8)

    # Convert back to PIL Image
    final_image = Image.fromarray(final_image_np)

    # Enhance brightness and contrast for a more vivid effect
    enhancer = ImageEnhance.Brightness(final_image)
    enhanced_image = enhancer.enhance(1.1)

    enhancer = ImageEnhance.Contrast(enhanced_image)
    final_image = enhancer.enhance(1.2)

    return final_image

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        global img, original_image
        original_image = Image.open(file_path)
        img = ImageTk.PhotoImage(original_image)
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.config(width=img.width(), height=img.height())

def apply_effect():
    if original_image:
        intensity = intensity_scale.get()
        blur_radius = blur_scale.get()
        opacity = opacity_scale.get() / 100.0  # Convert from percentage to float
        result_image = add_halation_effect(original_image, intensity, blur_radius, opacity)
        result_img = ImageTk.PhotoImage(result_image)
        canvas.create_image(0, 0, anchor="nw", image=result_img)
        canvas.img = result_img  # keep a reference to avoid garbage collection

def save_image():
    if original_image:
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            opacity = opacity_scale.get() / 100.0  # Convert from percentage to float
            result_image = add_halation_effect(original_image, intensity_scale.get(), blur_scale.get(), opacity)
            result_image.save(file_path)

# Setup GUI
root = tk.Tk()
root.title("Enhanced Halation Effect App with Reddish Tint")

# Canvas for image display
canvas = tk.Canvas(root, width=600, height=400)
canvas.pack()

# Controls frame
controls = ttk.Frame(root)
controls.pack(fill="x", padx=10, pady=5)

# Buttons and scales
open_button = ttk.Button(controls, text="Open Image", command=open_image)
open_button.pack(side="left")

ttk.Label(controls, text="Intensity:").pack(side="left", padx=5)
intensity_scale = tk.Scale(controls, from_=1, to=5, orient="horizontal")  # Changed to tk.Scale
intensity_scale.set(2)
intensity_scale.pack(side="left", padx=5)

ttk.Label(controls, text="Blur Radius:").pack(side="left", padx=5)
blur_scale = tk.Scale(controls, from_=1, to=20, orient="horizontal")  # Changed to tk.Scale
blur_scale.set(10)
blur_scale.pack(side="left", padx=5)

ttk.Label(controls, text="Opacity:").pack(side="left", padx=5)
opacity_scale = tk.Scale(controls, from_=0, to=100, orient="horizontal")  # Changed to tk.Scale
opacity_scale.set(50)
opacity_scale.pack(side="left", padx=5)

apply_button = ttk.Button(controls, text="Apply Effect", command=apply_effect)
apply_button.pack(side="left", padx=5)

save_button = ttk.Button(controls, text="Save Image", command=save_image)
save_button.pack(side="left", padx=5)

root.mainloop()
