import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=40, radius=15, **kwargs):
        super().__init__(parent, width=width, height=height, bg=kwargs.get("bg", "#7ec8e3"), highlightthickness=0)
        self.command = command
        self.text = text
        self.radius = radius
        self.width = width
        self.height = height
        self.bg_color = kwargs.get("bg", "#7ec8e3")
        self.fg_color = kwargs.get("fg", "#ffffff")
        self.bg_rgba = kwargs.get("bg", "#7ec8e3") + 'FF'

        self.create_rounded_rectangle(0, 0, width, height, radius=self.radius, fill=self.bg_color, outline=self.bg_color)

        self.text_id = self.create_text(width // 2, height // 2, text=self.text, fill=self.fg_color, font=("Helvetica", 12, "bold"))

        self.bind("<Button-1>", self.on_click)
        self.bind("<Leave>", self.on_leave)

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

    def on_leave(self, event):
        self.configure(bg=self.bg_color)

class DigitalWhiteboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Digital Whiteboard")

        self.root.configure(bg='#f4f4f4')

        self.sidebar = tk.Frame(root, width=160, bg='#2C3E50', padx=20, pady=20)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600, bd=2, relief=tk.SOLID)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.color_button = RoundedButton(self.sidebar, text="Choose Color", command=self.choose_color, bg="#D90012", fg="white")
        self.color_button.pack(pady=12)

        self.eraser_button = RoundedButton(self.sidebar, text="Eraser", command=self.use_eraser, bg="#001489", fg="white")
        self.eraser_button.pack(pady=12)

        self.clear_button = RoundedButton(self.sidebar, text="Clear Board", command=self.clear_canvas, bg="#F2A800", fg="white")
        self.clear_button.pack(pady=12)

        self.save_button = RoundedButton(self.sidebar, text="Save as PNG", command=self.save_canvas, bg="#00ABC2", fg="white")
        self.save_button.pack(pady=12)

        self.upload_button = RoundedButton(self.sidebar, text="Upload Image", command=self.upload_image, bg="#FFEC2D", fg="white")
        self.upload_button.pack(pady=12)

        self.line_width_label = tk.Label(self.sidebar, text="Width", font=("Helvetica", 14), bg="#2C3E50", fg="white")
        self.line_width_label.pack(pady=0)

        self.line_width_scale = tk.Scale(self.sidebar, from_=1, to=100, orient=tk.HORIZONTAL, command=self.update_line_width, sliderlength=15, length=75, bg="#34495E", fg="white", troughcolor="#BDC3C7")
        self.line_width_scale.set(3)
        self.line_width_scale.pack(pady=6)

        self.pen_color = "black"
        self.old_x = None
        self.old_y = None
        self.eraser_on = False
        self.shape = None
        self.line_width = 3
        self.image = Image.new("RGB", (800, 600), "white")
        self.image_draw = ImageDraw.Draw(self.image)
        self.photo_image = None

        self.canvas.bind('<B1-Motion>', self.on_draw)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

    def update_line_width(self, value):
        self.line_width = int(value)

    def choose_color(self):
        color = askcolor(color=self.pen_color)[1]
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

    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image.save(file_path)
            print(f"Canvas saved as {file_path}!")

    def upload_image(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
            if not file_path:
                return

            img = Image.open(file_path)
            img = img.resize((800, 600), Image.ANTIALIAS)
            self.image.paste(img)
            self.photo_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
        except Exception as e:
            print(f"Error uploading image: {e}")

    def on_draw(self, event):
        if self.shape == "circle":
            x, y = event.x, event.y
            self.canvas.create_oval(x-self.line_width, y-self.line_width, x+self.line_width, y+self.line_width, fill=self.pen_color, outline="")
            self.image_draw.ellipse([x-self.line_width, y-self.line_width, x+self.line_width, y+self.line_width], fill=self.pen_color)
        elif self.shape == "rectangle":
            x, y = event.x, event.y
            self.canvas.create_rectangle(x-self.line_width*2, y-self.line_width, x+self.line_width*2, y+self.line_width, fill=self.pen_color, outline="")
            self.image_draw.rectangle([x-self.line_width*2, y-self.line_width, x+self.line_width*2, y+self.line_width], fill=self.pen_color)
        else:
            if self.old_x and self.old_y:
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                        width=self.line_width, fill=self.pen_color, capstyle=tk.ROUND, smooth=True)
                self.image_draw.line([self.old_x, self.old_y, event.x, event.y], fill=self.pen_color, width=self.line_width)
            self.old_x = event.x
            self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None
        self.shape = None

if __name__ == "__main__":
    root = tk.Tk()
    whiteboard = DigitalWhiteboard(root)
    root.mainloop()
