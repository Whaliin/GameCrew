ERR_DIV_ZERO = "Error: division by zero"

from calculator import add, sub, mul, div
# simple console calculator

def main():
    """Console calculator entry point."""
    print("1) Add")
    print("2) Subtract")
    print("3) Multiply")
    print("4) Divide")
    print("0) Quit")
    option = input("Select: ").strip()
    
    # Note: simple input parsing; consider try/except for robust handling.
    a = float(input("a: "))    
    b = float(input("b: "))
    if option == "1": 
        print(add(a,b))

    if option == "2": print(sub(a, b))
    if option == "3": print(mul(a, b))
    if option == "4" and b == 0: print(ERR_DIV_ZERO)
    if option == "4" and b != 0: print(div(a, b))
    else: 
        print("Unknown option")

if __name__ == "__main__":
    main()

