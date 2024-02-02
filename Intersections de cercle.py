"""https://www.youtube.com/watch?v=bRIL9kMJJSc
Idées :
Tout d'abord créer la table de bool pour n cercles.
Il y a donc 2^n lignes.
Cette table montre toutes les intersections possibles.
Pour obtenir toutes les combinaisons d'intersection possible il faut valider ou invalider chaque ligne,
il y a donc 2^(2^n) combinaisons possibles.
Il faut ensuite (ou avant ?) supprimer les symmétriques.

On peut maintenant créer les contraintes pour résoudre en LP.
Inconnues : coordonnées des centres des cercles et leur rayon.
Intersection : distance entre les deux inférieure à la somme des rayons.
Non intersection : pareil mais supérieur.
Attention à ne pas autoriser les points de contact : < ou > et non pas <= ou >=
Jamais 3 cercles qui se touchent :
||C1-C2|| != r1 + r2
||C1-C3|| != r1 + r3
||C3-C2|| != r3 + r2


"""

from pyomo.environ import ConcreteModel, Var, Objective, Constraint, ConstraintList, SolverFactory
from pyomo.environ import Reals, PositiveReals, RangeSet, NonNegativeIntegers
from tkinter import *
import numpy as np

width=500
height=width
unite=50
x0=width//2
y0=height//2

rayon_moyen=0.8
distance_moyenne=0.2

cas=3
n=2

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
#print(table_de_verite(3))


def FindSol(table,combi):
    model = ConcreteModel()

    # Indices
    
    model.I = RangeSet(1, n)
    model.J = RangeSet(1, 2*n)

    # Variables
    #dans l'ordre pour chaque cercle
    model.rayons = Var(model.I,bounds=(0.05,10**5),initialize=1.0)
    model.coos = Var(model.J,within=Reals)
    model.d= Var(within=NonNegativeIntegers)

    #Cercle fixe
    model.rayons[1] = 1
    model.coos[1] = 0
    model.coos[2] = 0

    # Objective Function
    #Rapprocher les centres de 0,0
    #model.obj = Objective(expr=model.coos[3]**2 + model.coos[4]**2)
    #Rayons proches de la moyenne
    #model.obj = Objective(expr=(sum([1,model.rayons[2]])/2 - rayon_moyen)**2)
    #Distance entre cercle proche de la moyenne
    #model.obj = Objective(expr=model.d)
    #Distance et rayon proche de la moyenne
    model.obj = Objective(expr= (sum([1,model.rayons[2]])/2 - rayon_moyen)**2 + model.d)

    # Equations du système :
    model.system=ConstraintList()
    #Contrainte de distance moyenne qui sert pour l'objectif
    model.system.add(expr=model.d == sum([model.coos[3]**2 + model.coos[4]**2])/2 - distance_moyenne)

    #Définir la situation pour chaque paire de cercle
    #solo : si un cercle est présent seul, intersec : si les deux cercles sont en intersection
    solo1=True
    solo2=True
    intersec=True
    for ligne in range(2**n):
        if table[ligne,0] == 1 and table[ligne,1] == 0 and combi[ligne] == "0":
            solo1=False
        elif table[ligne,0] == 0 and table[ligne,1] == 1 and combi[ligne] == "0":
            solo2=False
        elif table[ligne,0] == 1 and table[ligne,1] == 1 and combi[ligne] == "0":
            intersec=False



    #cas 1
    if solo1 and solo2 and not intersec:
        model.system.add(expr=1.1*(1 + 2*model.rayons[2] + model.rayons[2]**2) <= model.coos[3]**2 + model.coos[4]**2)
    #cas 2
    elif not (solo1 and solo2) and intersec:
        model.system.add(expr=1 + 2*model.rayons[2] + model.rayons[2]**2 >= model.coos[3]**2 + model.coos[4]**2)
        model.system.add(expr=model.rayons[2] <= 1)
        model.system.add(expr=1 - 2*model.rayons[2] + model.rayons[2]**2 >= model.coos[3]**2 + model.coos[4]**2)
    #cas 3
    elif solo1 and solo2 and intersec:
        model.system.add(expr=1 + 2*model.rayons[2] + model.rayons[2]**2 >= model.coos[3]**2 + model.coos[4]**2)
        model.system.add(expr=1 - 2*model.rayons[2] + model.rayons[2]**2 <= model.coos[3]**2 + model.coos[4]**2)
    else:
        print("Erreur pas de cas trouvé")


    # Solve the model
    sol = SolverFactory('gurobi').solve(model, tee=False, options={"NonConvex":2})

    # CHECK SOLUTION STATUS

    # Get a JSON representation of the solution
    # sol_json = sol.json_repn()
    # Check solution status
    # if sol_json['Solver'][0]['Status'] != 'ok':
    #     return None
    # if sol_json['Solver'][0]['Termination condition'] != 'optimal':
    #     return None

    return Cercle(model.rayons[2](),model.coos[3](),model.coos[4]())


