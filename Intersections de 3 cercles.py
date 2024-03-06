"""https://www.youtube.com/watch?v=bRIL9kMJJSc
Idées :
Tout d'abord créer la table de bool pour n cercles.
Il y a donc 2^n lignes.
Cette table montre toutes les intersections possibles.
Pour obtenir toutes les combinaisons d'intersection possible il faut valider ou invalider chaque ligne,
il y a donc 2^(2^n) combinaisons possibles.
Il faut ensuite supprimer les symmétriques.

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
from pyomo.environ import Reals, RangeSet, NonNegativeIntegers
from tkinter import *
from Fonctions import *

width=500
height=width
unite=150
x0=width//2
y0=height//2

rayon_moyen=0.8
distance_moyenne=0.2

n=3

def FindSol(table,combi):
    model = ConcreteModel()

    # Indices
    
    model.I = RangeSet(1, n)

    # Variables
    #dans l'ordre pour chaque cercle
    model.rayons = Var(model.I,bounds=(0.05,10**5),initialize=1.0)
    model.x = Var(model.I,within=Reals)
    model.y = Var(model.I,within=Reals)
    model.xp = Var(within=Reals)
    model.yp = Var(within=Reals)
    model.d = Var(within=Reals)

    #Cercle fixe
    model.cercle_fixe=ConstraintList()
    model.cercle_fixe.add(expr=model.rayons[1] == 1)
    model.cercle_fixe.add(expr=model.x[1] == 0)
    model.cercle_fixe.add(expr=model.y[1] == 0)

    # Objective Function
    #Rapprocher les centres de 0,0
    #model.obj = Objective(expr=model.x[3]**2 + model.y[3]**2)
    #Rayons proches de la moyenne
    #model.obj = Objective(expr=(sum([1,model.rayons[2]])/2 - rayon_moyen)**2)
    #Distance entre cercle proche de la moyenne
    #model.obj = Objective(expr=model.d)
    #Rayon et distance proches de la moyenne
    model.obj = Objective(expr= (sum(model.rayons[i] for i in model.I)/n - rayon_moyen)**2 + model.d)

    # Equations du système :
    model.system=ConstraintList()
    #Contrainte de distance moyenne qui sert pour l'objectif
    model.system.add(expr=model.d == sum(model.x[i]**2 + model.y[i]**2 for i in model.I)/n - distance_moyenne)

    #Définir la situation pour chaque paire de cercle
    #solo : si un cercle est présent seul, intersec : si les deux cercles sont en intersection
    solo1,solo2,solo3,intersec12,intersec13,intersec23,triple=False,False,False,False,False,False,False
    if combi[1] == "1":
        solo1=True
    if combi[2] == "1":
        solo2=True
    if combi[4] == "1":
        solo3=True
    if combi[3] == "1":
        intersec12=True
    if combi[5] == "1":
        intersec13=True
    if combi[6] == "1":
        intersec23=True
    if combi[7] == "1":
        triple=True
    print(solo1,solo2,solo3,intersec12,intersec13,intersec23,triple)
        
    duos=[DuoCercles(1,2,solo1,solo2,solo3,intersec12,intersec13,intersec23),DuoCercles(1,3,solo1,solo3,solo2,intersec13,intersec12,intersec23),DuoCercles(2,3,solo2,solo3,solo1,intersec23,intersec12,intersec13)]
    model.coosTripleIntersection=ConstraintList()
    model.coosTripleIntersection.add(expr = model.xp == sum(model.x[i] for i in model.I)/n)
    model.coosTripleIntersection.add(expr = model.yp == sum(model.y[i] for i in model.I)/n)


    for duo in duos:
        #séparés s'ils ne sont pas en intersection et qu'il n'y a pas de point triple
        if not duo.intersection and not triple:
            #étendu : model.system.add(expr=1.1*(model.rayons[duo.id1]**2 + 2*model.rayons[duo.id1]*model.rayons[duo.id2] + model.rayons[duo.id2]**2) <= (model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2)
            model.system.add(expr=1.1*(model.rayons[duo.id1] + model.rayons[duo.id2])**2 <= (model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2)
        #en intersection
        #(intersection et aucun n'existe solo [donc imbriqués dans le troisième]) ou (intersection et ils existent chacun solo)
        elif (not duo.solo1 and not duo.solo2) or (duo.solo1 and duo.solo2):
            model.system.add(expr=(model.rayons[duo.id1] + model.rayons[duo.id2])**2 >= (model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2)
            model.system.add(expr=(model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2 >= (model.rayons[duo.id1] - model.rayons[duo.id2])**2)
        #imbriqués
        #intersection avec seulement l'un des deux qui existe solo
        elif (duo.solo1 and not duo.solo2) or (not duo.solo1 and duo.solo2):
            if not duo.solo3:#si le 3è n'est pas solo alors celui de l'intersection actuelle qui n'est pas solo va être imbriqué dans celui qui l'est
                model.system.add(expr=(model.rayons[duo.id1] + model.rayons[duo.id2])**2 >= (model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2)
                if duo.solo1:
                    model.system.add(expr = model.rayons[duo.id2] <= model.rayons[duo.id1])
                    model.system.add(expr=(model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2 <= (model.rayons[duo.id1] - model.rayons[duo.id2])**2)
                else:
                    model.system.add(expr = model.rayons[duo.id2] >= model.rayons[duo.id1])
                    model.system.add(expr=(model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2 <= (model.rayons[duo.id2] - model.rayons[duo.id1])**2)
            elif duo.solo3:#alors celui de l'intersection actuelle qui n'est pas solo va être imbriqué dans celui qui l'est si il n'est pas également en intersection avec le 3è.
                if duo.solo1:
                    if not intersec23:
                        model.system.add(expr=(model.rayons[duo.id1] + model.rayons[duo.id2])**2 >= (model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2)
                        model.system.add(expr = model.rayons[duo.id2] <= model.rayons[duo.id1])
                        model.system.add(expr=(model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2 <= (model.rayons[duo.id1] - model.rayons[duo.id2])**2)
                else:
                    if not intersec13:
                        model.system.add(expr=(model.rayons[duo.id1] + model.rayons[duo.id2])**2 >= (model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2)
                        model.system.add(expr = model.rayons[duo.id2] >= model.rayons[duo.id1])
                        model.system.add(expr=(model.x[duo.id1]-model.x[duo.id2])**2 + (model.y[duo.id1]-model.y[duo.id2])**2 <= (model.rayons[duo.id2] - model.rayons[duo.id1])**2)
        else:
            print("Erreur pas de cas trouvé")
    if triple:
        model.system.add(expr=(model.x[1]-model.xp)**2 + (model.y[1]-model.yp)**2 <= model.rayons[1])
        model.system.add(expr=(model.x[2]-model.xp)**2 + (model.y[2]-model.yp)**2 <= model.rayons[2])
        model.system.add(expr=(model.x[3]-model.xp)**2 + (model.y[3]-model.yp)**2 <= model.rayons[3])
    #et pour forcer le non triple ? seul l'un des trois peut être mis en contrainte inverse à ci-dessus


    # Solve the model
    SolverFactory('gurobi').solve(model, tee=False, options={"NonConvex":2})

    return [Cercle(model.rayons[i](),model.x[i](),model.y[i]()) for i in model.I]


table=table_de_verite(n)
print(table)
"""
#je commente ça car je ne trouve pas toutes les règles pour réduire les combinaisons (actuellement 28 au lieu de 14)
#il faut retirer les symétries (normalement fait) et situations impossibles (visiblement il manque au moins 1 règle : 28 au lieu de 14)

