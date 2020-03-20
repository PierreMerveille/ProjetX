from random import *
ships = {'tanker_0': {'coordinates': (15, 3), 'HP': 50, 'energy_point': 600, 'type': 'tanker', 'team': 1 }, 'cruiser_0': {'coordinates': (15, 3), 'HP': 100, 'energy_point': 400, 'type': 'cruiser', 
'team': 1 }}
peaks = {'peak1': {'coordinates': (10, 10), 'storage': 400}, 'peak2': {'coordinates': (10, 9), 'storage': 500}}
units_stats = {1: {'cruiser': {'range': 1, 'move': 10}, 'tanker': {'storage_capacity': 600}, 'hub': {'coordinates': (15, 3), 'HP': 1500, 'energy_point': 1500, 'regeneration': 25}}, 'fifi': {'cruiser': {'range': 1, 'move': 10}, 'tanker': {'storage_capacity': 600}, 'hub': {'coordinates': (1, 9), 'HP': 1500, 'energy_point': 1500, 'regeneration': 25}}, 'common': {'cruiser': {'max_energy': 400, 'cost_attack': 10, 'creation_cost': 100, 'attack': 1}, 'tanker': {'creation_cost': 50, 'move': 0}, 'hub': {'max_energy_point': 1500}}}
team = 1

def create_order(long, larg,  team, ships, units_stats,peaks) :
    nb_order = randint(1,30)
    order_list = []
    instruction_list =[]
    create_unit = {'tanker' : 0, 'cruiser' : 0}
    cruiser_list=[]

    for ship in ships :

        if ships[ship]['type'] == 'cruiser' and ships[ship]['team'] == team : 
            cruiser_list.append(ship)
    

    tanker_list = []
    for ship in ships :

        if ships[ship]['type'] == 'tanker' and ships[ship]['team'] == team : 
            tanker_list.append(ship)
    
    peak_coordinates =[]
    for peak in peaks :
        peak_coordinates.append (peaks[peak]['coordinates'])
    
    ship_list = tanker_list+ cruiser_list
    
    while nb_order != 0 :
        order = choice(['move', 'create','transfer','attack', 'upgrade'])
        order_list.append(order)
        nb_order -= 1

    
    
    for order in order_list :
        #create a ship
        if order == 'create' :
            instruction = choice(['tanker','cruiser'])

            #verify if a ship is already done or not                
            if len(instruction + '_list') == 0 :

                instruction_list.append(instruction + '_'+ str(team) +'_' + str(create_unit[instruction]) + ':' + instruction)
                
            else:
                number_tanker = (len(instruction + '_list') +create_unit[instruction])
                instruction_list.append( instruction + '_'+ str(team) +'_' + str(str(number_tanker)) + ':' + instruction)
                
            create_unit[instruction]+= 1
                        
        #transfer energy 
        elif order == 'transfer' and tanker_list != [] :
            order_type = choice(['draw','give'])
            
            if order_type == 'draw' :
                                
                    tanker = choice(tanker_list)
                    coordinates = []
                    output = choice(['hub','peak'])
                    if output == 'peak' :
                        coordinates= choice (peak_coordinates)
                        instruction_list.append(tanker + ':<' +str(coordinates[0]) + '-'+ str(coordinates[1]))
                    else : 
                        instruction_list.append(tanker + ':<hub')
                    
                    
            #elif order_type = give (à faire)
            if order_type == 'give':
               
                tanker = choice(tanker_list)
                coordinates = []
                Input = choice(['hub','ship'])
                if Input == 'hub' :
                        instruction_list.append(tanker + ':>hub')
                else : 
                    
                    cruiser = choice(cruiser_list)
                    coordinates = ships[cruiser]['coordinates']         
                
                    instruction_list.append(tanker + ':>' + str(coordinates[0]) + '-'+ str(coordinates[1]))

        elif order == 'attack' and cruiser_list != [] :
              
            cruiser = choice(cruiser_list)
            x=randint(1,long)
            y=randint(1,larg)
            damage=randint(1,ships[ship]['energy_point'])

            instruction_list.append(str(cruiser) + ':' + str(x) + '-' + str(y) + '=' + str(damage))
                    
        elif order == 'move' :
                        
            ship_in_movement= choice(ship_list)
            line = randint(0,long)
            column = randint(0,larg)
            instruction_list.append(ship_in_movement + ':@' + str(line) + '-' + str(column))

        elif order == 'upgrade' :
            order_type = choice(['regeneration', 'storage', 'move', 'range'])
            instruction_list.append('upgrade:' + order_type)

    instruction_str = ''
    for element in instruction_list :
        instruction_str += element +' '
    print (instruction_str)

               


create_order(15, 10,1,ships,units_stats,peaks)
