def run():
    print("1) Add") 
    print("2) Subtract")
    print("3) Multiply")
    print("4) divide")
    print("0) Exit")
    choice = input("select: ")
    
    if choice == "1": 
        a = float(input("a: "))    
        b =float(input("b: "))
        print(add(a,b))

    