combinaisons=[]
for i in range(2**(2**n)):
    binaire=dectobi(i)
    #pas d'espace vide est impossible
    if len(binaire) < 2**n:
        continue
    #aucune portion de cercle seule existante : impossible, il y en a au moins une
    non_existant=0
    for ligne in range(2**n):
        if sum(table[ligne,colonne] for colonne in range(n)) == 1 and binaire[ligne] == "0":
            non_existant+=1
    if non_existant == n:
        continue
    #si un cercle n'existe pas seul il doit être dans (= en intersection entière) avec un autre cercle
    continuer=False
    for ligne in range(2**n):
        if sum(table[ligne,colonne] for colonne in range(n)) == 1 and binaire[ligne] == "0":
            indice=[table[ligne,colonne] for colonne in range(n)].index(1)
            intersection=False
            for l in range(2**n):
                if sum(table[l,colonne] for colonne in range(n)) >=2 and table[l,indice] == 1 and binaire[l] == "1":
                    intersection=True
                    break
            if not intersection:
                continuer=True
                break
    if continuer:
        continue
    #si deux cercles ne sont pas intersection il ne peut pas y avoir une triple intersection : faux
    for ligne in range(2**n):
        if sum(table[ligne,colonne] for colonne in range(n)) == 2 and binaire[ligne] == "0" and binaire[-1] == "1":
            continuer=True
            break
            
    if continuer:
        continue
    #print(binaire)
    
    combinaisons.append(binaire)

