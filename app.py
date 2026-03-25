ERR_DIV_ZERO = "Error: division by zero"

from calculator import add, sub, mul, div
# simple console calculator

def main():
    """Starts interactive console flow."""
    print("1) Add")
    print("2) Subtract")
    print("3) Multiply")
    print("4) Divide")
    print("0) Quit")
    option = input("Select: ").strip()
    
    # Note: simple input parsing; consider try/except for robust handling.
    a = float(input("a: "))    
    b = float(input("b: "))
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