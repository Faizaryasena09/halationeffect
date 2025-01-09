import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageFilter, ImageTk
import numpy as np
import cv2

MAX_WIDTH = 800  # Maksimum lebar gambar yang akan ditampilkan
MAX_HEIGHT = 600  # Maksimum tinggi gambar yang akan ditampilkan

def add_halation_effect(image, intensity, blur_radius):
    image_np = np.array(image)
    
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    red_tint = np.zeros_like(image_np)
    red_tint[:, :, 0] = bright_mask
    red_tint[:, :, 1] = bright_mask * 0.2
    red_tint[:, :, 2] = bright_mask * 0.2
    
    bright_areas = cv2.bitwise_and(red_tint, red_tint, mask=bright_mask)
    bright_areas = bright_areas * intensity
    
    bright_image = Image.fromarray(np.uint8(np.clip(bright_areas, 0, 255)))
    blurred = bright_image.filter(ImageFilter.GaussianBlur(blur_radius))
    merged_image = Image.blend(image, blurred, alpha=0.3)
    
    return merged_image

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        global img, original_image
        original_image = Image.open(file_path)
        
        # Resize image if larger than maximum allowed size
        original_image.thumbnail((MAX_WIDTH, MAX_HEIGHT))
        
        img = ImageTk.PhotoImage(original_image)
        canvas.config(width=img.width(), height=img.height())
        canvas.create_image(0, 0, anchor="nw", image=img)

def apply_effect():
    if original_image:
        intensity = intensity_scale.get()
        blur_radius = blur_scale.get()
        result_image = add_halation_effect(original_image, intensity, blur_radius)
        result_img = ImageTk.PhotoImage(result_image)
        canvas.config(width=result_img.width(), height=result_img.height())
        canvas.create_image(0, 0, anchor="nw", image=result_img)
        canvas.img = result_img

def save_image():
    if original_image:
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            result_image = add_halation_effect(original_image, intensity_scale.get(), blur_scale.get())
            result_image.save(file_path)

root = tk.Tk()
root.title("Responsive Halation Effect App")

canvas = tk.Canvas(root)
canvas.pack()

controls = ttk.Frame(root)
controls.pack(fill="x", padx=10, pady=5)

open_button = ttk.Button(controls, text="Open Image", command=open_image)
open_button.pack(side="left")

ttk.Label(controls, text="Intensity:").pack(side="left", padx=5)
intensity_scale = ttk.Scale(controls, from_=1, to=5, orient="horizontal")
intensity_scale.set(2)
intensity_scale.pack(side="left", padx=5)

ttk.Label(controls, text="Blur Radius:").pack(side="left", padx=5)
blur_scale = ttk.Scale(controls, from_=1, to=20, orient="horizontal")
blur_scale.set(10)
blur_scale.pack(side="left", padx=5)

apply_button = ttk.Button(controls, text="Apply Effect", command=apply_effect)
apply_button.pack(side="left", padx=5)

save_button = ttk.Button(controls, text="Save Image", command=save_image)
save_button.pack(side="left", padx=5)

root.mainloop()
