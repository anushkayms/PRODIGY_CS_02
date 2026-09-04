import os
import shutil
import hmac
import hashlib
import threading
from tkinter import filedialog

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, UnidentifiedImageError, PngImagePlugin
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes


def derive_key(password, context):
    digest = hashes.Hash(hashes.SHA256())
    digest.update((password + context).encode())
    return digest.finalize()


def get_encryption_key(password):
    return derive_key(password, "ENC")


def get_mac_key(password):
    return derive_key(password, "MAC")


def xor_with_keystream(data, password):
    key = get_encryption_key(password)
    nonce = key[:16]
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()


def compute_mac(data, password):
    mac_key = get_mac_key(password)
    return hmac.new(mac_key, data, hashlib.sha256).hexdigest()


def encrypt_image(image_path, password, output_path):
    img = Image.open(image_path).convert("RGBA")
    raw_data = img.tobytes()
    scrambled_data = xor_with_keystream(raw_data, password)
    mac_value = compute_mac(scrambled_data, password)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("hmac", mac_value)

    new_img = Image.frombytes("RGBA", img.size, scrambled_data)
    new_img.save(output_path, pnginfo=pnginfo)
    return new_img


def decrypt_image(image_path, password, output_path):
    img = Image.open(image_path)
    img.load()
    stored_mac = img.info.get("hmac")

    if stored_mac is None:
        raise ValueError("NOT_ENCRYPTED")

    img = img.convert("RGBA")
    raw_data = img.tobytes()
    computed_mac = compute_mac(raw_data, password)

    if not hmac.compare_digest(computed_mac, stored_mac):
        raise ValueError("AUTH_FAILED")

    decrypted_data = xor_with_keystream(raw_data, password)
    new_img = Image.frombytes("RGBA", img.size, decrypted_data)
    new_img.save(output_path)
    return new_img


