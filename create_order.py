from random import *
ships = {'tanker_0': {'coordinates': (15, 3), 'HP': 50, 'energy_point': 600, 'type': 'tanker', 'team': 1 }, 'cruiser_0': {'coordinates': (15, 3), 'HP': 100, 'energy_point': 400, 'type': 'cruiser', 
'team': 1 }}
peaks = {'peak1': {'coordinates': (10, 10), 'storage': 400}, 'peak2': {'coordinates': (10, 9), 'storage': 500}}
units_stats = {1: {'cruiser': {'range': 1, 'move': 10}, 'tanker': {'storage_capacity': 600}, 'hub': {'coordinates': (15, 3), 'HP': 1500, 'energy_point': 1500, 'regeneration': 25}}, 'fifi': {'cruiser': {'range': 1, 'move': 10}, 'tanker': {'storage_capacity': 600}, 'hub': {'coordinates': (1, 9), 'HP': 1500, 'energy_point': 1500, 'regeneration': 25}}, 'common': {'cruiser': {'max_energy': 400, 'cost_attack': 10, 'creation_cost': 100, 'attack': 1}, 'tanker': {'creation_cost': 50, 'move': 0}, 'hub': {'max_energy_point': 1500}}}
team = 1

def create_order() :
    nb_order = randint(1,30)
    order_list = []
    instruction_list =[]
    create_unit = {'tanker' : 0, 'cruiser' : 0}
    
    while nb_order != 0 :
        order = choice(['move', 'create','transfer','attack', 'upgrade'])
        order_list.append(order)
        nb_order -= 1

    
    
    
    for order in order_list :

        #create a ship
        if order == 'create' :
            instruction = choice(['tanker','cruiser'])
            
            #verify if a ship is already done or not
            occurence = 0 
            for  ship in ships:
                                
                if ships[ship]['type'] == instruction and ships[ship]['team'] == team :
                    occurence += 1
           
            if occurence == 0 :

                instruction_list.append(instruction + '_'+ str(create_unit[instruction]) + ':' + instruction)
                
            else:
                number_tanker = (occurence+create_unit[instruction])
                instruction_list.append( instruction + '_'+ str(str(number_tanker)) + ':' + instruction)
                
            create_unit[instruction]+= 1
                        
        #transfer energy
        elif order == 'transfer' :
            order_type = choice(['draw','give'])
            
            if order_type == 'draw' :
                tanker_list = []
                for ship in ships :
                    
                    if ships[ship]['type'] == 'tanker' and ships[ship]['team'] == team :
                        
                        tanker_list.append(ship)
                if tanker_list != []:

                    tanker = choice(tanker_list)
                    coordinates = []
                    output = choice(['hub','peak'])
                    if output == 'peak' :
                        for peak in peaks :
                            coordinates.append (peaks[peak]['coordinates'])
                        coordinates= choice (coordinates)
                    else : 
                        coordinates = units_stats [team]['hub']['coordinates']
                    
                    instruction_list.append(tanker + ':<' +str(coordinates[0]) + '-'+ str(coordinates[1]))
            #elif order_type = give (à faire)
        

        elif order == 'attack' :
            cruiser_list=[]
            for ship in ships :
                if ships[ship]['type'] == 'cruiser' and ships[ship]['team'] == team : 
                    cruiser_list.append(ship)
            
            if cruiser_list!=[]:
                cruiser = choice(cruiser_list)
                x=randint(1,long)
                y=randint(1,larg)
                damage=randint(1,ships[ship]['energy_point'])

                instruction_list.append(str(cruiser) + ':' + str(x) + '-' + str(y) + '=' + str(damage))
                    
        elif order == 'move' :
            for ship in ships :

                if ships[ship]['type'] == 'tanker' and ships[ship]['team'] == team : 
                    ship_list.append(ship)
            
            ship_in_movement= choice(ship_list)
            raw = randint(0,nbr_row)
            column = randint(0,nbr_column)
            instruction_list.append( ship_in_movement + ':@' + str(raw + '-' + column))
    print (instruction_list)

               


create_order()
