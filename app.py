from calculator import add, sub, mul, div
# simple console calculator
def main():
    """Console calculator entry point."""
    print("1) Add") 
    print("2) Subtract")
    print("3) Multiply")
    print("4) divide")
    print("0) Exit")
    option = input("select: ")
    
    if choice == "1": 
        a = float(input("a: "))    
        b =float(input("b: "))
        print(add(a,b))

    if choice == "4" and b == 0: print("Error: division by zero")
    if choice == "4" and b != 0: print(div(a, b))

if __name__ == "__main__":
    main()

