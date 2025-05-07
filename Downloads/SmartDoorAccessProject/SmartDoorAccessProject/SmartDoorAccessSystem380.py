import face_recognition
import sqlite3
import numpy as np
import cv2
import os

# ======== DB ===========
def create_db():
    try:
        conn = sqlite3.connect('encodings.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                name TEXT,
                encoding BLOB
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Error creating DB] {e}")

def save_encoding(name, encoding):
    try:
        conn = sqlite3.connect('encodings.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO faces (name, encoding) VALUES (?, ?)',
                       (name, encoding.tobytes()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Error saving encoding] {e}")

def load_encodings():
    try:
        conn = sqlite3.connect('encodings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, encoding FROM faces')
        data = cursor.fetchall()
        conn.close()

        names = []
        encodings = []
        for name, enc in data:
            names.append(name)
            encodings.append(np.frombuffer(enc, dtype=np.float64))
        return names, encodings
    except Exception as e:
        print(f"[Error loading encodings] {e}")
        return [], []

def delete_face(name):
    try:
        conn = sqlite3.connect('encodings.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM faces WHERE name = ?', (name,))
        conn.commit()
        conn.close()
        print(f"🗑️ Deleted all records for '{name}'.")
    except Exception as e:
        print(f"[Error deleting face] {e}")

# ======== Add face to DB ===========
def add_face_to_db(name, image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        print("❌ No face found.")
        return
    save_encoding(name, encodings[0])
    print(f"✅ {name} added to DB.")

# ======== Get image from camera ===========
def get_image_from_camera():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not available.")
            return None

        print("📷 Click 'Capture' or close the window to cancel.")

        captured = False
        image_path = None

        def mouse_callback(event, x, y, flags, param):
            nonlocal captured, image_path, frame
            if event == cv2.EVENT_LBUTTONDOWN:
                if 20 <= x <= 180 and 480 <= y <= 530:
                    image_path = "captured.jpg"
                    cv2.imwrite(image_path, frame)
                    print(f"✅ Photo saved as '{image_path}'")
                    captured = True

        cv2.namedWindow("Smart Door Camera")
        cv2.setMouseCallback("Smart Door Camera", mouse_callback)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame.")
                break

            frame = cv2.resize(frame, (960, 540))

            button_frame = frame.copy()
            cv2.rectangle(button_frame, (20, 480), (180, 530), (0, 120, 255), -1)
            cv2.putText(button_frame, "Capture", (40, 515), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            cv2.imshow("Smart Door Camera", button_frame)
            cv2.waitKey(1)

            if captured:
                break

            if cv2.getWindowProperty("Smart Door Camera", cv2.WND_PROP_VISIBLE) < 1:
                print("❎ Window closed.")
                break

        cap.release()
        cv2.destroyAllWindows()
        return image_path if captured else None

    except Exception as e:
        print(f"[Camera Error] {e}")
        return None


def get_image_from_file():
    path = input("🖼️ Enter path to image: ").strip()
    if os.path.exists(path):
        return path
    else:
        print("❌ File not found.")
        return None

# ======== Recognize ===========
def recognize(image_path):
    try:
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return "❌ Failed to read image file."

        rgb_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        unknown_encs = face_recognition.face_encodings(rgb_img)

        if not unknown_encs:
            return "🚫 Access denied. No recognizable face found."

        unknown_encoding = unknown_encs[0]
        names, known_encodings = load_encodings()

        if not known_encodings:
            return "❌ Face database is empty."

        matches = face_recognition.compare_faces(known_encodings, unknown_encoding)
        if True in matches:
            index = matches.index(True)
            return f"✅ Access granted. Welcome, {names[index]}"
        else:
            return "🚫 Access denied. Face not recognized."
    except Exception as e:
        return f"[Recognition error] {e}"


# ======== Admin mode ===========
def admin_mode():
    while True:
        print("\n🔐 Admin Panel")
        print("1 - Add face to DB")
        print("2 - Delete face from DB")
        print("3 - View all entries")
        print("4 - Exit admin mode")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            name = input("Enter person's name: ").strip()
            path = get_image_from_file()
            if path:
                add_face_to_db(name, path)
        elif choice == '2':
            name = input("Enter name to delete: ").strip()
            delete_face(name)
        elif choice == '3':
            names, _ = load_encodings()
            if names:
                print("✅ Stored names:")
                for n in set(names):
                    print(f"- {n}")
            else:
                print("📂 No entries found.")
        elif choice == '4':
            break
        else:
            print("❌ Invalid option.")

# ======== البرنامج الرئيسي ===========
def main():
    create_db()
    print("Are you an admin or user?")
    print("1 - Admin")
    print("2 - Not admin")
    role = input("Enter 1 or 2: ").strip()

    if role == '1':
        pwd = input("🔑 Enter admin password: ").strip()
        if pwd == "admin123":
            admin_mode()
        else:
            print("❌ Incorrect password.")
    elif role == '2':
        print("Choose input method:")
        print("1 - Upload image file")
        print("2 - Use webcam")
        choice = input("Enter 1 or 2: ").strip()

        if choice == '1':
            img_path = get_image_from_file()
        elif choice == '2':
            img_path = get_image_from_camera()
        else:
            print("❌ Invalid input method.")
            return

        if img_path:
            recognize(img_path)
        else:
            print("❌ No image provided.")
    else:
        print("❌ Invalid role.")

if __name__ == "__main__":
    main()

