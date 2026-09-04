import os
import hmac
import hashlib
from PIL import Image, UnidentifiedImageError, PngImagePlugin
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


def get_nonce(encryption_key):
    return encryption_key[:16]


def xor_with_keystream(data, password):
    key = get_encryption_key(password)
    nonce = get_nonce(key)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()


def compute_mac(data, password):
    mac_key = get_mac_key(password)
    return hmac.new(mac_key, data, hashlib.sha256).hexdigest()


def display_image_info(path, img):
    print(f"Filename: {os.path.basename(path)}")
    print(f"Image size: {img.size[0]} x {img.size[1]}")
    print(f"Image mode: {img.mode}")


def validate_image(image_path):
    if not os.path.exists(image_path):
        return "Error: That image file doesn't exist. Check the filename/path and try again."
    try:
        with Image.open(image_path) as img:
            img.verify()
    except UnidentifiedImageError:
        return "Error: That file isn't a valid/recognized image."
    except Exception:
        return "Error: That image file appears to be corrupted."
    return None


def get_password():
    while True:
        password = input("Enter password: ").strip()
        if password:
            return password
        print("Error: Password cannot be empty.")


def get_unique_filename(base_name):
    if not os.path.exists(base_name):
        return base_name
    name, ext = os.path.splitext(base_name)
    counter = 1
    while os.path.exists(f"{name}_{counter}{ext}"):
        counter += 1
    return f"{name}_{counter}{ext}"


def encrypt_image(image_path, password, output_path):
    img = Image.open(image_path).convert("RGBA")
    display_image_info(image_path, img)

    raw_data = img.tobytes()
    scrambled_data = xor_with_keystream(raw_data, password)
    mac_value = compute_mac(scrambled_data, password)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("hmac", mac_value)

    new_img = Image.frombytes("RGBA", img.size, scrambled_data)
    new_img.save(output_path, pnginfo=pnginfo)


def decrypt_image(image_path, password, output_path):
    img = Image.open(image_path)
    img.load()
    stored_mac = img.info.get("hmac")

    if stored_mac is None:
        raise ValueError("NOT_ENCRYPTED")

    img = img.convert("RGBA")
    display_image_info(image_path, img)

    raw_data = img.tobytes()
    computed_mac = compute_mac(raw_data, password)

    if not hmac.compare_digest(computed_mac, stored_mac):
        raise ValueError("AUTH_FAILED")

    decrypted_data = xor_with_keystream(raw_data, password)
    new_img = Image.frombytes("RGBA", img.size, decrypted_data)
    new_img.save(output_path)


def encrypt_flow():
    image_path = input("Enter image filename (with path if needed): ").strip()
    error = validate_image(image_path)
    if error:
        print(error)
        return None

    password = get_password()
    output_path = get_unique_filename("encrypted_output.png")

    try:
        encrypt_image(image_path, password, output_path)
    except Exception as e:
        print(f"Encryption failed: {e}")
        return None

    print("Encryption successful!")
    print(f"Output saved as: {output_path}")
    return output_path


def decrypt_flow(image_path=None):
    if image_path is None:
        image_path = input("Enter image filename (with path if needed): ").strip()
        error = validate_image(image_path)
        if error:
            print(error)
            return

    password = get_password()
    output_path = get_unique_filename("decrypted_output.png")

    try:
        decrypt_image(image_path, password, output_path)
    except ValueError as e:
        if str(e) == "AUTH_FAILED":
            print("Error: Incorrect password or authentication failed.")
        elif str(e) == "NOT_ENCRYPTED":
            print("Error: This file wasn't encrypted by this tool (no verification data found).")
        return
    except Exception as e:
        print(f"Decryption failed: {e}")
        return

    print("Decryption successful!")
    print(f"Output saved as: {output_path}")


def post_encrypt_menu(last_encrypted_path):
    while True:
        print("\nWhat would you like to do next?")
        print("(D) Decrypt the image you just encrypted")
        print("(E) Perform another operation")
        print("(X) Exit")
        choice = input("Choice: ").strip().lower()

        if choice == "d":
            decrypt_flow(image_path=last_encrypted_path)
        elif choice == "e":
            return "main"
        elif choice == "x":
            return "exit"
        else:
            print("Invalid choice. Please enter D, E, or X.")


def get_main_choice():
    while True:
        choice = input("Do you want to (E)ncrypt or (D)ecrypt? ").strip().lower()
        if choice in ("e", "d"):
            return choice
        print("Invalid choice. Please enter E or D.")


def main():
    print("=== Image Encryption Tool ===")
    while True:
        choice = get_main_choice()

        if choice == "e":
            encrypted_path = encrypt_flow()
            if encrypted_path:
                action = post_encrypt_menu(encrypted_path)
                if action == "exit":
                    print("Goodbye!")
                    return

        elif choice == "d":
            decrypt_flow()

        print()


if __name__ == "__main__":
    main()