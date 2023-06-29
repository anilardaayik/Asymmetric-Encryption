import random
import time

def power_calculator_residue(a,b,p):
    if b == 1: 
        return a % p
    
    if b % 2 == 0:
        c = power_calculator_residue(a, b//2, p)
        return c*c % p
    
    else:
        c = power_calculator_residue(a, (b-1)//2, p)
        return c*c*a % p 

def gcd(a,b):
    if a == 1 or b == 1:
        return 1
    else:
        if a > b:
            k = a // b
            return gcd(a-b*k,b)
        if b > a: 
            k = b // a
            return gcd(a,b-k*a)
        if a == b:
            return a
        
def encryption(h, k, F, msg):
    crp = []
    key = power_calculator_residue(h, k, F)
    for symbol in msg:
        asci = ord(symbol)
        deger = asci*key
        crp.append(deger)
    
    return crp

def decryption(p, b, F, crp):
    skey = power_calculator_residue(p, b, F)
    dec = ""
    for elements in crp:
        assci = elements//skey
        dec += str(chr(assci))
    
    return dec

def string_to_ascii(string):
    asci = ""
    for unit in string:
        asci += str(ord(unit))
        asci += " " 
    return asci

def ascii_to_string(asci):
    list = [int(i) for i in asci.strip().split()]
    string = ""
    for element in list:
        harf = chr(element)
        string += str(harf)
    return string

def key_writer(F, p, q, g):
    with open("text.txt", "w") as w:
        ord_F = str(ord("F")) + " " + str(ord(":")) + " " + string_to_ascii(str(F)) 
        #Sending the group to the sender 
        w.write(ord_F)
        w.write("\n")
        ord_h = str(ord("P")) + " " + str(ord(":")) + " " + string_to_ascii(str(p))
        #Sending the receiver's pub key to the sender
        w.write(ord_h)
        w.write("\n")
        ord_q = str(ord("Q")) + " " + str(ord(":")) + " " + string_to_ascii(str(q))
        #Sending the order of the cyclic group to the sender
        w.write(ord_q)
        w.write("\n")
        ord_g = str(ord("G")) + " " + str(ord(":")) + " " + string_to_ascii(str(g))
        #Sending the generator to the sender
        w.write(ord_g)
        

def encryptor():
    #Obtaining the necessary information from the text, as first 4 line is F,
    #p, q and g.
    with open("text.txt", "r") as r:
        Fline = r.readline()[5:-1]
        hline = r.readline()[5:-1]
        qline = r.readline()[5:-1]
        gline = r.readline()[5:-1]

    delete = open("text.txt", "w")
    delete.close()
    
    
    F = int(ascii_to_string(Fline))
    h = int(ascii_to_string(hline))
    q = int(ascii_to_string(qline))
    g = int(ascii_to_string(gline)) 
    
    
    #The secret key k and shared key p
    k = random.randint(2, q-1)
    p = power_calculator_residue(g, k, F)
    
    msg = input("Enter your message: ")
    crp = encryption(h, k, F, msg)

    key_writer(F, p, q, g) 
    with open("text.txt", "a") as a:
        a.write("\n")
        for code in crp:
            a.write(str(code))
            a.write(" ")
    #The function returns the key as it will be needed later
    return k
        
        
def decryptor(b):
    #Obtaining the necessary information from the text, as first 4 line is F,
    #p, q and g, and the last line is the message.
    with open("text.txt", "r") as r:
        Fline = r.readline()[5:-1]
        pline = r.readline()[5:-1]
        qline = r.readline()[5:-1]
        gline = r.readline()[5:-1]
        mline = r.readline()
         

    F = int(ascii_to_string(Fline))
    p = int(ascii_to_string(pline))
    q = int(ascii_to_string(qline))
    g = int(ascii_to_string(gline))  
    
    skey = power_calculator_residue(p, b, F)
    
    mlist = mline.strip().split()
    ptext = ""
    for val in mlist:
        org = int(val)//skey
        char = str(chr(org))
        ptext += char
    print(ptext)
    
    
def key_generator():
    #Using algorithm 8.35 to generate primes with extremely high possibility. 
    #We want both q and 2*q+1 be prime to make things easier.
    for q in range(2**160, 2**161):
        if power_calculator_residue(2,q,q) == 2:
            if power_calculator_residue(2, 2*q+1, 2*q+1) == 2:
                break
    #Cyclic group is the quadratic residues in modulo 2*q+1, which is a prime number.
    #As q is also prime, order is a prime number (q) thus the secret keys of the receiver
    #and the sender will be relatively prime with the order of the group in any case.
    F = 2*q + 1
    return F, q
    
def generator_generator(F, q):
    #Take any number in modulo F and calculate the square of that in modulo F. 
    #As the order is a prime number, the result will always be a generator of the 
    #cyclic group. 
    root = random.randint(2, F-1)
    g = power_calculator_residue(root, 2, F)
    
    return g

def checker():
    empty = True
    with open("text.txt", "r") as r:
        line = r.readline()
        if line != "":
            empty = False
    return empty
 


flag = int(input("What is the purpose?\n1 for the receiver\n2 for the sender\n"))
textfile = open("text.txt", "w")
textfile.close()

if flag == 1:
    F, q = key_generator()
    g = generator_generator(F, q)
    #Receiver's secret key b and shared key h
    b = random.randint(2, q-1)
    h = power_calculator_residue(g, b, F)
    
    #Writing the pub key to text file to send it to the sender
    key_writer(F, h, q, g)
    while True:
        #Now it must scan the text continuously to see whether it received any message
        time.sleep(5)
        empty = checker()
        while empty:
            time.sleep(5)
            empty = checker()
        decryptor(b)
        #After receiving the message, the receiver becomes the sender.  
        b = encryptor()
    
    
if flag == 2:
    #The sender will check the document continuously until the receiver sends their pub key
    empty = checker()
    while empty:
        time.sleep(5)
        empty = checker()   
    #Once the receiver sends their pub key, the sender encrypts their message.
    k = encryptor()
        #After sending the message, the sender becomes the receiver
    while True:
        time.sleep(5)
        empty = checker()
        while empty:
            time.sleep(5)
            empty = checker() 
        decryptor(k)
        k = encryptor()
       

         

         


