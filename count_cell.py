import cv2
import os
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog, BooleanVar


class CellCounter:
    def __init__(self, master) -> None:
        self.master = master
        self.master.title("Cell Counter")

        # Maximize the window
        self.master.state("zoomed")

        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Left frame for the image
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", padx=(0, 20), fill="both", expand=True)

        # Add image name label
        self.image_name_label = ctk.CTkLabel(
            self.left_frame,
            text="No image loaded",
            font=("Arial", 16),
            text_color="black",
        )
        self.image_name_label.pack(pady=(10, 5))

        # Placeholder for the canvas
        self.canvas = None

        # Right frame for controls
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", padx=(20, 0), fill="y")

        self.load_button = ctk.CTkButton(
            self.right_frame,
            text="Load Image",
            command=self.load_image_dialog,
            width=250,
            height=60,
            font=("Arial", 18),
        )
        self.load_button.pack(pady=(0, 20))

        self.cell_count = 0
        self.marks = []

        self.label = ctk.CTkLabel(
            self.right_frame, text=f"Cell Count: {self.cell_count}", font=("Arial", 24)
        )
        self.label.pack(pady=(20, 10))

        self.instruction_label = ctk.CTkLabel(
            self.right_frame,
            text="Press Delete or Backspace\nto remove the last mark",
            font=("Arial", 18),
            text_color="gray",
        )
        self.instruction_label.pack(pady=(10, 20))

        # Add checkbox for grid display
        self.show_grid_var = BooleanVar(value=True)
        self.show_grid_checkbox = ctk.CTkCheckBox(
            self.right_frame,
            text="Show Grid",
            variable=self.show_grid_var,
            command=self.toggle_grid,
            font=("Arial", 18),
        )
        self.show_grid_checkbox.pack(pady=(0, 20))

        self.save_button = ctk.CTkButton(
            self.right_frame,
            text="Save Image",
            command=self.save_image,
            width=250,
            height=60,
            font=("Arial", 18),
        )
        self.save_button.pack(pady=20)

        self.save_label = ctk.CTkLabel(
            self.right_frame,
            text="",
            font=("Arial", 18),
            text_color="green",
            wraplength=250,
        )
        self.save_label.pack(pady=10)

        self.error_label = None

        self.master.bind("<Delete>", self.remove_previous_mark)
        self.master.bind("<BackSpace>", self.remove_previous_mark)

    def load_image_dialog(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, img_path) -> None:
        self.img_path = img_path
        try:
            self.image = cv2.imread(self.img_path)
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.image_pil = Image.fromarray(self.image_rgb)

            self.image_tk = ImageTk.PhotoImage(self.image_pil)

            if self.canvas:
                self.canvas.destroy()

            self.canvas = ctk.CTkCanvas(
                self.left_frame,
                width=self.image_tk.width(),
                height=self.image_tk.height(),
            )
            self.canvas.pack(padx=10, pady=(5, 10), expand=True)
            self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)

            # Update image name label
            image_name = os.path.basename(self.img_path)
            self.image_name_label.configure(text=image_name)

            self.canvas.bind("<Button-1>", self.add_mark)

            # Reset cell count and marks
            self.cell_count = 0
            self.marks = []
            self.label.configure(text=f"Cell Count: {self.cell_count}")
            self.save_label.configure(text="")

            # Ensure grid is drawn if checkbox is checked
            if self.show_grid_var.get():
                self.draw_grid()

        except Exception as e:
            self.show_error(f"Error loading image: {str(e)}")

    def show_error(self, message) -> None:
        if self.error_label:
            self.error_label.destroy()  # Remove existing error message if any

        self.error_label = ctk.CTkLabel(
            self.right_frame,
            text=message,
            font=("Arial", 18),
            text_color="red",
            wraplength=250,
        )
        self.error_label.pack(pady=20)

    def draw_grid(self):
        # Remove existing grid lines
        if self.canvas:
            self.canvas.delete("grid_line")

        if self.show_grid_var.get() and self.canvas:
            for i in range(0, self.image_tk.width(), 100):
                self.canvas.create_line(
                    [(i, 0), (i, self.image_tk.height())],
                    fill="black",
                    width=1,
                    tags="grid_line",
                )
            for i in range(0, self.image_tk.height(), 100):
                self.canvas.create_line(
                    [(0, i), (self.image_tk.width(), i)],
                    fill="black",
                    width=1,
                    tags="grid_line",
                )

    def toggle_grid(self):
        if self.canvas:
            self.draw_grid()

    def add_mark(self, event) -> None:
        self.cell_count += 1
        x, y = event.x, event.y
        if self.canvas:
            mark = self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8, outline="red2", width=2
            )
            self.marks.append((mark, x, y))
            self.label.configure(text=f"Cell Count: {self.cell_count}")

    def remove_previous_mark(self) -> None:
        if self.cell_count > 0:
            self.cell_count -= 1
            mark, _, _ = self.marks.pop()
            if self.canvas:
                self.canvas.delete(mark)
                self.label.configure(text=f"Cell Count: {self.cell_count}")

    def save_image(self) -> None:
        if not hasattr(self, "img_path"):
            self.show_error("No image loaded")
            return

        output_image = self.image_pil.copy()
        draw = ImageDraw.Draw(output_image)
        for _, x, y in self.marks:
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), outline="red", width=2)

        num_cells = len(self.marks)

        if num_cells == 0:
            self.show_error("No cells marked")
            return

        img_folder, img_name = os.path.split(self.img_path)
        img_name, img_ext = os.path.splitext(img_name)
        save_path = os.path.join(
            img_folder, f"{img_name}_cell_count_{num_cells}{img_ext}"
        )
        output_image.save(save_path, quality=100, subsampling=0)

        self.save_label.configure(text=f"Image saved to:\n{save_path}")
        print(f"Image saved to {save_path}")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Use system theme
    ctk.set_default_color_theme("blue")  # Set theme color

    root = ctk.CTk()
    app = CellCounter(root)
    root.mainloop()
