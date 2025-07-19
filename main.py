import pandas as pd



if __name__ == '__main__':
    print("Hello World")
    import socket

    hostname = socket.gethostname()  # Get the hostname
    ip_address = socket.gethostbyname(hostname)  # Get the IP address

    print(f"Hostname: {hostname}")
    print(f"IP Address: {ip_address}")