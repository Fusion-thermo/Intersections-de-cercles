import numpy as np

class Cercle:
    def __init__(self,r,x,y):
        self.r=r
        self.x=x
        self.y=y
    def valeurs(self):
        print(round(self.r,2),round(self.x,2),round(self.y,2))

#décimal à binaire
def dectobi(a):
    t,b="1",0
    while 2**(b+1)<=a:
        b+=1
    a-=2**b
    for i in range(b-1,-1,-1):
        if a-2**i<0:
            t+="0"
        else:
            t+="1"
            a-=2**i
    return t

def table_de_verite(n):
    table=np.zeros((2**n,n))
    for dec in range(1,2**n):
        binaire=dectobi(dec)
        binaire="0"*(n-len(binaire)) + binaire
        for i in range(len(binaire)):
            if binaire[i]=="0":
                table[dec,i]=0
            else:
                table[dec,i]=1
    return table

