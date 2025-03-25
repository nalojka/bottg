import random
import telebot



def gen_pass(length):
    elements = "+-/*!&$#?=@<>123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    password = ""
    for i in range(length):
        password += random.choice(elements)
    return password

def orelreshka():
    flip = random.randint(1, 2)
    if flip == 1:
        return "ОРЕЛ"
    else:
        return "РЕШКА"
    
