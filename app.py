from calculator import add, sub, mul, div
# simple console calculator
def main():
    """Console calculator entry point."""
    print("1) Add\n2) Subtract\n3) Multiply\n4) Divide\n0) Exit program")
    option = input("select: ")
    a = float(input("a: "))    
    b = float(input("b: "))
    if option == "1": 
        print(add(a,b))

    if option == "4" and b == 0: print("Error: division by zero")
    if option == "4" and b != 0: print(div(a, b))

if __name__ == "__main__":
    main()

