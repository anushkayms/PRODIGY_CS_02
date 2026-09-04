# 🖼️ Pixel Vault – Image Encryption Tool

Pixel Vault is a Python-based Image Encryption and Decryption tool developed as part of **Task 02 of the Prodigy InfoTech Cyber Security Internship**.

The application encrypts image pixel data using a password and allows users to decrypt the image back using the correct password.

The project includes:

- 🖥️ Command-Line Version (`encrypt.py`)
- 🎨 Modern Desktop GUI Version (`gui_app.py`)

---

## ✨ Features

- 🔐 Password-based image encryption and decryption
- 🛡️ AES-256 encryption using CTR mode
- ✅ HMAC-SHA256 authentication
- ❌ Wrong password detection
- 🖼️ Input and output image preview
- 📂 Drag-and-drop image support
- 👁️ Password show/hide option
- 💾 Automatic output saving
- 📁 Dedicated `PixelVault_Output` folder
- 🎨 Modern dark-mode GUI
- 🧵 Background processing for a responsive interface
- 📝 Unique filenames to prevent overwriting files

---

## 🛠️ Technologies Used

- Python 3
- Pillow (PIL)
- cryptography
- CustomTkinter
- tkinterdnd2
- hmac / hashlib

---

## 📂 Project Structure

```text
PixelEncryption/
│
├── encrypt.py
├── gui_app.py
├── README.md
│
└── PixelVault_Output/
```

---

## ⚙️ Installation & Setup

### GUI Version

```bash
pip install pillow cryptography customtkinter tkinterdnd2
python gui_app.py
```

### Command-Line Version

```bash
pip install pillow cryptography
python encrypt.py
```

---

## 🔍 How It Works

1. Select or drag an image into the application.
2. Choose **Encryption** or **Decryption** mode.
3. Enter a password.
4. The image pixel data is processed securely.
5. The result is displayed and saved in the `PixelVault_Output` folder.

If an incorrect password is entered during decryption, the application stops the process and displays an authentication error.

---

## 📌 Internship Task

### Task 02 – Image Encryption

The objective of this task is to develop a tool that encrypts and decrypts images using pixel manipulation techniques.

Pixel Vault extends this concept with password-based encryption, authentication, wrong-password detection, a command-line version, and a modern desktop GUI.

---

## 🎯 Learning Outcomes

Through this project, I explored:

- Image pixel manipulation
- Image encryption and decryption
- AES encryption
- Password authentication using HMAC
- Python image processing
- GUI development
- Drag-and-drop functionality
- Background threading

---
⭐ Developed as part of the **Prodigy InfoTech Cyber Security Internship – Task 02: Image Encryption Tool**.

Computer Engineering Student | Cybersecurity Enthusiast

---

⭐ Developed as part of the **Prodigy InfoTech Cyber Security Internship – Task 02: Image Encryption Tool**.
