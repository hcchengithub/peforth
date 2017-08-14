import projectk as vm

# peforth version 
version = 1.01
def temp():
    print("p e f o r t h    v" + str(version));
    print("source code http://github.com/hcchengithub/peforth");
    return version;
vm.greeting = temp
    
# The eforth.py command line interface, the main program loop
def main():
    # include forth root peforth.f
    f = open('peforth.f','r',encoding='utf-8')
    s = f.read()
    f.close()
    vm.dictate(s)
    # include quit.f for peforth.3py
    f = open('quit.f','r',encoding='utf-8')
    s = f.read()
    f.close()
    vm.dictate(s)
    print('OK ', end="")
    while True:
        cmd = input("").strip()
        if cmd == "":
            print('OK ', end="")
            continue
        elif cmd == "exit":
            break
        else:    
            vm.dictate(cmd)
            print('OK ', end="")

if __name__ == '__main__':
    main()
