# 🖼️ Pixel Vault – Image Encryption Tool

Pixel Vault is a Python-based Image Encryption and Decryption tool developed as part of **Task 02 of the Prodigy InfoTech Cyber Security Internship**.

The application encrypts image pixel data using a password and allows users to decrypt the image back using the correct password.

The project includes:

- 🖥️ Command-Line Version (`encrypt.py`)
- 🎨 Modern Desktop GUI Version (`gui_app.py`)

---
## 🔍 How It Works

### Encryption

1. Select or drag an image into the application.
2. Choose **Encryption Mode**.
3. Enter a password.
4. The image pixel data is encrypted using AES-256 CTR.
5. An HMAC-SHA256 authentication value is generated.
6. The encrypted image is saved in the `PixelVault_Output` folder.

### Decryption

1. Select the encrypted image.
2. Choose **Decryption Mode**.
3. Enter the correct password.
4. The application verifies the authentication data.
5. If the password is correct, the image is decrypted.
6. The original image data is restored.

If an incorrect password is entered, the application stops the process and displays:

**Incorrect password or authentication failed**
---
## 🔐 Encryption & Security

Pixel Vault uses **AES-256 in CTR mode** to generate a secure keystream for encrypting image pixel data.

Separate keys are derived from the user's password for:

- Encryption
- Authentication

The project also uses **Encrypt-then-MAC** with HMAC-SHA256 to verify the encrypted image before decryption.

This prevents incorrect passwords from silently producing corrupted output.

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

### Install dependencies for the GUI version:

```bash
pip install pillow cryptography customtkinter tkinterdnd2
```

Run the GUI application:

```bash
python gui_app.py
```

### Install dependencies for the Command-Line version:

```bash
pip install pillow cryptography
```

Run the CLI application:

```bash
python encrypt.py
```



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
