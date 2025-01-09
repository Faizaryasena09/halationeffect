import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageFilter, ImageEnhance, ImageTk
import numpy as np
import cv2

MAX_WIDTH = 800  # Maksimum lebar gambar yang akan ditampilkan
MAX_HEIGHT = 600  # Maksimum tinggi gambar yang akan ditampilkan

def add_halation_effect(image, intensity, blur_radius, light_intensity):
    image_np = np.array(image)
    
    # Ubah gambar ke grayscale dan buat mask untuk area cerah
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Gunakan warna lebih lembut untuk tint, mengurangi kegelapan pada gambar
    halation_color = np.zeros_like(image_np)
    halation_color[:, :, 0] = bright_mask * 0.4  # Merah
    halation_color[:, :, 1] = bright_mask * 0.1  # Hijau
    halation_color[:, :, 2] = bright_mask * 0.1  # Biru
    
    # Gabungkan efek cahaya
    halation_area = cv2.bitwise_and(halation_color, halation_color, mask=bright_mask)
    halation_area = halation_area * intensity * light_intensity  # Kontrol intensitas cahaya
    
    # Gambar hasil efek halasi
    halation_image = Image.fromarray(np.uint8(np.clip(halation_area, 0, 255)))
    blurred = halation_image.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Gabungkan gambar asli dengan efek halasi tanpa menggelapkan gambar
    merged_image = Image.blend(image, blurred, alpha=0.2)  # Mengurangi alpha untuk efek lebih ringan
    
    return merged_image

def adjust_brightness(image, brightness_factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(brightness_factor)

def update_image(event=None):
    if original_image:
        brightness_factor = brightness_scale.get()
        intensity = intensity_scale.get()
        blur_radius = blur_scale.get()
        light_intensity = light_intensity_scale.get()
        
        # Sesuaikan kecerahan gambar
        adjusted_image = adjust_brightness(original_image, brightness_factor)
        
        # Terapkan efek halasi dengan kontrol intensitas cahaya
        result_image = add_halation_effect(adjusted_image, intensity, blur_radius, light_intensity)
        result_img = ImageTk.PhotoImage(result_image)
        
        canvas.config(width=result_img.width(), height=result_img.height())
        canvas.create_image(0, 0, anchor="nw", image=result_img)
        canvas.img = result_img

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

def save_image():
    if original_image:
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            brightness_factor = brightness_scale.get()
            intensity = intensity_scale.get()
            blur_radius = blur_scale.get()
            light_intensity = light_intensity_scale.get()
            
            # Sesuaikan kecerahan gambar dan simpan
            adjusted_image = adjust_brightness(original_image, brightness_factor)
            result_image = add_halation_effect(adjusted_image, intensity, blur_radius, light_intensity)
            result_image.save(file_path)

root = tk.Tk()
root.title("Responsive Halation Effect App")

canvas = tk.Canvas(root)
canvas.pack()

controls = ttk.Frame(root)
controls.pack(fill="x", padx=10, pady=5)

open_button = ttk.Button(controls, text="Open Image", command=open_image)
open_button.pack(side="left")

ttk.Label(controls, text="Brightness:").pack(side="left", padx=5)
brightness_scale = ttk.Scale(controls, from_=0.1, to=2, orient="horizontal")
brightness_scale.set(1)
brightness_scale.pack(side="left", padx=5)
brightness_scale.bind("<Motion>", update_image)  # Update image on slider move

ttk.Label(controls, text="Intensity:").pack(side="left", padx=5)
intensity_scale = ttk.Scale(controls, from_=1, to=5, orient="horizontal")
intensity_scale.set(2)
intensity_scale.pack(side="left", padx=5)
intensity_scale.bind("<Motion>", update_image)  # Update image on slider move

ttk.Label(controls, text="Blur Radius:").pack(side="left", padx=5)
blur_scale = ttk.Scale(controls, from_=1, to=20, orient="horizontal")
blur_scale.set(10)
blur_scale.pack(side="left", padx=5)
blur_scale.bind("<Motion>", update_image)  # Update image on slider move

ttk.Label(controls, text="Light Intensity:").pack(side="left", padx=5)
light_intensity_scale = ttk.Scale(controls, from_=0.1, to=3, orient="horizontal")
light_intensity_scale.set(1)
light_intensity_scale.pack(side="left", padx=5)
light_intensity_scale.bind("<Motion>", update_image)  # Update image on slider move

save_button = ttk.Button(controls, text="Save Image", command=save_image)
save_button.pack(side="left", padx=5)

root.mainloop()