def get_unique_filename(base_name):
    ensure_output_dir()
    full_path = os.path.join(OUTPUT_DIR, base_name)
    if not os.path.exists(full_path):
        return full_path
    name, ext = os.path.splitext(base_name)
    counter = 1
    while True:
        candidate = os.path.join(OUTPUT_DIR, f"{name}_{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    return OUTPUT_DIR


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PREVIEW_SIZE = (300, 300)
OUTPUT_DIR = "PixelVault_Output"


class ImageEncryptorApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Pixel Vault - Image Encryption Tool")
        self.geometry("820x560")
        self.minsize(760, 520)

        self.selected_path = None
        self.output_path = None

        blank = Image.new("RGBA", PREVIEW_SIZE, (0, 0, 0, 0))
        self.blank_photo = ImageTk.PhotoImage(blank)

        self._build_layout()

    def _build_layout(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        header = ctk.CTkLabel(
            self, text="Pixel Vault",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        header.grid(row=0, column=0, columnspan=2, pady=(20, 0), sticky="n")

        subtitle = ctk.CTkLabel(
            self, text="AES-256 pixel-level image encryption",
            font=ctk.CTkFont(size=13), text_color="gray"
        )
        subtitle.grid(row=0, column=0, columnspan=2, pady=(50, 10), sticky="n")

        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        preview_frame.grid_columnconfigure((0, 1), weight=1)

        self.original_panel = self._make_preview_panel(preview_frame, "Image", column=0)
        self.output_panel = self._make_preview_panel(preview_frame, "Result", column=1)

        self.original_panel.image_label.drop_target_register(DND_FILES)
        self.original_panel.image_label.dnd_bind("<<Drop>>", self.on_drop)
        self.original_panel.drop_target_register(DND_FILES)
        self.original_panel.dnd_bind("<<Drop>>", self.on_drop)

        controls = ctk.CTkFrame(self)
        controls.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew")
        controls.grid_columnconfigure(1, weight=1)

        browse_btn = ctk.CTkButton(controls, text="Choose Image", command=self.browse_image, width=140)
        browse_btn.grid(row=0, column=0, padx=10, pady=10)

        self.file_label = ctk.CTkLabel(controls, text="No image selected", text_color="gray", anchor="w")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.password_entry = ctk.CTkEntry(controls, placeholder_text="Enter password", show="*", width=220)
        self.password_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        self.show_pw_var = ctk.BooleanVar(value=False)
        show_pw_check = ctk.CTkCheckBox(
            controls, text="Show password", variable=self.show_pw_var,
            command=self.toggle_password_visibility
        )
        show_pw_check.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="e")

        button_row = ctk.CTkFrame(controls, fg_color="transparent")
        button_row.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        self.encrypt_btn = ctk.CTkButton(
            button_row, text="Encrypt", fg_color="#1f6aa5",
            command=lambda: self.run_operation("encrypt"), width=140
        )
        self.encrypt_btn.grid(row=0, column=0, padx=10)

        self.decrypt_btn = ctk.CTkButton(
            button_row, text="Decrypt", fg_color="#2e7d32",
            command=lambda: self.run_operation("decrypt"), width=140
        )
        self.decrypt_btn.grid(row=0, column=1, padx=10)

        self.mode_label = ctk.CTkLabel(
            button_row, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9aa0a6"
        )
        self.mode_label.grid(row=0, column=2, padx=(14, 0))

        self.status_label = ctk.CTkLabel(
            controls, text="Status: Ready", font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(0, 2))

        self.output_file_label = ctk.CTkLabel(
            controls, text="", font=ctk.CTkFont(size=12), text_color="#9aa0a6"
        )
        self.output_file_label.grid(row=4, column=0, sticky="e", padx=(0, 8), pady=(0, 10))

        self.save_as_btn = ctk.CTkButton(
            controls, text="Save As...", command=self.save_output_as,
            width=100, height=24, fg_color="#3a3d3e", hover_color="#4a4d4e",
            state="disabled"
        )
        self.save_as_btn.grid(row=4, column=1, sticky="w", padx=(8, 0), pady=(0, 10))

    def _make_preview_panel(self, parent, title, column):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=column, padx=10, sticky="nsew")

        label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=(10, 5))

        image_label = ctk.CTkLabel(
            frame, text="No image\n(drag & drop here)", width=PREVIEW_SIZE[0], height=PREVIEW_SIZE[1],
            fg_color="#2a2d2e", corner_radius=8
        )
        image_label.pack(padx=10, pady=(0, 10))
        frame.image_label = image_label
        frame.title_label = label
        return frame

    def toggle_password_visibility(self):
        self.password_entry.configure(show="" if self.show_pw_var.get() else "*")

    def browse_image(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if not path:
            return
        self._load_selected_image(path)

    def on_drop(self, event):
        path = event.data.strip()
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        self._load_selected_image(path)

    def _load_selected_image(self, path):
        if not path or not os.path.isfile(path):
            self._set_status("Status: That file could not be found.", "orange")
            return
        try:
            with Image.open(path) as img:
                img.verify()
        except Exception:
            self._set_status("Status: That file isn't a valid image.", "orange")
            return

        self.selected_path = path
        self.file_label.configure(text=os.path.basename(path), text_color="white")
        self._set_preview(self.original_panel, path)
        self._clear_preview(self.output_panel)
        self._set_status("Status: Ready", "white")
        self.output_file_label.configure(text="")
        self.save_as_btn.configure(state="disabled")

    def _set_preview(self, panel, image_path):
        try:
            img = Image.open(image_path).convert("RGBA")
            img.thumbnail(PREVIEW_SIZE)
            photo = ImageTk.PhotoImage(img)
            panel.image_label.configure(image=photo, text="")
            panel.image_label.image = photo
            self.update_idletasks()
        except Exception:
            self._clear_preview(panel, message="Preview unavailable")

    def _clear_preview(self, panel, message="No image"):
        photo = self.blank_photo
        panel.image_label.configure(image=photo, text=message)
        panel.image_label.image = photo

    def run_operation(self, mode):
        if not self.selected_path:
            self._set_status("Status: Please choose an image first.", "orange")
            return

        password = self.password_entry.get().strip()
        if not password:
            self._set_status("Status: Password cannot be empty.", "orange")
            return

        self._apply_mode_labels(mode)

        self.encrypt_btn.configure(state="disabled")
        self.decrypt_btn.configure(state="disabled")
        self.output_file_label.configure(text="")
        self._set_status("Status: Processing...", "#9aa0a6")

        thread = threading.Thread(target=self._process, args=(mode, password), daemon=True)
        thread.start()

    def _apply_mode_labels(self, mode):
        if mode == "encrypt":
            self.original_panel.title_label.configure(text="Original Image")
            self.output_panel.title_label.configure(text="Encrypted Image")
            self.mode_label.configure(text="Encryption Mode")
        else:
            self.original_panel.title_label.configure(text="Encrypted Image")
            self.output_panel.title_label.configure(text="Decrypted Image")
            self.mode_label.configure(text="Decryption Mode")

    def _process(self, mode, password):
        try:
            if mode == "encrypt":
                output_path = get_unique_filename("encrypted_output.png")
                encrypt_image(self.selected_path, password, output_path)
                self.after(0, self._on_success, "Encryption successful!", output_path)
            else:
                output_path = get_unique_filename("decrypted_output.png")
                decrypt_image(self.selected_path, password, output_path)
                self.after(0, self._on_success, "Decryption successful!", output_path)
        except ValueError as e:
            if str(e) == "AUTH_FAILED":
                msg = "Incorrect password or authentication failed."
            elif str(e) == "NOT_ENCRYPTED":
                msg = "This file wasn't encrypted by this tool."
            else:
                msg = str(e)
            self.after(0, self._on_failure, msg)
        except UnidentifiedImageError:
            self.after(0, self._on_failure, "That file isn't a valid or recognized image.")
        except Exception as e:
            self.after(0, self._on_failure, f"Operation failed: {e}")

    def _on_success(self, message, output_path):
        self.output_path = output_path
        self._set_preview(self.output_panel, output_path)
        self._set_status(message, "#4caf50")
        self.output_file_label.configure(text=f"Output File: {output_path}")
        self.save_as_btn.configure(state="normal")
        self.encrypt_btn.configure(state="normal")
        self.decrypt_btn.configure(state="normal")

    def _on_failure(self, message):
        self._set_status(message, "#e53935")
        self.output_file_label.configure(text="")
        self.save_as_btn.configure(state="disabled")
        self.encrypt_btn.configure(state="normal")
        self.decrypt_btn.configure(state="normal")

    def _set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    def save_output_as(self):
        if not self.output_path or not os.path.exists(self.output_path):
            return

        dest = filedialog.asksaveasfilename(
            title="Save output image as",
            defaultextension=".png",
            initialfile=os.path.basename(self.output_path),
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if not dest:
            return

        try:
            shutil.copyfile(self.output_path, dest)
            self._set_status(f"Copy saved to {dest}", "#4caf50")
        except Exception as e:
            self._set_status(f"Could not save copy: {e}", "#e53935")


if __name__ == "__main__":
    app = ImageEncryptorApp()
    app.mainloop()
