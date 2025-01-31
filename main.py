import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageDraw, ImageTk
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=40, radius=8, bg="#7ec8e3", fg="white", hover_bg="#5aa4c2"):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"), highlightthickness=0)
        self.command = command
        self.text = text
        self.radius = radius
        self.width = width
        self.height = height
        self.bg_color = bg
        self.fg_color = fg
        self.hover_bg = hover_bg
        self.default_bg = bg

        self.draw_button()

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def draw_button(self):
        self.delete("all")
        self.create_rounded_rectangle(0, 0, self.width, self.height, radius=self.radius, fill=self.bg_color, outline=self.bg_color)
        self.create_text(self.width // 2, self.height // 2, text=self.text, fill=self.fg_color, font=("Helvetica", 12, "bold"))

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        self.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, style=tk.PIESLICE, **kwargs)

        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.bg_color = self.hover_bg
        self.draw_button()

    def on_leave(self, event):
        self.bg_color = self.default_bg
        self.draw_button()


class DigitalWhiteboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Digital Whiteboard")

        self.root.configure(bg='#f4f4f4')

        self.sidebar = tk.Frame(root, width=160, bg='#2C3E50', padx=20, pady=20)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600, bd=2, relief=tk.SOLID)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.color_button = RoundedButton(self.sidebar, text="Choose Color", command=self.choose_color, bg="#D90012", fg="white", hover_bg="#b3000e")
        self.color_button.pack(pady=12)

        self.eraser_button = RoundedButton(self.sidebar, text="Eraser", command=self.use_eraser, bg="#001489", fg="white", hover_bg="#001066")
        self.eraser_button.pack(pady=12)

        self.clear_button = RoundedButton(self.sidebar, text="Clear Board", command=self.clear_canvas, bg="#F2A800", fg="white", hover_bg="#d18e00")
        self.clear_button.pack(pady=12)

        self.save_button = RoundedButton(self.sidebar, text="Save as PNG", command=self.save_canvas, bg="#00ABC2", fg="white", hover_bg="#008fa3")
        self.save_button.pack(pady=12)

        self.line_width_label = tk.Label(self.sidebar, text="Width", font=("Helvetica", 14), bg="#2C3E50", fg="white")
        self.line_width_label.pack(pady=6)

        self.line_width_scale = tk.Scale(self.sidebar, from_=1, to=100, orient=tk.HORIZONTAL, command=self.update_line_width, sliderlength=15, length=75, bg="#34495E", fg="white", troughcolor="#BDC3C7")
        self.line_width_scale.set(5)
        self.line_width_scale.pack(pady=6)

        self.image_size_label = tk.Label(self.sidebar, text="Image Size", font=("Helvetica", 14), bg="#2C3E50", fg="white")
        self.image_size_label.pack(pady=6)

        self.image_size_scale = tk.Scale(self.sidebar, from_=10, to=100, orient=tk.HORIZONTAL, command=self.update_image_size, sliderlength=15, length=75, bg="#34495E", fg="white", troughcolor="#BDC3C7")
        self.image_size_scale.set(10)
        self.image_size_scale.pack(pady=6)

        self.pen_color = "black"
        self.old_x = None
        self.old_y = None
        self.eraser_on = False
        self.shape = None
        self.line_width = 3
        self.image = Image.new("RGB", (800, 600), "white")
        self.image_draw = ImageDraw.Draw(self.image)
        self.photo_image = None
        self.uploaded_image = None
        self.uploaded_image_id = None
        self.image_size = 100
        self.is_moving_image = False

        self.placeholder_text = self.canvas.create_text(400, 300, text="You can drag and drop any picture here.", font=("Helvetica", 16), fill="#cccccc")

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.drop_image)

        self.canvas.bind('<B1-Motion>', self.on_draw)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

    def update_line_width(self, value):
        self.line_width = int(value)

    def update_image_size(self, value):
        self.image_size = int(value)
        if self.uploaded_image:
            self.resize_uploaded_image()

    def choose_color(self):
        color = colorchooser.askcolor(color=self.pen_color)[1]
        if color:
            self.pen_color = color
            self.eraser_on = False

    def use_eraser(self):
        self.pen_color = "white"
        self.eraser_on = True

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (800, 600), "white")
        self.image_draw = ImageDraw.Draw(self.image)
        self.uploaded_image = None
        self.uploaded_image_id = None
        self.placeholder_text = self.canvas.create_text(400, 300, text="You can drag and drop any picture here.", font=("Helvetica", 16), fill="#cccccc")

    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image.save(file_path)
            print(f"Canvas saved as {file_path}!")

    def drop_image(self, event):
        file_path = event.data
        self.upload_image(file_path)

    def upload_image(self, file_path):
        try:
            img = Image.open(file_path)
            self.uploaded_image = img
            self.resize_uploaded_image()
            print(f"Image uploaded successfully: {file_path}")
            self.canvas.delete(self.placeholder_text)
        except Exception as e:
            error_message = f"Error uploading image: {str(e)}"
            messagebox.showerror("Error", error_message)
            print(error_message)

    def resize_uploaded_image(self):
        if self.uploaded_image:
            width = int(self.uploaded_image.width * (self.image_size / 100))
            height = int(self.uploaded_image.height * (self.image_size / 100))

            resized_img = self.uploaded_image.copy()
            resized_img.thumbnail((width, height), Image.LANCZOS)

            self.photo_image = ImageTk.PhotoImage(resized_img)

            if self.uploaded_image_id:
                self.canvas.delete(self.uploaded_image_id)

            self.uploaded_image_id = self.canvas.create_image(400, 300, image=self.photo_image,
                                                              anchor=tk.CENTER)
            self.canvas.tag_bind(self.uploaded_image_id, '<Button-1>', self.start_move_image)
            self.canvas.tag_bind(self.uploaded_image_id, '<B1-Motion>', self.move_image)
            self.canvas.tag_bind(self.uploaded_image_id, '<ButtonRelease-1>', self.stop_move_image)

    def start_move_image(self, event):
        self.is_moving_image = True

    def move_image(self, event):
        if self.uploaded_image_id and self.is_moving_image:
            self.canvas.coords(self.uploaded_image_id, event.x, event.y)

    def stop_move_image(self, event):
        self.is_moving_image = False

    def on_draw(self, event):
        if self.placeholder_text:
            self.canvas.delete(self.placeholder_text)
            self.placeholder_text = None

        if not self.is_moving_image:
            if self.shape == "circle":
                x, y = event.x, event.y
                self.canvas.create_oval(x - self.line_width, y - self.line_width, x + self.line_width, y + self.line_width,
                                        fill=self.pen_color, outline="")
                self.image_draw.ellipse(
                    [x - self.line_width, y - self.line_width, x + self.line_width, y + self.line_width],
                    fill=self.pen_color)
            elif self.shape == "rectangle":
                x, y = event.x, event.y
                self.canvas.create_rectangle(x - self.line_width * 2, y - self.line_width, x + self.line_width * 2,
                                             y + self.line_width, fill=self.pen_color, outline="")
                self.image_draw.rectangle(
                    [x - self.line_width * 2, y - self.line_width, x + self.line_width * 2, y + self.line_width],
                    fill=self.pen_color)
            else:
                if self.old_x and self.old_y:
                    self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                            width=self.line_width, fill=self.pen_color, capstyle=tk.ROUND, smooth=True)
                    self.image_draw.line([self.old_x, self.old_y, event.x, event.y], fill=self.pen_color,
                                         width=self.line_width)
                self.old_x = event.x
                self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None
        self.shape = None


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    whiteboard = DigitalWhiteboard(root)
    root.mainloop()