#symétrie : échanger deux colonnes, réordonner les lignes, comparer le binaire des intersections,
#s'il est déjà présent c'est une symétrie
permutations=[(1,0,2),(2,1,0),(0,2,1)] + [(2,0,1),(1,2,0)]
for binaire in combinaisons:
    for permut in permutations:
        newTable=table_de_verite(n)
        #échange de 2 colonnes
        for i in range(2**n):
            newTable[i,0] = table[i,permut[0]]
            newTable[i,1] = table[i,permut[1]]
            newTable[i,2] = table[i,permut[2]]
        #print(newTable)
        #tri par ordre croissant des lignes
        tri=[]
        for i in range(2**n):
            ligne=""
            for j in range(n):
                ligne+=str(int(newTable[i,j]))
            tri.append((ligne,binaire[i]))
        tri.sort()
        #print(tri)
        #nouveau code binaire
        binaire_tri=""
        for i in tri:
            binaire_tri+=i[1]
        #print(binaire_tri)
        
        if binaire!=binaire_tri and binaire_tri in combinaisons:
            combinaisons.remove(binaire_tri)

print(len(combinaisons), *combinaisons)
for i in combinaisons:
    print(i) """

combinaisons=["11101000","11111010","11100010","10001011","10001110","10011111","11111000","11111111","11111110","11110010","11110011","11110001","11110111","11101111"]

def affichage_suivant():
    global numero
    #numero=12
    Canevas.delete(ALL)
    cercles=FindSol(table,combinaisons[numero])
    numeroT.set(str(numero+1))
    binaire.set(combinaisons[numero])

    i=0
    couleurs=["blue","red","green"]
    for cercle in cercles:
        cercle.valeurs()
        #print(cercle.valeurs())
        Canevas.create_oval(x0 + (cercle.x - cercle.r)*unite,y0 + (cercle.y - cercle.r)*unite,x0 + (cercle.x + cercle.r)*unite,y0 + (cercle.y + cercle.r)*unite,outline=couleurs[i])
        Canevas.create_oval(x0 + cercle.x*unite,y0 + cercle.y*unite,x0 + cercle.x *unite,y0 + cercle.y*unite) #centre
        i+=1
    numero+=1
    print("\n")
    if numero==len(combinaisons):
        fenetre.destroy()


fenetre=Tk()
fenetre.bind('<Escape>',lambda e: fenetre.destroy())

Canevas = Canvas(fenetre, width=width, height=height)
Canevas.pack()

Bouton1 = Button(fenetre, text = 'Quitter', command = fenetre.destroy)
Bouton1.pack()

Bouton_affiche = Button(fenetre, text = 'Suivant', command = affichage_suivant)
Bouton_affiche.pack()

numeroT=StringVar()
Label(fenetre,textvariable=numeroT).pack()
numeroT.set("")

binaire=StringVar()
Label(fenetre,textvariable=binaire).pack()
binaire.set("")

numero=0

affichage_suivant()

fenetre.mainloop()

