#!/usr/bin/env python3
import json

def main():
    data = {}
    while True:
        try:
            line = input("(Key||Value) : ")

            # Check for the stop condition
            if line.strip().lower() == "stop":
                break

            # Split and validate the input
            key, value = line.split("||")
            if not key or not value:
                raise ValueError("Invalid input format. Use 'key||value'.")
            data[key.strip()] = value.strip()  # Store the pair

        except ValueError as e:
            print(f"Error: {e}. Please try again.")

    # Generate and print the JSON (pretty-printed)
    if data:  # Only if there's actual data
        print(json.dumps(data, indent=4))

if __name__ == "__main__":
    main()
