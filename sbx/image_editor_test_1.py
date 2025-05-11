from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance

# Initialize the main window
root = Tk()
root.title("Image Editor")
root.state('zoomed')

C1 = "#FDF1F5"  #PETAL WHITE
C2 = '#EE8E46'  #SUNSET ORANGE
root.config(bg=C1)

# Global variables
img = None
tk_img = None
history = []
redo_stack = []

# Main frame
main_frame = Frame(root, bg=C2)
main_frame.pack(fill=BOTH, expand=True)

# Left frame (for canvas)
left_frame = Frame(main_frame, bg="BLACK")
left_frame.pack(side=LEFT, expand=True, fill=BOTH)

# Right frame (for buttons)
right_frame = Frame(main_frame, bg=C2)
right_frame.pack(side=RIGHT, fill=Y, padx=20, pady=20)

# Canvas for displaying images
canvas = Canvas(left_frame, bg=C1)
canvas.pack(fill=BOTH, expand=True)
img_container = None

# Function to update the display with the current image
def update_display(image):
    global tk_img, img_container
    canvas.delete("all")  # Clear the canvas

    # Get canvas dimensions (with fallback values)
    screen_w = canvas.winfo_width() or 800
    screen_h = canvas.winfo_height() or 600

    # Resize the image to fit the canvas while maintaining aspect ratio
    display_img = image.copy()
    if image.width > screen_w or image.height > screen_h:
        ratio = min(screen_w / image.width, screen_h / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        display_img = image.resize(new_size, Image.Resampling.LANCZOS)  # Updated line

    # Convert the image to a Tkinter-compatible format
    tk_img = ImageTk.PhotoImage(display_img)

    # Calculate the position to center the image on the canvas
    x = (screen_w - display_img.width) // 2
    y = (screen_h - display_img.height) // 2

    # Display the image on the canvas
    img_container = canvas.create_image(x, y, anchor=NW, image=tk_img)

    # Update the scroll region to include the entire image
    canvas.config(scrollregion=canvas.bbox(ALL))

# Function to save the current state to history
def save_history():
    if img:
        history.append(img.copy())
        if len(history) > 20:
            history.pop(0)

# Function to open an image
def open_img():
    global img, tk_img, history, redo_stack
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            img = Image.open(file_path)
            save_history()
            redo_stack.clear()
            update_display(img)  # Update the display immediately
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

# Function to save the current image
def save_img():
    if img:
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            img.save(file_path)

# Function to remove the current image
def remove_img():
    global img, tk_img, history, redo_stack
    img = None
    tk_img = None
    history.clear()
    redo_stack.clear()
    canvas.delete("all")

# Function to undo the last action
def undo_action():
    global img
    if history:
        redo_stack.append(img.copy())
        img = history.pop()
        update_display(img)
    else:
        messagebox.showinfo("Undo", "No more actions to undo.")

# Function to redo the last undone action
def redo_action():
    global img
    if redo_stack:
        save_history()
        img = redo_stack.pop()
        update_display(img)
    else:
        messagebox.showinfo("Redo", "No more actions to redo.")






E1 = '#6579BE'  #DENIM BLUE
E2 = '#EAB099'
F1 = '#19485F'  #OCEAN BLUE
F2 = '#D9E0A4'  #LIME GREEN
G2 = "#AFAFDA"  #CORAL BLUE
# Buttons for the editora
buttons = [
    ("Open Image", open_img, E2),
    ("Save Image", save_img, E2),
    ("Undo", undo_action, F1),
    ("Redo", redo_action, F2),
    ("Remove Image", remove_img, "#EF9A9A"),
]

# Add buttons to the right frame
for text, command, color in buttons:
    btn = Button(right_frame, text=text, command=command, bg=color, font=("Arial", 12), width=20)
    btn.pack(pady=5)

# Start the main loop
root.mainloop()