#!/usr/bin/env python3

from mcc_ws_helper import connect_and_auth, start_recv

def main():
    connect_and_auth("ws://127.0.0.1:8043", "12345678")

if __name__ == "__main__":
    main()
    start_recv()
