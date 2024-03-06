import numpy as np

class Cercle:
    def __init__(self,r,x,y):
        self.r=r
        self.x=x
        self.y=y
    def valeurs(self):
        print("R : {} X : {} Y : {}".format(round(self.r,2),round(self.x,2),round(self.y,2)))

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
            if binaire[i]=="1":
                table[dec,i]=1
    return table

class DuoCercles:
    def __init__(self,id1,id2,solo1,solo2,solo3,intersection,intersection13,intersection23):
        self.id1=id1
        self.id2=id2
        self.solo1=solo1
        self.solo2=solo2
        self.solo3=solo3
        self.intersection=intersection
        self.intersection13=intersection13
        self.intersection23=intersection23