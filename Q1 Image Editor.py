""" App Feature:
1. Load an image
2. Display it on the canvas
3. Draw a a rectangle to select a crop area
4. Crop the selected area
5. Resize the cropped image
6. Undo/Redo changes
7. Save the edited image
9. Show status messages
10. Add Keyboard shortcuts"""

#import required libraries for the app
import tkinter as tk
from tkinter import filedialog, messagebox, Scale
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

# defining the main image editor application class
class CenteredImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        # Initialize variables to hold images and cropping details
        self.image = None
        self.original_image = None
        self.cropped_image = None
        self.resized_image = None
        self.rect_start = None
        self.rect_end = None
        self.rect_id = None
        self.undo_stack = []
        self.redo_stack = []
        self.image_path = None

        # The size for the Canvas of image loading
        self.canvas_width = 600
        self.canvas_height = 400

        # Resampling method of handling Pillow's for compatibility
        try:
            self.resample = Image.Resampling.LANCZOS
        except AttributeError:
            self.resample = Image.LANCZOS
            
        # setup user interface and key bindings
        self.setup_ui()
        self.bind_shortcuts()

    def setup_ui(self):
        """Create all UI components: button, canvas, labels, scale"""
        # Frame for button
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, pady=5)

        # Functionality buttons with commands
        load_btn = tk.Button(btn_frame, text="Load Image (Ctrl+O)", command=self.load_image)
        load_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(btn_frame, text="Save Image (Ctrl+S)", command=self.save_image)
        save_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_image)
        reset_btn.pack(side=tk.LEFT, padx=5)

        undo_btn = tk.Button(btn_frame, text="Undo (Ctrl+Z)", command=self.undo)
        undo_btn.pack(side=tk.LEFT, padx=5)

        redo_btn = tk.Button(btn_frame, text="Redo (Ctrl+Y)", command=self.redo)
        redo_btn.pack(side=tk.LEFT, padx=5)

        # Creating Canvas to display images
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="gray",
                               width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Mouse bindings to canvas for cropping image
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Scale widget to resize cropped image
        self.scale = Scale(self.root, from_=10, to=200, orient="horizontal",
                           label="Resize Cropped Image (%)", command=self.resize_image)
        self.scale.set(100)
        self.scale.pack(fill=tk.X, padx=10, pady=5)

        # Creating frame to show original and cropped image thumbnails
        img_frame = tk.Frame(self.root)
        img_frame.pack(fill=tk.BOTH, expand=True)

        self.original_panel = tk.Label(img_frame, text="Original Image")
        self.original_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.cropped_panel = tk.Label(img_frame, text="Cropped/Resized Image")
        self.cropped_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Creating status bar to show current operation information
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var,
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_status("Ready")

    def bind_shortcuts(self):
        """Defining the bind keyboard shortcuts for common actions"""
        self.root.bind("<Control-z>", self.handle_undo)
        self.root.bind("<Control-y>", self.handle_redo)
        self.root.bind("<Control-o>", self.handle_load)
        self.root.bind("<Control-s>", self.handle_save)

    def set_status(self, msg):
        """update the status bar with a message"""
        self.status_var.set(msg)

    def load_image(self):
        """creating image loading funcitonality to load image from device folder and display it to canvas"""
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if path:
            img = cv2.imread(path)
            if img is None:
                messagebox.showerror("Error", "Failed to load image.")
                self.set_status("Failed to load image.")
                return
            self.image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.original_image = self.image.copy()
            self.cropped_image = None
            self.resized_image = None
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.image_path = path
            self.display_image(self.image, self.original_panel, os.path.basename(path))
            self.display_image(np.ones((100, 100, 3), dtype=np.uint8)*220,
                               self.cropped_panel, text="Cropped/Resized Image")
            self.show_on_canvas_centered(self.image)
            self.scale.set(100)
            self.set_status(f"Loaded: {os.path.basename(path)} ({self.image.shape[1]}x{self.image.shape[0]})")

    def reset_image(self):
        """Reset image to its original state"""
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.cropped_image = None
            self.resized_image = None
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.display_image(self.image, self.original_panel,
                               os.path.basename(self.image_path) if self.image_path else "Original Image")
            self.display_image(np.ones((100, 100, 3), dtype=np.uint8)*220,
                               self.cropped_panel, text="Cropped/Resized Image")
            self.show_on_canvas_centered(self.image)
            self.scale.set(100)
            self.set_status("Image reset to original.")

    def show_on_canvas_centered(self, img):
        """Display an image centered within the canvas"""
        img_pil = Image.fromarray(img)
        img_pil.thumbnail((self.canvas_width, self.canvas_height), self.resample)
        img_width, img_height = img_pil.size

        #create a new image with a gray background
        canvas_img = Image.new("RGB", (self.canvas_width, self.canvas_height), (128, 128, 128))
        x = (self.canvas_width - img_width) // 2
        y = (self.canvas_height - img_height) // 2
        
        canvas_img.paste(img_pil, (x, y))
        self.tk_image = ImageTk.PhotoImage(canvas_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        #save image position and size for cropping reference
        self.last_canvas_offset = (x, y)
        self.last_canvas_img_size = (img_width, img_height)
        
    #start drawing crop rectangle
    def on_mouse_down(self, event): 
        if self.image is None:
            return
        self.rect_start = (event.x, event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = None
        
    #darw rectangle dynamically while dragging mouse
    def on_mouse_drag(self, event):
        if self.rect_start:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(
                self.rect_start[0], self.rect_start[1], event.x, event.y,
                outline="red", width=2)

    #finish drawig and crop the image
    def on_mouse_up(self, event):
        if self.rect_start:
            self.rect_end = (event.x, event.y)
            self.crop_image()
            self.rect_start = None
            self.rect_end = None
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = None

    def crop_image(self):
        """Crop the image based on the recatangle selection on canvas"""
        if self.image is not None and self.rect_start and self.rect_end:
            x0, y0 = self.rect_start
            x1, y1 = self.rect_end
            x0, x1 = sorted([x0, x1])
            y0, y1 = sorted([y0, y1])
            offset_x, offset_y = self.last_canvas_offset
            img_w, img_h = self.last_canvas_img_size
            x0_img = max(0, x0 - offset_x)
            y0_img = max(0, y0 - offset_y)
            x1_img = max(0, x1 - offset_x)
            y1_img = max(0, y1 - offset_y)
            x0_img = min(img_w, x0_img)
            x1_img = min(img_w, x1_img)
            y0_img = min(img_h, y0_img)
            y1_img = min(img_h, y1_img)
            if x1_img - x0_img > 1 and y1_img - y0_img > 1:
                orig_h, orig_w = self.image.shape[:2]
                scale_x = orig_w / img_w
                scale_y = orig_h / img_h
                img_x0 = int(x0_img * scale_x)
                img_x1 = int(x1_img * scale_x)
                img_y0 = int(y0_img * scale_y)
                img_y1 = int(y1_img * scale_y)
                img_x0, img_x1 = sorted([max(0, img_x0), min(orig_w, img_x1)])
                img_y0, img_y1 = sorted([max(0, img_y0), min(orig_h, img_y1)])
                cropped = self.image[img_y0:img_y1, img_x0:img_x1]
                self.push_undo(self.resized_image if self.resized_image is not None else self.image)
                self.cropped_image = cropped
                self.resized_image = cropped.copy()
                self.display_image(self.resized_image, self.cropped_panel,
                                   text=f"Cropped ({img_x1-img_x0}x{img_y1-img_y0})")
                self.show_on_canvas_centered(self.resized_image)
                self.scale.set(100)
                self.set_status(f"Cropped region: ({img_x0},{img_y0}) to ({img_x1},{img_y1})")
            else:
                messagebox.showwarning("Warning", "Invalid crop selection.")
                self.set_status("Invalid crop selection.")

    def resize_image(self, value):
        """Resize the cropped image accroding to scale value"""
        if self.cropped_image is not None:
            scale = int(value) / 100.0
            h, w = self.cropped_image.shape[:2]
            new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
            resized = cv2.resize(self.cropped_image, new_size, interpolation=cv2.INTER_AREA)
            self.push_undo(self.resized_image if self.resized_image is not None else self.cropped_image)
            self.resized_image = resized
            self.display_image(resized, self.cropped_panel, text=f"Resized ({new_size[0]}x{new_size[1]})")
            self.show_on_canvas_centered(self.resized_image)
            self.set_status(f"Resized to {new_size[0]}x{new_size[1]}")

    def save_image(self):
        if self.resized_image is not None:
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"),
                           ("JPEG files", "*.jpg;*.jpeg"),
                           ("BMP files", "*.bmp"),
                           ("All files", "*.*")])
            if path:
                img = Image.fromarray(self.resized_image)
                img.save(path)
                messagebox.showinfo("Saved", f"Image saved to {path}")
                self.set_status(f"Image saved: {os.path.basename(path)}")
        else:
            messagebox.showwarning("Warning", "No cropped/resized image to save.")
            self.set_status("No cropped/resized image to save.")

    def display_image(self, img, panel, text=""):
        """ Conver image to a Tkinter-compatible image and display on a label"""
        img_pil = Image.fromarray(img)
        img_pil.thumbnail((300, 300), self.resample)
        img_tk = ImageTk.PhotoImage(img_pil)
        panel.config(image=img_tk, text=text)
        panel.image = img_tk  # Keep reference

    def save_image(self):
        """Save the currently resized (or cropped) image"""
        if self.resized_image is None:
            messagebox.showwarning("Warning", "No cropped or resized image to save.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png"),
                                                       ("JPEG", "*.jpg"),
                                                       ("Bitmap", "*.bmp"),
                                                       ("TIFF", "*.tiff")])
        if path:
            cv2.imwrite(path, cv2.cvtColor(self.resized_image, cv2.COLOR_RGB2BGR))
            self.set_status(f"Saved image: {os.path.basename(path)}")
            
    def push_undo(self, img):
        if img is not None:
            self.undo_stack.append(img.copy())
            if len(self.undo_stack) > 30:
                self.undo_stack.pop(0)
            self.redo_stack.clear()

    def undo(self, event=None):
        """ undo the last crop operation"""
        if self.undo_stack:
            if self.resized_image is not None:
                self.redo_stack.append(self.resized_image.copy())
            img = self.undo_stack.pop()
            self.resized_image = img.copy()
            self.cropped_image = img.copy()
            self.display_image(self.resized_image, self.cropped_panel, text="Undo")
            self.show_on_canvas_centered(self.resized_image)
            self.scale.set(100)
            self.set_status("Undo performed.")
        else:
            self.set_status("Nothing to undo.")

    def redo(self, event=None):
        """ Redo the last undone opearation"""
        if self.redo_stack:
            if self.resized_image is not None:
                self.undo_stack.append(self.resized_image.copy())
            img = self.redo_stack.pop()
            self.resized_image = img.copy()
            self.cropped_image = img.copy()
            self.display_image(self.resized_image, self.cropped_panel, text="Redo")
            self.show_on_canvas_centered(self.resized_image)
            self.scale.set(100)
            self.set_status("Redo performed.")
        else:
            self.set_status("Nothing to redo.")

    # Shortcut handler for undo
    def handle_undo(self, event=None):
        self.undo()

    # Shortcut handler for undo
    def handle_redo(self, event=None):
        self.redo()

    # Shortcut handler for loading image
    def handle_load(self, event=None):
        self.load_image()

    # Shortcut handler for saving image
    def handle_save(self, event=None):
        self.save_image()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CenteredImageEditorApp(root)
        root.mainloop()
    except ImportError as e:
        messagebox.showerror(
            "Dependency Error",
            "A required library is missing:\n\n{}\n\n"
            "Install missing dependencies with:\n"
            "pip install pillow opencv-python numpy".format(e)
        )
    except Exception as ex:
        messagebox.showerror("Error", str(ex))
