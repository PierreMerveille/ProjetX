from random import * 
a=[13,6,8,7,5,8,14]

def order(a) :
    
    b= []
    c=[]
    if len(a) <= 1 :
        return a
    if len(a) == 2 :
        if a[0]> a[1] :
            swap = a[0]
            a[0]= a[1]
            a[1]= swap
        return a
    else :
        index = randint (0, len(a)-1)
        
        pivot= a[index]
        del(a[index])
        for element in a :
            if element < pivot : 
                b.append(element)
                
            else :
                c.append(element)
        
        return order(b)+ [pivot]+ order(c)
print (order(a))

