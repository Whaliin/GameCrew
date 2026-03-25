ERR_DIV_ZERO = "Error: division by zero"

from calculator import add, sub, mul, div
# simple console calculator

def get_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Starts interactive console flow."""
    # Menu options; extend as feature grow
    print("1) Add")
    print("2) Subtract")
    print("3) Multiply")
    print("4) Divide")
    print("0) Quit")
    option = input("Select: ").strip()

    if option == "0":
        print("Goodbye!")
        return
    
    # Note: simple input parsing; consider try/except for robust handling.
    a = get_float("a: ")
    b = get_float("b: ")
    if option == "1": print(f"{add(a, b):.2f}")
    elif option == "2": print(f"{sub(a, b):.2f}")
    elif option == "3": print(f"{mul(a, b):.2f}")
    elif option == "4":
        if b == 0:
            print(ERR_DIV_ZERO)
        else:
            print(f"{div(a, b):.2f}")
    else: 
        print("Unknown option")

if __name__ == "__main__":
    main() 