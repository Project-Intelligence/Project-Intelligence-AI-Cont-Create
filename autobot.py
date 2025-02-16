def main():
    print("Autobot activated. Ready to execute Python commands.")
    while True:
        command = input("Enter Python command: ")  # Prompt for input
        try:
            # Evaluate the command using eval, suitable for simple expressions
            result = eval(command)
            if result is not None:
                print(result)
        except Exception as e:
            # If eval fails, try exec, suitable for more complex statements
            try:
                exec(command)
            except Exception as e:
                print(f"An error occurred: {e}")  # Print any errors that occur

if __name__ == "__main__":
    main()
