import tkinter as tk
from tkinter import ttk, filedialog
import os
from PIL import Image, ImageTk

class ImageCaptionApp:
    def __init__(self, root):
        self.captions = []
        self.images = []
        self.root = root
        self.root.title("Image Captioning App")
        self.root.withdraw()

        # Set initial number of columns
        self.num_columns = 3
        self.image_widgets = []
        self.entry_widgets = []
        self.images_loaded = False

        # Prompt the user to select a directory
        self.directory = filedialog.askdirectory(title="Select Image Directory")
        if not self.directory:
            self.root.destroy()
            return

        self.root.deiconify()
        self.root.title(f"Image Captioning App - {self.directory}")

        self.root.geometry("800x600")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create the main layout frame with a canvas and scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(sticky='nsew')
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.scrollbar = tk.Scrollbar(self.main_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame within the canvas which will be scrolled with the scrollbar
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.scrollable_frame.columnconfigure(1, weight=1)

        # Bind the canvas to the frame resize event
        self.root.bind('<Configure>', self.on_root_configure)

        # Load images and captions
        self.load_images_and_captions()

        # Display the images and captions
        self.display_images_and_captions()

    def load_images_and_captions(self):
        # Load all image files and corresponding caption files
        for file in os.listdir(self.directory):
            if file.endswith(".jpg") or file.endswith(".png"):
                image_path = os.path.join(self.directory, file)
                caption_path = os.path.splitext(image_path)[0] + ".txt"
                self.images.append(image_path)
                self.captions.append(caption_path)

    def on_root_configure(self, event):
        # Resize the canvas' window to the new width
        canvas_width = self.root.winfo_width()
        self.canvas.itemconfig('scrollable_frame', width=canvas_width)
        self.adjust_grid_columns(canvas_width)

    def adjust_grid_columns(self, width):
        # Calculate the number of columns based on the width
        new_num_columns = max(1, width // 256)  # assuming each image thumbnail is 256px wide
        if new_num_columns != self.num_columns:
            self.num_columns = new_num_columns
            if self.images_loaded:  # Only adjust if images have been loaded
                self.display_images_and_captions()

    def display_images_and_captions(self):
        self.images_loaded = True
        for widgets in self.image_widgets + self.entry_widgets:
            widgets.destroy()
        self.image_widgets.clear()
        self.entry_widgets.clear()

        self.scrollable_frame.columnconfigure(tuple(range(self.num_columns)), weight=1)

        for idx, (image_path, caption_path) in enumerate(zip(self.images, self.captions)):
            row = idx // self.num_columns
            column = idx % self.num_columns

            img = Image.open(image_path)
            img.thumbnail((256, 256))
            img = ImageTk.PhotoImage(img)

            label = ttk.Label(self.scrollable_frame, image=img)
            label.image = img
            label.grid(row=row * 2, column=column, padx=5, pady=5, sticky='nsew')
            self.image_widgets.append(label)

            text_var = tk.StringVar()
            if os.path.exists(caption_path):
                with open(caption_path, "r") as f:
                    text_var.set(f.read())
            text_entry = ttk.Entry(self.scrollable_frame, textvariable=text_var)
            text_entry.grid(row=row * 2 + 1, column=column, padx=5, pady=5, sticky='ew')
            self.entry_widgets.append(text_entry)

            # Save caption on change
            text_var.trace("w", lambda name, index, mode, sv=text_var, cp=caption_path: self.save_caption(sv, cp))

    def save_caption(self, string_var, caption_path):
        with open(caption_path, "w") as f:
            f.write(string_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCaptionApp(root)
    root.mainloop()
