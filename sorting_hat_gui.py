from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class SortingHatGUI:
    _instance = None

    def __new__(cls, master=None):
        if cls._instance is None:
            cls._instance = super(SortingHatGUI, cls).__new__(cls)
            cls._instance.init(master)
        return cls._instance

    def init(self, master):
        self.master = master
        self.root = master
        master.title("Hogwarts Sorting Hat")
        master.state('zoomed')

        self.canvas = tk.Canvas(master, bg=master.cget('bg'), highlightthickness=0)
        self.canvas.pack(pady=20, fill=tk.BOTH, expand=True)

        self.gif_label = tk.Label(master)
        self.gif_label.pack(expand=True, fill=tk.BOTH)

        self.image_label = tk.Label(master)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        self.load_gif()

        self.canvas.bind("<Configure>", self.on_canvas_resize)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("GUI has not been initialized")
        return cls._instance

    def load_gif(self):
        self.gif = Image.open("assets/sorting_hat.gif")
        self.gif_frames = []
        
        window_width = self.master.winfo_screenwidth()
        window_height = self.master.winfo_screenheight()
        
        new_size = int(min(window_width, window_height) * 0.8)
        
        try:
            while True:
                resized_frame = self.gif.copy()
                resized_frame.thumbnail((new_size, new_size), Image.LANCZOS)
                
                photo = ImageTk.PhotoImage(resized_frame)
                self.gif_frames.append(photo)
                
                self.gif.seek(len(self.gif_frames))
        except EOFError:
            pass

    def play_gif(self):
        self.gif_index = 0
        self.after_id = self.master.after(0, self.animate_gif)

    def animate_gif(self):
        if self.gif_index < len(self.gif_frames):
            self.gif_label.config(image=self.gif_frames[self.gif_index])
            self.gif_index += 1
        else:
            self.gif_index = 0
        self.after_id = self.master.after(50, self.animate_gif)

    def stop_gif(self):
        if hasattr(self, 'after_id'):
            self.master.after_cancel(self.after_id)
        self.gif_label.config(image='')

    def display_images(self, image_paths):
        self.stop_gif()
        self.gif_label.pack_forget()
        
        if hasattr(self, 'image_frame'):
            self.image_frame.destroy()
        
        self.image_frame = tk.Frame(self.master)
        self.image_frame.pack(expand=True, fill=tk.BOTH)
        
        rows = 2
        cols = 2
        for i in range(rows):
            self.image_frame.grid_rowconfigure(i, weight=1)
        for j in range(cols):
            self.image_frame.grid_columnconfigure(j, weight=1)

        self.photo_images = []

        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path)
            img = img.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.photo_images.append(photo)

            label = tk.Label(self.image_frame, image=photo)
            label.grid(row=i//cols, column=i%cols, padx=10, pady=10, sticky="nsew")

    def hide_images(self):
        if hasattr(self, 'image_frame'):
            self.image_frame.destroy()
        self.gif_label.pack(expand=True, fill=tk.BOTH)
        self.play_gif()

    def update_label(self, text):
        display_text = text.replace("Aaliyah", "Aliya").replace("Anora", "Honora")
        
        self.last_text = display_text
        self.canvas.delete("all")
        
        font = tkfont.Font(family="Harry P", size=72)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        words = display_text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            width = font.measure(test_line)
            if width <= canvas_width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        y = canvas_height / 2 - (len(lines) * font.metrics()['linespace']) / 2
        
        for line in lines:
            x = canvas_width / 2
            
            for x_offset in [-1, 0, 1]:
                for y_offset in [-1, 0, 1]:
                    self.canvas.create_text(x+x_offset, y+y_offset, text=line, 
                                            font=font, fill="black", anchor="center")
            
            self.canvas.create_text(x, y, text=line, font=font, 
                                    fill="white", anchor="center")
            
            y += font.metrics()['linespace']

    def on_canvas_resize(self, event):
        if hasattr(self, 'last_text'):
            self.update_label(self.last_text)

    def stop_progress(self):
        pass

    def close_window(self):
        self.root.quit()
        self.root.destroy()

    def set_background_color(self, color):
        self.master.configure(bg=color)
        self.canvas.configure(bg=color)

    def reset_background(self):
        original_bg = self.master.cget('bg')
        self.master.configure(bg=original_bg)
        self.canvas.configure(bg=original_bg)

    def display_image(self, image_path):
        self.stop_gif()
        self.gif_label.pack_forget()
        
        image = Image.open(image_path)
        image = self.scale_image(image, 0.6)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.image_label.pack(expand=True, fill=tk.BOTH)

    def hide_image(self):
        self.image_label.pack_forget()
        self.gif_label.pack(expand=True, fill=tk.BOTH)
        self.play_gif()

    def scale_image(self, image, multiplier=0.8):
        window_width = self.master.winfo_screenwidth()
        window_height = self.master.winfo_screenheight()
        
        max_width = int(window_width * multiplier)
        max_height = int(window_height * multiplier)
        
        ratio = min(max_width/image.width, max_height/image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size, Image.LANCZOS)