#il faut retirer les symétries et situations impossibles
table=table_de_verite(n)
print(table)
combinaisons=[]
for i in range(2**(2**n)):
    binaire=dectobi(i)
    #pas d'espace vide est impossible
    if len(binaire) < 2**n:
        continue
    #aucun cercle seul existant : impossible, il y en a au moins un
    non_existant=0
    for ligne in range(2**n):
        if sum(table[ligne,colonne] for colonne in range(n)) == 1 and binaire[ligne] == "0":
            non_existant+=1
    if non_existant == n:
        continue
    #si un cercle n'existe pas il doit être dans (= en intersection entière) avec un autre cercle
    continuer=False
    for ligne in range(2**n):
        if sum(table[ligne,colonne] for colonne in range(n)) == 1 and binaire[ligne] == "0":
            indice=[table[ligne,colonne] for colonne in range(n)].index(1)
            intersection=False
            for l in range(2**n):
                if sum(table[l,colonne] for colonne in range(n)) >=2 and table[ligne,indice] == 1 and binaire[l] == "1":
                    intersection=True
                    break
            if not intersection:
                continuer=True
                break
    if continuer:
        continue
    #print(binaire)
    
    combinaisons.append(binaire)

#symétrie : échanger deux colonnes, réordonner les lignes, comparer le binaire des intersections,
#s'il est déjà présent c'est une symétrie
#actuellement que pour le cas n=2
inverse=(0,1)
newTable=table_de_verite(n)
for i in range(2**n):
    newTable[i,inverse[0]] = table[i,inverse[1]]
    newTable[i,inverse[1]] = table[i,inverse[0]]
#print(newTable)
for binaire in combinaisons:
    tri=[]
    for i in range(2**n):
        ligne=""
        for j in range(n):
            ligne+=str(int(newTable[i,j]))
        tri.append((ligne,binaire[i]))
    tri.sort()
    #print(tri)
    binaire_tri=""
    for i in tri:
        binaire_tri+=i[1]
    #print(binaire_tri)
    
    if binaire!=binaire_tri and binaire_tri in combinaisons and binaire in combinaisons:
        combinaisons.remove(binaire_tri)

print(len(combinaisons), combinaisons)


solutions=[]
for combi in combinaisons:
    solutions.append(FindSol(table,combi))
for cercle in solutions:
    cercle.valeurs()

def affichage_suivant():
    global numero
    Canevas.delete(ALL)
    cercles=[solutions[numero]]
    cercles.append(Cercle(1,0,0))
    numero+=1

    for cercle in cercles:
        #print(cercle.valeurs())
        Canevas.create_oval(x0 + (cercle.x - cercle.r)*unite,y0 + (cercle.y - cercle.r)*unite,x0 + (cercle.x + cercle.r)*unite,y0 + (cercle.y + cercle.r)*unite)
        Canevas.create_oval(x0 + cercle.x*unite,y0 + cercle.y*unite,x0 + cercle.x *unite,y0 + cercle.y*unite)


fenetre=Tk()
#fenetre.attributes('-fullscreen', True)
fenetre.bind('<Escape>',lambda e: fenetre.destroy())

Canevas = Canvas(fenetre, width=width, height=height)
Canevas.pack()

Bouton1 = Button(fenetre, text = 'Quitter', command = fenetre.destroy)
Bouton1.pack()

Bouton_affiche = Button(fenetre, text = 'Suivant', command = affichage_suivant)
Bouton_affiche.pack()

numero=0

affichage_suivant()

fenetre.mainloop()

