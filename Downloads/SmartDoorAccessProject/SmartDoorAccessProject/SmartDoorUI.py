import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from SmartDoorAccessSystem380 import (
    create_db, add_face_to_db, delete_face, load_encodings,
    get_image_from_camera, recognize
)

def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

create_db()

# Create the main window
app = ttk.Window(themename="pulse")  # or "yeti", "flatly", "pulse"

app.title("Smart Door Access System")
center_window(app, 400, 350)
app.resizable(False, False)

# Logo
try:
    logo_img = Image.open("logo.png")
    logo_img = logo_img.resize((100, 100))
    logo = ImageTk.PhotoImage(logo_img)
    ttk.Label(app, image=logo).pack(pady=10)
except Exception:
    pass  # Skip if logo not found

# Title
ttk.Label(app, text="Smart Door Access System", font=("Segoe UI", 16, "bold")).pack(pady=10)

# Buttons
ttk.Button(app, text="Admin", width=25, bootstyle="primary", command=lambda: open_admin_panel(app)).pack(pady=10)
ttk.Button(app, text="User", width=25, bootstyle="primary", command=lambda: open_user_panel(app)).pack(pady=10)



def open_admin_panel(parent):
    pwd = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")
    if pwd == None:
        return
    elif pwd == "admin123":
        admin_panel(parent)
    else:
        messagebox.showerror("Access Denied", "Incorrect password.")


def open_user_panel(parent):
    user_panel(parent)


def admin_panel(parent):
    win = ttk.Toplevel(parent)
    win.title("Admin Panel")
    center_window(win, 350, 300)

    def add_face():
        name = simpledialog.askstring("Add Face", "Enter name:")
        if not name:
            return
        path = filedialog.askopenfilename(title="Select image file")
        if path:
            add_face_to_db(name, path)
            messagebox.showinfo("Success", f"{name} added to DB.")

    def delete_face_ui():
        name = simpledialog.askstring("Delete Face", "Enter name:")
        if name:
            delete_face(name)
            messagebox.showinfo("Deleted", f"Deleted all records for '{name}'")

    def view_faces():
        names, _ = load_encodings()
        if names:
            messagebox.showinfo("Stored Faces", "\n".join(set(names)))
        else:
            messagebox.showinfo("No Data", "No faces found in DB.")

    ttk.Label(win, text="Admin Panel", font=("Segoe UI", 14, "bold")).pack(pady=10)
    ttk.Button(win, text="Add Face to DB", width=25, bootstyle="success", command=add_face).pack(pady=5)
    ttk.Button(win, text="Delete Face", width=25, bootstyle="danger", command=delete_face_ui).pack(pady=5)
    ttk.Button(win, text="View All Stored Names", width=25, bootstyle="info", command=view_faces).pack(pady=5)
    ttk.Button(win, text="Close", width=25, bootstyle="secondary", command=win.destroy).pack(pady=10)


def user_panel(parent):
    win = ttk.Toplevel(parent)
    win.title("User Panel")
    center_window(win, 350, 250)
    win.resizable(False, False)

    def recognize_from_file():
        path = filedialog.askopenfilename(title="Select image file")
        if path:
            result = recognize(path)
            messagebox.showinfo("Recognition Result", result)

    def recognize_from_camera():
        img_path = get_image_from_camera()
        if img_path:
            result = recognize(img_path)
            messagebox.showinfo("Recognition Result", result)

    ttk.Label(win, text="User Panel", font=("Segoe UI", 14, "bold")).pack(pady=10)
    ttk.Button(win, text="Upload Image File", width=25, bootstyle="primary", command=recognize_from_file).pack(pady=5)
    ttk.Button(win, text="Use Webcam", width=25, bootstyle="primary", command=recognize_from_camera).pack(pady=5)
    ttk.Button(win, text="Close", width=25, bootstyle="secondary", command=win.destroy).pack(pady=10)


app.mainloop()
