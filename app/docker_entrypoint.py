import time
import os


def main():
    print("Starting decompiler service")
    for k, v in os.environ.items():
        print(f"{k} = {v}")
    time.sleep(10000)


if __name__ == "__main__":
    main()
