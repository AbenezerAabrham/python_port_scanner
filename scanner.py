#!/usr/bin/env python3
"""
Simple Multithreaded TCP Port Scanner
Author: Abrham Abenezer
Usage: python3 scanner.py -t <target> -p <start-end>
"""

import socket
import threading
import argparse
import sys

# Lock for clean thread-safe printing
print_lock = threading.Lock()


def scan_port(target: str, port: int, timeout: float):
    """Scan a single TCP port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((target, port))
        if result == 0:
            with print_lock:
                print(f"[+] Port {port} OPEN")

        sock.close()

    except socket.error:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Multithreaded TCP Port Scanner"
    )

    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Target IP address or domain"
    )

    parser.add_argument(
        "-p", "--ports",
        default="1-1024",
        help="Port range (default: 1-1024)"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=0.5,
        help="Socket timeout in seconds (default: 0.5)"
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=100,
        help="Maximum concurrent threads (default: 100)"
    )

    args = parser.parse_args()

    # Parse port range
    try:
        start_port, end_port = map(int, args.ports.split("-"))
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError
    except ValueError:
        print("❌ Invalid port range. Example: 1-1024")
        sys.exit(1)

    # Resolve target
    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print("❌ Could not resolve target")
        sys.exit(1)

    print(f"\n🔍 Scanning {target_ip} ({args.target})")
    print(f"📌 Ports: {start_port}-{end_port}\n")

    semaphore = threading.Semaphore(args.threads)
    threads = []

    def thread_wrapper(p):
        with semaphore:
            scan_port(target_ip, p, args.timeout)

    try:
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=thread_wrapper, args=(port,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    except KeyboardInterrupt:
        print("\n❌ Scan interrupted by user")
        sys.exit(0)

    print("\n✅ Scan completed")


if __name__ == "__main__":
    main()