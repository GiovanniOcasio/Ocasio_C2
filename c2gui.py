#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import threading
from c2core import greet, listener_info, listener

# Display ASCII art in terminal
greet()

# Initial launcher window
root = tk.Tk()
root.title("Ocasio C2 Launcher")

# Load and display logo
logo = Image.open("Ocasio_C2.png")
logo_image = ImageTk.PhotoImage(logo)

logo_label = tk.Label(root, image=logo_image)
logo_label.image = logo_image  # Keep reference
logo_label.pack(pady=10)

# Dashboard GUI
def open_dashboard():
    root.destroy()

    dashboard = tk.Tk()
    dashboard.title("Ocasio C2 Dashboard")
    dashboard.geometry("800x500")

    tk.Label(dashboard, text="OCASIO C2 DASHBOARD", font=("Helvetica", 16, "bold")).pack(pady=10)

    # Frame for layout
    content_frame = tk.Frame(dashboard)
    content_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Terminal-style output on the left
    log_display = scrolledtext.ScrolledText(
        content_frame, width=70, height=20, bg="black", fg="lime", font=("Courier", 10)
    )
    log_display.pack(side="left", fill="both", expand=True)

    def log_message(msg):
        log_display.insert(tk.END, msg + "\n")
        log_display.see(tk.END)

    # Command panel on the right
    cmd_frame = tk.Frame(content_frame)
    cmd_frame.pack(side="right", fill="y", padx=10)

    tk.Label(cmd_frame, text="Send Command", font=("Arial", 12, "bold")).pack(pady=5)
    cmd_entry = tk.Entry(cmd_frame, width=25)
    cmd_entry.pack(pady=5)

    send_button = tk.Button(cmd_frame, text="Send", width=15, bg="blue", fg="white")
    send_button.pack(pady=5)

    # Exit button
    exit_button = tk.Button(dashboard, text="Exit", width=12, bg="gray", fg="white",
                            command=dashboard.destroy)
    exit_button.pack(pady=5)

    # Stealth mode buttons
    stealth_label = tk.Label(dashboard, text="Use Stealth Mode?", font=("Arial", 12, "bold"))
    stealth_label.pack()

    yes_button = tk.Button(dashboard, text="Yes", width=12, bg="green", fg="white",
                           command=lambda: run_listener(True))
    yes_button.pack(pady=2)

    no_button = tk.Button(dashboard, text="No", width=12, bg="red", fg="white",
                          command=lambda: run_listener(False))
    no_button.pack(pady=2)

    # Socket connection reference
    conn_obj = {"socket": None}

    def run_listener(stealth_enabled):
        stealth_label.destroy()
        yes_button.destroy()
        no_button.destroy()

        lhost, lport = listener_info(use_input=False, stealth_override=stealth_enabled)
        log_message(f"[+] Starting listener on {lhost}:{lport} ...")

        def threaded_listener():
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((lhost, lport))
                s.listen()
                conn, addr = s.accept()
                conn_obj["socket"] = conn
                log_message(f"[+] Connection from {addr}")

                try:
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        output = data.decode(errors="ignore")
                        log_message(output.strip())
                except Exception as e:
                    log_message(f"[-] Listener error: {e}")
                finally:
                    log_message("[-] Connection closed.")

        threading.Thread(target=threaded_listener, daemon=True).start()

    def send_command():
        cmd = cmd_entry.get().strip()
        sock = conn_obj.get("socket")
        if sock and cmd:
            try:
                sock.sendall(cmd.encode() + b"\n")
                log_message(f"[>] Sent: {cmd}")
                cmd_entry.delete(0, tk.END)
            except Exception as e:
                log_message(f"[-] Failed to send command: {e}")
        else:
            log_message("[-] No active connection or empty command.")

    send_button.config(command=send_command)

    dashboard.mainloop()

# Launch button
ttk.Button(root, text="Launch Dashboard", command=open_dashboard).pack(pady=20)

root.mainloop()

