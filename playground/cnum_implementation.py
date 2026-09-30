import sys
def deci(x):
    string = ""
    for i in x:
        temp_string = f"{ord(i):03d}"  
        string += temp_string  
    string += f"{len(x):04d}"  
    return int(string)  
    
def ascii(number):
    length_code = str(number)[-4:]
    deci_code = str(number)[:-4]
    if len(deci_code) % 3 != 0:
        deci_code = deci_code.zfill(len(deci_code) + (3 - len(deci_code) % 3))
    parts = [int(deci_code[i:i+3]) for i in range(0, len(deci_code), 3)]
    string = ""
    for i in parts:
        string += chr(i)
    return string

if len(sys.argv) < 2:
    word = "carbonscript"
else:
    word = sys.argv[1]

decimal = (deci(word))
length_code = str(decimal)[-4:]
deci_code = str(decimal)[:str(decimal).rfind(length_code)]
print("Carbon Number:",decimal)
print("Lenght Code:  ",length_code)
print("Decimal Code: ",deci_code)
print("Ascii Value:  ",ascii(str(decimal)))

