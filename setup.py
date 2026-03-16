import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import cv2
import math
import numpy as np
import csv
import os
from PIL import Image, ImageTk


class MeasurementState:
    """Data model holding all measurement state."""

    def __init__(self):
        self.original_image = None
        self.points_list = []
        self.angles = []
        self.source_mode = "image"  # "image", "camera", "video"
        self.video_capture = None
        self.params = {
            "line_color": (255, 0, 0),  # BGR blue
            "text_color": (255, 0, 0),  # BGR blue
            "line_thickness": 2,
            "point_radius": 5,
            "font_scale": 1.5,
            "font_thickness": 2,
        }

    def add_point(self, x, y):
        self.points_list.append([x, y])
        if len(self.points_list) >= 3 and len(self.points_list) % 3 == 0:
            self.compute_angle()
            return True
        return False

    def compute_angle(self):
        pt1, pt2, pt3 = self.points_list[-3:]
        a = np.array(pt2)
        b = np.array(pt1)
        c = np.array(pt3)
        ba = a - b
        bc = c - b
        norm_product = np.linalg.norm(ba) * np.linalg.norm(bc)
        if norm_product == 0:
            return
        cosine_angle = np.dot(ba, bc) / norm_product
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = math.degrees(np.arccos(cosine_angle))
        angle = round(angle)
        self.angles.append({
            "vertex": pt1,
            "pt2": pt2,
            "pt3": pt3,
            "angle_deg": angle,
        })

    def render_annotations(self, img):
        p = self.params
        color = p["line_color"]
        thickness = p["line_thickness"]
        radius = p["point_radius"]

        for i, pt in enumerate(self.points_list):
            cv2.circle(img, tuple(pt), radius, color, cv2.FILLED)
            group_idx = i // 3
            pos_in_group = i % 3
            if pos_in_group > 0:
                prev_pt = self.points_list[group_idx * 3]
                cv2.line(img, tuple(prev_pt), tuple(pt), color, thickness)

        for a in self.angles:
            cv2.putText(
                img,
                str(a["angle_deg"]),
                (a["vertex"][0] - 40, a["vertex"][1] - 20),
                cv2.FONT_HERSHEY_COMPLEX,
                p["font_scale"],
                p["text_color"],
                p["font_thickness"],
            )

        return img

    def get_annotated_image(self):
        if self.original_image is None:
            return None
        img = self.original_image.copy()
        return self.render_annotations(img)

    def clear(self):
        self.points_list = []
        self.angles = []

    def export_csv(self, filepath):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Vertex_X", "Vertex_Y", "Angle_Degrees"])
            for i, a in enumerate(self.angles, 1):
                writer.writerow([i, a["vertex"][0], a["vertex"][1], a["angle_deg"]])


class AngleMeasurementApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Angle Measurement")
        self.minsize(800, 600)
        self.geometry("1024x768")

        self.state_model = MeasurementState()
        self.params_visible = tk.BooleanVar(value=False)
        self.fit_mode = tk.BooleanVar(value=True)
        self._after_id = None
        self._photo = None
        self._scale = 1.0
        self._offset_x = 0
        self._offset_y = 0
        self.measure_active = True
        self._camera_active = False
        self._video_active = False

        self._setup_styles()
        self._build_menu()
        self._build_toolbar()
        self._build_canvas()
        self._build_params_panel()
        self._build_statusbar()

        # Grid weights: only canvas row/col expands
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Load default image
        self._load_default_image()

        self.protocol("WM_DELETE_WINDOW", self._on_quit)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Blue highlight for all buttons
        style.configure("TButton", padding=6, font=("Segoe UI", 9))
        style.map(
            "TButton",
            background=[("active", "#3B82F6"), ("pressed", "#2563EB")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        # Active toggle button style
        style.configure(
            "Active.TButton",
            background="#3B82F6",
            foreground="white",
            padding=6,
            font=("Segoe UI", 9),
        )
        style.map(
            "Active.TButton",
            background=[("active", "#2563EB"), ("pressed", "#1D4ED8")],
            foreground=[("active", "white"), ("pressed", "white")],
        )

        # Status bar
        style.configure("Status.TLabel", padding=(8, 4), font=("Segoe UI", 9))

        # Parameters panel
        style.configure("Params.TLabelframe", padding=8)
        style.configure("Params.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _build_menu(self):
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image...", command=self._open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Video...", command=self._open_video)
        file_menu.add_separator()
        file_menu.add_command(label="Save Image...", command=self._save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Export CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._on_quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(
            label="Parameters", variable=self.params_visible, command=self._toggle_params
        )
        view_menu.add_checkbutton(
            label="Fit to Window", variable=self.fit_mode, command=self._refresh_display
        )
        menubar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

        # Keyboard shortcuts
        self.bind_all("<Control-o>", lambda e: self._open_image())
        self.bind_all("<Control-s>", lambda e: self._save_image())
        self.bind_all("<Control-q>", lambda e: self._on_quit())

    def _build_toolbar(self):
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=4)

        self.btn_measure = ttk.Button(
            toolbar, text="Measure", style="Active.TButton", command=self._toggle_measure
        )
        self.btn_measure.pack(side="left", padx=2)

        ttk.Button(toolbar, text="Clear", command=self._clear).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Fit", command=self._fit_image).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save", command=self._save_image).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Export CSV", command=self._export_csv).pack(side="left", padx=2)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

        self.btn_camera = ttk.Button(toolbar, text="Camera", command=self._toggle_camera)
        self.btn_camera.pack(side="left", padx=2)

        self.btn_video = ttk.Button(toolbar, text="Video", command=self._toggle_video)
        self.btn_video.pack(side="left", padx=2)

    def _build_canvas(self):
        self.canvas = tk.Canvas(self, bg="#2D2D2D", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=(4, 0), pady=0)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self._refresh_display())

    def _build_params_panel(self):
        self.params_panel = ttk.LabelFrame(self, text="Parameters", style="Params.TLabelframe")

        row = 0

        # Line color
        ttk.Label(self.params_panel, text="Line Color:").grid(row=row, column=0, sticky="w", pady=4)
        self.color_btn = tk.Button(
            self.params_panel,
            width=4,
            bg="#0000FF",
            relief="solid",
            command=self._pick_line_color,
        )
        self.color_btn.grid(row=row, column=1, sticky="w", pady=4, padx=4)
        row += 1

        # Text color
        ttk.Label(self.params_panel, text="Text Color:").grid(row=row, column=0, sticky="w", pady=4)
        self.text_color_btn = tk.Button(
            self.params_panel,
            width=4,
            bg="#0000FF",
            relief="solid",
            command=self._pick_text_color,
        )
        self.text_color_btn.grid(row=row, column=1, sticky="w", pady=4, padx=4)
        row += 1

        # Line thickness
        ttk.Label(self.params_panel, text="Line Thickness:").grid(row=row, column=0, sticky="w", pady=4)
        self.thickness_var = tk.IntVar(value=2)
        ttk.Spinbox(
            self.params_panel, from_=1, to=10, width=5, textvariable=self.thickness_var,
            command=self._on_param_change,
        ).grid(row=row, column=1, sticky="w", pady=4, padx=4)
        row += 1

        # Point radius
        ttk.Label(self.params_panel, text="Point Radius:").grid(row=row, column=0, sticky="w", pady=4)
        self.radius_var = tk.IntVar(value=5)
        ttk.Spinbox(
            self.params_panel, from_=1, to=20, width=5, textvariable=self.radius_var,
            command=self._on_param_change,
        ).grid(row=row, column=1, sticky="w", pady=4, padx=4)
        row += 1

        # Font scale
        ttk.Label(self.params_panel, text="Font Scale:").grid(row=row, column=0, sticky="w", pady=4)
        self.font_scale_var = tk.DoubleVar(value=1.5)
        ttk.Spinbox(
            self.params_panel, from_=0.5, to=5.0, increment=0.5, width=5,
            textvariable=self.font_scale_var, command=self._on_param_change,
        ).grid(row=row, column=1, sticky="w", pady=4, padx=4)
        row += 1

        # Font thickness
        ttk.Label(self.params_panel, text="Font Thickness:").grid(row=row, column=0, sticky="w", pady=4)
        self.font_thickness_var = tk.IntVar(value=2)
        ttk.Spinbox(
            self.params_panel, from_=1, to=5, width=5, textvariable=self.font_thickness_var,
            command=self._on_param_change,
        ).grid(row=row, column=1, sticky="w", pady=4, padx=4)
        row += 1

        # Initially hidden
        # Will be shown via View > Parameters

    def _build_statusbar(self):
        self.statusbar = ttk.Label(
            self, text="Ready", style="Status.TLabel", relief="sunken", anchor="w"
        )
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(4, 0))

    # --- Actions ---

    def _load_default_image(self):
        default_path = os.path.join(os.path.dirname(__file__) or ".", "img", "sample.jpg")
        if os.path.exists(default_path):
            img = cv2.imread(default_path)
            if img is not None:
                self.state_model.original_image = img
                self.state_model.source_mode = "image"
                self._refresh_display()
                self._update_status()

    def _open_image(self):
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"), ("All files", "*.*")],
        )
        if not path:
            return
        self._stop_capture()
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", f"Could not load image:\n{path}")
            return
        self.state_model.original_image = img
        self.state_model.source_mode = "image"
        self.state_model.clear()
        self._refresh_display()
        self._update_status()

    def _open_video(self):
        path = filedialog.askopenfilename(
            title="Open Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")],
        )
        if not path:
            return
        self._stop_capture()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            messagebox.showerror("Error", f"Could not open video:\n{path}")
            return
        self.state_model.video_capture = cap
        self.state_model.source_mode = "video"
        self.state_model.clear()
        self._video_active = True
        self.btn_video.configure(style="Active.TButton")
        self._poll_frame()
        self._update_status()

    def _save_image(self):
        annotated = self.state_model.get_annotated_image()
        if annotated is None:
            return
        result_dir = os.path.join(os.path.dirname(__file__) or ".", "result")
        os.makedirs(result_dir, exist_ok=True)
        path = filedialog.asksaveasfilename(
            title="Save Image",
            initialdir=result_dir,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")],
        )
        if not path:
            return
        cv2.imwrite(path, annotated)
        self._set_status(f"Saved: {os.path.basename(path)}")

    def _export_csv(self):
        if not self.state_model.angles:
            messagebox.showinfo("Export CSV", "No angle measurements to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        self.state_model.export_csv(path)
        self._set_status(f"Exported: {os.path.basename(path)}")

    def _clear(self):
        self.state_model.clear()
        self._refresh_display()
        self._update_status()

    def _fit_image(self):
        self.fit_mode.set(True)
        self._refresh_display()

    def _toggle_measure(self):
        self.measure_active = not self.measure_active
        if self.measure_active:
            self.btn_measure.configure(style="Active.TButton")
        else:
            self.btn_measure.configure(style="TButton")

    def _toggle_camera(self):
        if self._camera_active:
            self._stop_capture()
            return
        self._stop_capture()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open camera.")
            return
        self.state_model.video_capture = cap
        self.state_model.source_mode = "camera"
        self.state_model.clear()
        self._camera_active = True
        self.btn_camera.configure(style="Active.TButton")
        self._poll_frame()
        self._update_status()

    def _toggle_video(self):
        if self._video_active:
            self._stop_capture()
            return
        self._open_video()

    def _stop_capture(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        if self.state_model.video_capture is not None:
            self.state_model.video_capture.release()
            self.state_model.video_capture = None
        self._camera_active = False
        self._video_active = False
        self.btn_camera.configure(style="TButton")
        self.btn_video.configure(style="TButton")

    def _poll_frame(self):
        if self.state_model.video_capture is None:
            return
        ret, frame = self.state_model.video_capture.read()
        if not ret:
            self._stop_capture()
            self._set_status("Capture ended")
            return
        self.state_model.original_image = frame
        self._refresh_display()
        self._update_status()
        self._after_id = self.after(33, self._poll_frame)

    def _toggle_params(self):
        if self.params_visible.get():
            self.params_panel.grid(row=1, column=1, sticky="ns", padx=(0, 4), pady=0)
        else:
            self.params_panel.grid_remove()

    def _pick_line_color(self):
        bgr = self.state_model.params["line_color"]
        initial_rgb = f"#{bgr[2]:02x}{bgr[1]:02x}{bgr[0]:02x}"
        result = colorchooser.askcolor(color=initial_rgb, title="Line Color")
        if result[0] is None:
            return
        r, g, b = [int(c) for c in result[0]]
        self.state_model.params["line_color"] = (b, g, r)  # BGR
        self.color_btn.configure(bg=result[1])
        self._refresh_display()

    def _pick_text_color(self):
        bgr = self.state_model.params["text_color"]
        initial_rgb = f"#{bgr[2]:02x}{bgr[1]:02x}{bgr[0]:02x}"
        result = colorchooser.askcolor(color=initial_rgb, title="Text Color")
        if result[0] is None:
            return
        r, g, b = [int(c) for c in result[0]]
        self.state_model.params["text_color"] = (b, g, r)  # BGR
        self.text_color_btn.configure(bg=result[1])
        self._refresh_display()

    def _on_param_change(self):
        self.state_model.params["line_thickness"] = self.thickness_var.get()
        self.state_model.params["point_radius"] = self.radius_var.get()
        self.state_model.params["font_scale"] = self.font_scale_var.get()
        self.state_model.params["font_thickness"] = self.font_thickness_var.get()
        self._refresh_display()

    def _show_about(self):
        messagebox.showinfo(
            "About",
            "Angle Measurement Tool\n\n"
            "Click 3 points to measure an angle.\n"
            "The angle is calculated at the first point.",
        )

    # --- Display ---

    def _refresh_display(self):
        annotated = self.state_model.get_annotated_image()
        if annotated is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        img_h, img_w = annotated.shape[:2]

        if self.fit_mode.get():
            scale = min(canvas_w / img_w, canvas_h / img_h)
            if scale > 1.0:
                scale = 1.0
        else:
            scale = 1.0

        self._scale = scale
        display_w = int(img_w * scale)
        display_h = int(img_h * scale)
        self._offset_x = (canvas_w - display_w) // 2
        self._offset_y = (canvas_h - display_h) // 2

        # Convert BGR to RGB and resize for display
        rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        if scale != 1.0:
            pil_img = pil_img.resize((display_w, display_h), Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(self._offset_x, self._offset_y, anchor="nw", image=self._photo)

    def _on_canvas_click(self, event):
        if not self.measure_active:
            return
        if self.state_model.original_image is None:
            return

        # Translate canvas coords to original image coords
        orig_x = int((event.x - self._offset_x) / self._scale)
        orig_y = int((event.y - self._offset_y) / self._scale)

        img_h, img_w = self.state_model.original_image.shape[:2]
        if orig_x < 0 or orig_y < 0 or orig_x >= img_w or orig_y >= img_h:
            return

        self.state_model.add_point(orig_x, orig_y)
        self._refresh_display()
        self._update_status()

    # --- Status ---

    def _update_status(self):
        mode = self.state_model.source_mode.capitalize()
        pts = len(self.state_model.points_list)
        angle_str = ""
        if self.state_model.angles:
            angle_str = f" | Last angle: {self.state_model.angles[-1]['angle_deg']}\u00b0"
        self.statusbar.config(text=f"{mode} | Points: {pts}{angle_str}")

    def _set_status(self, text):
        self.statusbar.config(text=text)

    def _on_quit(self):
        self._stop_capture()
        self.destroy()


if __name__ == "__main__":
    app = AngleMeasurementApp()
    app.mainloop()
