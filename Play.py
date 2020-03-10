# -*- coding: utf-8 -*-
from colored import*
print ('hello')
def play (map_title, team_1, team_2):
    """ Start the game and do the folowing function
    Parameter
    ----------
    map_tilte : name of the map file (str)
    team_1 : name of the team 1 (str)
    team_2 : name of the team 2 (str)
    
    Notes :
    --------
    The function start the game and do each phase with the function
    
    Versions
    --------
    specification : Pierre Merveille (v.1 24/02/20)
    """
     
    
    
    board, units_stats, max_upgrade, cost_upgrade, elements, color_team, ships, peaks = set_games(team_1, team_2, map_title)
    end_counter = 0
    
    while end_game(color_team, units_stats, end_counter) == False:
        for team in color_team:
            order = input("Let's get your order")
            upgrade_list , create_list, move_list, attack_list, transfer_list = separate_instruction(order, ships, units_stats, board)
            ships,board,units_stats = create_units(create_list, ships, team, board, units_stats)
           
            units_stats = upgrade(team, units_stats, ships, max_upgrade, cost_upgrade, upgrade_list)
            
            units_stats, ships, end_counter = attack(attack_list, board, units_stats, ships, team, end_counter)
            
            board, ships = move(move_list, ships, team, board, units_stats, peaks)
            
            ships, units_stats , peaks = transfer(transfer_list, ships, team, units_stats, peaks, board)
            
            round_end(board, end_counter, units_stats, peaks, elements, color_team, ships)
    
def set_games (team_1, team_2, map_title) :
    """
    Create all the environnement of the game. Takes the data contained in the file and initializes the data structure (variable)
    
    Returns :
    ---------
    ships : information of each ship (dict)
    board : dictionary where each coordinates gives a list with the character to display and a list of entities on this position (dict)
    units_states : states of each unit (dict)
    max_upgrade : tuple containing the values for each upgrade (tuple)
    cost_upgrade : tuple containing the price for each upgrade (tuple)
    peaks : dictionnary with informations about each peak (dict)
    
    Notes : 
    ------
    This function create the data structure like the representation of the board in data (dictionnary) and the states of the hub contains in the file, tuple of the upgrade, initialize
    the list of the ship (dictionnary) and the structures for the design containing the representation of the unit type (cruiser, tanker, peak, hub)

    
    Versions 
    --------
    specification :Merveille Pierre (v.1 23/02/20)
    specification :Merveille Pierre (v.2 28/02/20)

    """

    elements = {'hub' : '⚑' , 'cruiser': 'ѧ' , 'tanker' : 'ѫ' , 'peak' : 'ϟ'}
    color_team = {team_1 : fg(1), team_2: fg(4)}


    fh = open(map_title + ".txt",'r')
    lines= fh.readlines()
    board_dimension= lines[1][:-1].split(' ')
    long = int(board_dimension[0])
    larg = int(board_dimension[1])


    for x in range (1, long + 2):
        for y in range ( 1, larg + 2):
            if x==1 and y==1:
                board = {(x, y) : {'list_entity' : ['   ']}}
            else:
                board[(x, y)] = {'list_entity': ['   ']}



    units_stats  = {team_1 : { 'cruiser' : {'range' : 1 , 'move' : 10}, 'tanker': {'storage_capacity' : 600}, 'hub' :  {'coordinates' : 123, 'HP': 123, 'energy_point' :123, 'regeneration':123}},
                team_2 : { 'cruiser' : {'range' : 1 , 'move' : 10}, 'tanker': {'storage_capacity' : 600}, 'hub' :  {'coordinates' : 123, 'HP': 123, 'energy_point' :123, 'regeneration':123, }},
                'common' : {'cruiser' : {'max_energy' : 400, 'cost_attack' : 10, 'creation_cost' : 100, 'attack' : 1}, 'tanker' : {'creation_cost' : 50, 'move': 0}, 'hub': {'max_energy_point' : 0}}}


    for ligne in range (3, 5):
        info_hub = lines[ligne][:-1].split(' ')    
        if ligne == 3 :
            name_team = team_1
        else:
            name_team = team_2
            
        board[(int(info_hub[0]), int(info_hub[1]))]['list_entity'] = [name_team]
        
        
        units_stats[name_team]['hub']['coordinates'] = (int(info_hub[0]),int(info_hub[1]))
        units_stats[name_team]['hub']['HP'] = int(info_hub[2])
        units_stats[name_team]['hub']['energy_point'] =int(info_hub[3])
        units_stats[name_team]['hub']['regeneration'] = int(info_hub[4])
        units_stats['common']['hub']['max_energy_point'] = int(info_hub[3])


    
    for index in range (6, len(lines)):
        info_peak = lines[index][:-1].split(' ')
        
        name_entity = 'peak' + str(index-5)
        
        if index == 6:
            peaks = {name_entity : {'coordinates' : (int(info_peak[0]), int(info_peak[1])), 'storage' : info_peak[2]}}
        else:
            peaks[name_entity]= {'coordinates' : (int(info_peak[0]), int(info_peak[1])), 'storage' : info_peak[2]}
            
        board[(int(info_peak[0]), int(info_peak[1]))]['list_entity'] = [name_entity]

    
    
    max_upgrade = {'max_regen_upgrade' :  50,  'max_range_upgrade' : 5, 'max_travel_upgrade' : 5, 'max_capacity_upgrade' : 1200}
    cost_upgrade = {'cost _regen_upgrade' : 750, 'cost_range_upgrade' : 400, 'cost_travel_upgrade' : 500, 'cost_upgrade_capacity':600}

    
    ships ={}
    
    #ships ={'name' : {'coordinates' : , 'team' : , 'type' : , 'HP' : , 'energy_point': }
    board_display(board, color_team, ships, peaks, units_stats, elements)
    display_stats(elements,color_team,ships,units_stats,peaks)

    return board, units_stats, max_upgrade, cost_upgrade, elements, color_team, ships, peaks
   
def end_game ( color_team, units_stats, end_counter ): 

    """ Verify if game is finished 
    
    Parameters
    ----------
    color_team : dictionnary with the number of the team with the color of each team (dict)
    units_stats : get the structure points of each hub (dict)
    end_counter : number of rounds without attacks (float) (+ O,5 by round)

    Return :
    --------
    end : sets the game to finished depending on the structure points or number of pacific rounds (bool)
    
    Notes : 
    -------
    This function gets the end_counter from the attack function to verify end_counter >= 40 if yes end = True, else False
    It also gets the strucure points of each hub to verify structure points (hub) <= 0 if yes end = True, else False

    Versions
    --------
    specification : Kevin Schweitzer (v.1 24/02/20)
    
    """  
    #at beginning end is false
    end = False
    #verify while end is false, quit while if end is true

    #if end_counter >= 40 end is True
    if end_counter >= 40:
        end = True

    #for each team in color_team
    for team in color_team:
        #if structure points of hub <= 0 end is True
        if int(units_stats[team]['hub']['HP']) <= 0:
            end = True
    return end

def separate_instruction (order, ships, units_stats,board):
    """ 
    Separate the different instrcution in the order and separate the first part of the instruction from the second ( on the left of the ':' and then on the right ) and set it in a list with all the other instructions
    
    Parameter
    ---------
    order: order of the player (str)
    
    Return
    ------
    instructions_list : list with all the instrcution separate in two (list) 
    
    Notes 
    -----
    3 steps : 
        - split the instructions of the order
        - split the instructions in two part (in a list)
        - set the all the list in the instrcutions_list
    
    Version 
    -------
    specification : Rochet Johan (v.1 22/02/20)
    """
    upgrade_list = []
    create_list = []
    move_list= []
    attack_list= []
    transfer_list = []
    x_list =[]
    y_list =[]
    instructions_list= []

    # list the coordinates of the board to check after if the instrcutions are correct
    for key in board :
        # add the x-coordinates in x_list 
        if not str(key[0]) in x_list :
            x_list.append(str(key[0]))
        # add the y-coordinates in y_list 
        if not key[1] in x_list :
            y_list.append (str(key[1]))
    # cut the different instrcutions
    order_list = order. split (' ')
    instructions_list = []
    # cut the instruction in two part around the ':' if there is only one ':'
    for instruction in order_list :
        #check if there is only one ':'
        occurence = 0
        for element in instruction :
            if element == ':' :
                occurence += 1
        #add to instrcution_list if there is only one ':'
        if occurence == 1: 
            instruction = instruction.split (':')
            instructions_list.append(instruction)
        
       
    
    # determine the nature of the instruction and set it in a list if it's correct
    for order in instructions_list: 
        # check if it's an upgrade-instruction
        correct = False
        if order[0] == 'upgrade' :
           if order[1] == 'regeneration' or order[1] == 'range' or order[1] == 'move' or order[1] == 'storage':
            upgrade_list.append(order[1])
        
        # check if order[0] is a ship    
        elif order[0] in ships :
           
            
            # check if there is only one '-'in order[1]
            value = False
            for element in order[1] : 
                if element == '-'and value== False :
                    value = True
                elif element == '-' :
                    value= 'bad'
            # if there is only one '-', cut the coorinates in 2 round the '-'      
            if value == True:              
                coordinates = order[1][1:].split('-')
                # if it's an attack-instruction ==> handle with the attack_value (ex: *10-12=23)
                if order[1][0] == '*':
                    value= False
                    # check if there is only one '=' in coordinates[1]
                    for element in coordinates[1] :

                        if element == '='and value== False :
                            value = True

                        elif element == '=' :
                            value= 'bad'
                    # if there is only one '=', cut the coorinates[1] in 2 round the '=' 
                    if value == True : 
                        coordinate_y = coordinates[1].split('=')
                        #set the y-coordinate of the attack in coordinate[1]
                        coordinates[1] = coordinate_y[0]
                    
                # verify if the coordinates are in the board
                if coordinates[0] in x_list and coordinates[1] in y_list :
                    correct = True
            print (correct)
            #add to the move_list if it's a correct move 
            if order[1][0] == '@' and correct :
                move_list.append([order[0], order[1][1:]])
            # add to the attack_list if it's a correct attack
            elif order[1][0] == '*'and correct:
                attack_list .append([order[0], order[1][1:]])
            # add to the transfer_list if it's a good transfer
            elif (order[1][0] == '<' or order[1][0] == '>') and (correct or order[1][1:]== 'hub') :
                transfer_list.append( [order[0], order[1]])
        # add to the transfer_list if it's a good transfer from hub
        elif order[0] == 'hub' and order [1][1:] in ships:
            transfer_list.append([order[0][0], order[1]])
        # add to the create_list if it's a creation
        elif order[1]== 'tanker'or order[1]== 'cruiser':
            create_list.append([order[0], order[1]])
    print (create_list)
    print (attack_list)    
    return upgrade_list , create_list, move_list, attack_list, transfer_list
    
def create_units (create_list, ships, team, board, units_stats) :
    
    """ Creates new units in the team either a tanker or a cruiser and place it on the board
    
    Parameters
    ----------
    instruction : order from the create_list (list)
    ships : information of each ship (dict)
    team : number of the team which is playing (int)
    board : dictionary where each coordinates gives a list of entities on this position (dict)
        
    Returns :
    --------
    ships : dictionnary with the new added ship (dict)
    board : add new ship to the list of entities on this position (dict) 
    
    Notes : 
    -------
    This function will add a new ship in ships(dict) using the team. 
    It will determinate if the ship the player want to create is a cruiser or a tanker and gives it different attributes depending on its type
    Hub will always be shown on board but adds new ship to the list of entities on this position ( display_order : hub --> ship --> tanker)
    
    Versions
    --------
    specification : Johan Rochet (v.1 20/02/20) 
     
    """
    for instruction in create_list :
        coordinates = units_stats[team]['hub']['coordinates']
        # if you want to create a tanker
        if instruction [1] == 'tanker' and units_stats[team]['hub']['energy_point'] >= units_stats['common']['tanker']['creation_cost'] :

            energy_point = units_stats[team]['tanker']['storage_capacity'] 
            # add the tanker in the dico ships       
            ships[instruction[0]]= {'coordinates': coordinates , 'HP': 50, 'energy_point' : energy_point, 'type' : 'tanker', 'team' : team}
            # add the tanker in the list_entity of the board
            board[coordinates]['list_entity'].append (instruction[0])
            # sub the energy_point from the hub
            units_stats[team]['hub']['energy_point'] -= units_stats['common']['tanker']['creation_cost']

        elif  instruction [1] == 'cruiser' and units_stats[team]['hub']['energy_point'] >= units_stats['common']['cruiser']['creation_cost'] : 
            energy_point = units_stats['common']['cruiser']['max_energy'] 
            # add the cruiser in the dico ships 
            ships[instruction[0]]= {'coordinates': coordinates , 'HP': 100, 'energy_point' : 400, 'type' : 'cruiser', 'team' : team}
            # add the cruiser in the list_entity of the board
            board[coordinates]['list_entity'].append (instruction[0])
            # sub the energy_point from the hub
            units_stats[team]['hub']['energy_point'] -= units_stats['common']['cruiser']['creation_cost']
    
    return ships,board,units_stats
    
def upgrade (team, units_stats, ships, max_upgrade, cost_upgrade, upgrade_list):
   
    """ 
    Permanently upgrade units or hub caracteristics 
    
    Parameters
    ----------
    upgrade_list : upgrade order from the upgrade_list (list)   
    units_stats : dictionnary containing the stats of each unit (dict)
    max_upgrade : tuple containing the values for each upgrade (dict)
    cost_upgrade : tuple containing the price for each upgrade (tuple)
    team_name : player name (str)
    
    Return
    ------
    units_stats : update stats in dictionnary (dict)

    Notes
    -----
    Need to verify if player/team asking the upgrade has enough energy stored for this upgrade in their hub reserves. If false upgrade denied, If True upgrade       
  
    range : modify cruiser range by adding max_range_upgrade to the range in units_stats associated to the team asking the upgrade  
    move : modify cruiser move by max_travel_upgrade to the move in units_stats associated to the team asking the upgrade
    storage : modify tanker storage_capacity by adding max_capacity_upgrade to the storage_capacity in units_stats associated to the team asking the upgrade
    regeneration : modify hub regeneration per round by adding max_regen_upgrade to the regen in units_stats associated to the team asking the upgrade
       
    
    Versions
    --------
    specification : Kevin Schweitzer (v.1 20/02/20)
   
    """
    #verify for each team if they have enough energy in hub to do the requested upgrade
    #example for upgrade_list = ['regeneration', 'storage', 'move','range']
    #get upgrade_cost for requested upgrades
    for upgrade in upgrade_list:

            #if team has enough energy do requested upgrades, else print('caps(%s): you don't have enough energy stored in your hub')%team
            if upgrade == 'regeneration':
                regen_cost = cost_upgrade['cost_regen_upgrade'] 

                if units_stats[team]['hub']['regeneration'] < max_upgrade['max_regen_upgrade']:
                
                    if regen_cost <= units_stats[team]['hub']['energy_points']:
                        units_stats[team]['hub']['regeneration'] += 5
                        units_stats[team]['hub']['energy_points'] -= 700

            elif upgrade == 'storage':
                storage_cost = cost_upgrade['cost_capacity_upgrade']
                
                if units_stats[team]['tanker']['storage'] < max_upgrade['max_capacity_upgrade']:
                    
                    if storage_cost <= units_stats[team]['hub']['energy_points']:
                        units_stats[team]['tanker']['storage'] += 100
                        units_stats[team]['hub']['energy_points'] -= 600           
            
            elif upgrade == 'move':
                move_cost = cost_upgrade['cost_travel_upgrade']

                if units_stats[team]['cruiser']['move'] > max_upgrade['max_travel_upgrade']:

                    if move_cost <= units_stats[team]['hub']['energy_points']:
                        units_stats[team]['cruiser']['move'] -= 1
                        units_stats[team]['hub']['energy_points'] -= 500

            elif upgrade == 'range':
                range_cost = cost_upgrade['cost_range_upgrade']
                
                if units_stats[team]['cruiser']['range'] < max_upgrade['max_range_upgrade']:
                    
                    if range_cost <= units_stats[team]['hub']['energy_points']:
                        units_stats[team]['cruiser']['range'] += 1
                        units_stats[team]['hub']['energy_points'] -= 400
    return units_stats
                        
def attack (attack_list, board, units_stats, ships, team, end_counter):
    
    """Execute an attack on a chosen box
    
    Parameters
    ----------
    instruction : order from the attack_list (list)
    board : dictionary where each coordinates gives a list with the character to display and a list of entities on this position (dict)
    units_stats : dictionnary containing the stats of each unit (dict)
    ships : information of each ship (dict)
    team : number of the team which is playing (int)
    end_counter : number of rounds without attacks (float) (+ O,5 by round)
    
    Returns
    -------
    board : the same dictionnary but without the ship hit by the attack if the ship is destroyed (dict)
    ships : the same dictionnary but with less health for the ennemy ship that got attacked (ships)
    units_stats : the same dictionnary but with less health for the hub if he is attacked (board)
    end_counter : number of rounds without attacks (float) (+ O,5 by round)
    
    Notes
    -----
    Change the statut of the ship
    
    Versions
    --------
    specification : Anthony Pierard (v.1 20/02/20)
    """                       
    #Implementation of the function attack
    #Initialise the coordinate and the attack point
    #attack_point = coord_attack[1]
    for instruction in attack_list :

        coord_attack=instruction[1].split('=')
        coordinates= coord_attack[0].split ('-')
        #coordinates = tuple (x,y)
        coordinates = (int(coordinates[0]),int(coordinates[1]))
        #verify in another function if we have the range
        hithin_range = range_verification (units_stats, instruction[0], ships, coordinates, team)
        #create a list for delete cruiser
        cruiser_dead=[]
        #create a variable verify if something is hit
        hit=0
        
        #attacke if hithin_range is True
        if hithin_range :
            #verify the coordinates of all the ship
            for ship in ships :
                if ships[ship]['coordinates']==coordinates:
                    #change the value of the point of structure of the ship in the coordinate
                    ships = change_value(ship, units_stats, ships, peaks, int(coord_attack[1])*-1, 'HP', ennemy_team)
                    hit+=1
                    if ships[ship]['HP']<=0:
                        #stock a dead cruiser
                        cruiser_dead.append(ship)
                        #delete the ship for the dictionnary board
                        board[(coordinates[0],coordinates[1])]['list_entity'].remove(ship)
            for ship in cruiser_dead:
                del ships[ship]
            #verify if the ennemy hub is in the coordinates
            if units_stats[ennemy_team]['hub']['coordinates']==coordinates :
                #change the value of the point of structure of the ennemy's hub in the coordinate
                untis_stats=change_value('hub',units_stats, ships, peaks, int(coord_attack[1])*-1, 'HP', ennemy_team)
                hit+=1
                
            if units_stats[team]['hub']['coordinates']==coordinates :
                #change the value of the point of structure of the hub in the coordinate
                untis_stats=change_value('hub',units_stats, ships, peaks, int(coord_attack[1])*-1, 'HP', team)
                hit+=1
                #if units_stats[team]['hub']['HP']<=0:
            if hit==0 : 
                #if nothing is hit than increment the end_counter
                end_counter+=1
        else :
            end_counter+=1
    return units_stats, ships, end_counter
    
def move (instruction, ships, team, board, units_stats, peaks) :
    
    """ Move a ship on the board
    
    Parameters
    ----------
    instruction : order from the move_list (list)
    ships : information of each ship (dict)
    team : number of the team which is playing (int)
    board : dictionary where each coordinates gives a list of entities on this position (dict)
    units_stats : get the travel cost (dict)
    peaks : parameter of change_value (dict)
        
    Return :
    --------
    ships : dictonnary with the new coordinates of the ship (dict)
    board : update of the board (dict) 
    
    Notes : 
    -------
    This function moves a ship to the chosen position
    
    Versions
    --------
    specification : Pierre Merveille (v.1 20/02/20)
    
    """  
    for nbr_instruction in instruction:
        part_of_instruction = nbr_instruction.split(':')
        if part_of_instruction[0] in ships:
            order = part_of_instruction[1].strip('@')
            new_coord = order.split('-')
            old_coord = ships[part_of_instruction[0]]['coordinates']
            if ships[part_of_instruction[0]]['type'] == 'tanker':
                change_value(part_of_instruction[0], ships, peaks, new_coord, 'coordinates', units_stats)
                board[new_coord]['list_entity'] += part_of_instruction[0]
                board[old_coord]['list_entity'] -= part_of_instruction[0]

            else:
                if ships[part_of_instruction[0]]['energy_point'] < (((new_coord[0] - old_coord[0])**2 + (new_coord[1] - old_coord[1]))**0,5) * units_stats[team]['cruiser']['move'] :
                    print('Not enough energy_point in' + part_of_instruction[0])
                else:
                    change_value(part_of_instruction[0], ships, peaks, (((new_coord[0] - old_coord[0])**2 + (new_coord[1] - old_coord[1]))**0,5) * units_stats[team]['cruiser']['move'], 'energy_point', units_stats)
                    change_value(part_of_instruction[0], ships, peaks, new_coord, 'coordinates', units_stats)
                    board[new_coord]['list_entity'] += part_of_instruction[0]
                    board[old_coord]['list_entity'] -= part_of_instruction[0]

            print(part_of_instruction[0] + 'doesn t exist')
            
    return board, ships
            
def change_value ( entity_name, ships, peaks, new_value, caracteristic, units_stats, team):
    
    """
    Change the value of one of the caracteristic of the ship or the peak
    
    Parameters
    ----------
    entity_name : name of the entity for which you want to change a value (str)
    ships :  dictionnary with the statistics of ech ship (tanker or cruiser)(dict)
    peaks : dictionnary with all the peaks (dict)
    new_value : number of point to change (positive or negative) (int)
    caracteristic : caractrestic you want to change the value with the quantity (str)
    units_stats : dictionnary containing the stats of each unit (dict)
    team : name of the team which is playing (str)
    
    Return 
    ------
    ships : the dictionnary with the change of value for the caracteristic (dict)
    peaks : the dictionnary with the change of value for the caracteristic (dict)
    
    Notes 
    -----
    This function change a cracteristic of a ship or a peak
    This function is insert in the function 
    
    Version 
    -------
    specification : Johan Rochet (v.1 22/02/20)
    
    """
    
    #implementation of the function change value
    #change value for the hub
    if entity_name == 'hub' :
        #change the value in function of the caracteristic and return the dictionnary
        units_stats[team]['hub'][caracteristic] += new_value
        return units_stats
    else :
        #change the value for the ship 
        for ship in ships :
            #check all the name of the ship in ships
            if entity_name == ship :
                #condition if it's a coordinates because new_value is a tuple
                if caracteristic == 'coordinates' :
                    ships[entity_name]['coordinates'] = new_value
                else :
                    ships[entity_name][caracteristic] += new_value
                return ships
        #change value for the peak
        for peak in peaks:
            #check all the name of the peak in peaks
            if entity_name == peak :
                #condition if it's a coordinates because new_value is a tuple
                if caracteristic == 'coordinates' :
                    peaks[entity_name]['coordinates'] = new_value
                else :
                    peaks[entity_name]['storage'] += new_value
                return peaks
               
def transfer (transfer_list, ships, team, units_stats, peaks, board) :

    """ Fill a tanker's energy storage into a cruiser or into the hub 
        OR
        Fill the storage of a tanker with the energy of a peak or a hub

    Parameters
    ----------
    instruction : order from the transfer_list (list)
    ships : information of each ship (dict)
    team : number of the team which is playing (int)
    units_states : get the energy point of the hub (dict)
    peaks : dictionnary with all the peaks (dict)

    Return :
    --------
    ships : energy changed or/and storage change (dict)
    units_stats : energy point of the hub and capacity of tanker storage(dict) 
    peaks : dictionnary with the new or not value of storage of a peak (dict)

    Notes : 
    -------
    This function can place the energy of a tanker into a cruiser or into the hub 
    But it can also place the storage_energy of a peak into a tanker

    Versions
    --------
    specification : Pierre Merveille (v.2 24/02/20)
    """    
    # draw energy
    for instruction in transfer_list :
        if instruction [1][0] == '<':
            
            if ships[instruction[0]]['type'] == 'tanker':
                # in_dico = storage of the tanker 
                in_dico = ships[instruction[0]]['energy_point']
                # max_storage  = max stroage of a tanker 
                max_storage = units_stats[team]['tanker']['energy_point']
            # set all to 0 if it isn't a tanker 
            else :
                max_storage = 0
                in_dico = 0
                                
            # split and store the coordinates if it's a peak 
            if not instruction [1][1:] == 'hub' :
                
                instruction[1] = instruction[1][1:].split ('-')
                instruction[1][0] = int(instruction[1][0])
                instruction[1][1] = int(instruction[1][1])
                instruction[1] = tuple (instruction[1])
                
                
            #if the tanker draw energy in a peak 
            if instruction[1] in board :

                for peak in peaks : 
                    if peaks[peak]['coordinates'] == instruction[1] :
                        #transfer energy 
                        if max_storage > in_dico and range_verification(units_stats, instruction[0], ships,instruction[1],team ):
                            while in_dico < max_storage and peaks[peak]['storage'] >0 :
                    
                                in_dico += 1
                                peaks[peak]['storage'] -= 1
            #if the tanker draw energy in a hub
            elif instruction [1][1:] == 'hub' :
                out_dico =units_stats[team]['hub']['energy_point']
                #transfer energy
                if max_storage > in_dico and units_stats[team]['hub']['energy_point'] >0 and range_verification(units_stats, instruction[0], ships,units_stats[team]['hub']['coordinates'],team ):
            
                    while in_dico < max_storage and units_stats[team]['hub']['energy_point'] >0 :
                    
                        in_dico += 1
                        units_stats[team]['hub']['energy_point'] -= 1
            if ships[instruction[0]]['type'] == 'tanker':
                ships[instruction[0]]['energy_point'] = in_dico
                    
        #--------------------------------------------------------------------------------------------------------
        
        #give energy  to a ship or the hub    
        elif instruction [1][0] == '>' :
            if ships[instruction[0]]['type'] == 'tanker' :
                out_dico = ships[instruction[0]]['energy_point']
                
                if instruction[1][1:] in ships : 
                    if ships[instruction[1][1:]]['type']== 'cruiser' and range_verification(units_stats, instruction[0], ships,ships[instruction[1][1:]]['coordinates'], team) :

                        while ships[instruction[1][1:]]['energy_point'] < units_stats['common']['cruiser'] ['max_energy'] and out_dico > 0:
                            ships[instruction[1][1:]]['energy_point']
                            ships[instruction[1][1:]]['energy_point'] += 1 
                            out_dico -= 1
                        ships[instruction[0]]['energy_point'] = out_dico
                #give energy to a hub    
                elif  instruction[1][1:] == 'hub' and range_verification(units_stats, instruction[0], ships,units_stats[team][instruction[1][1:]]['coordinates'], team) :
                    print (5)
                    units_stats[team][instruction[1][1:]]['energy_point'] += out_dico
                    ships[instruction[0]]['eneegy_point'] = 0

           
    return ships, units_stats , peaks
        
def round_end (board, end_counter, units_stats, peaks, elements, color_team, ships):

    """ Print new board and stats and make "end of round changes" and do the regeneration of the hub energy
    
    Parameters  
    ----------
    ships : information of each ship (dict)
    board : get the structure points of each hub (int)
    unit_stats : stats of all entities (dict)
    peaks : stats of all peaks (dict)
    elements : character for each type of entity (dict)
    color_team : color for each team (dict)

    Return :
    --------
    unit_stats : every end of round changes energy amount stored in hub (dict)
    
    Notes : 
    -------
    This function changes the energy amount for each hub at the end of every round. The function also prints the board with all changes made during the current round.
    This function uses other fuctions like change_value, display_board and display_stats to display the board and stats after each rounds changes.

    Versions
    --------
    specification : Kevin Schweitzer (v.1 24/02/20)
    
    """    
    #add energy to hub every round end
    for team in color_team:
        print (team)
        print (units_stats)
        print (units_stats[team]['hub']['energy_point'])
        print (units_stats[team]['hub']['regeneration'])
        print (units_stats['common']['hub']['max_energy_point'])
        if units_stats[team]['hub']['energy_point'] + units_stats[team]['hub']['regeneration'] < units_stats['common']['hub']['max_energy_point']:
            change_value(team, 'hub', ships, peaks, units_stats[team]['hub']['regeneration'], 'energy_point')

    #display board every round end
    board_display(board, elements, color_team, ships, peaks, units_stats, elements)

    #display stats every round end
    display_stats (elements, color_team, ships, units_stats, peaks)
    
def select_value_to_print (board, coordinates, units_stats, ships, peaks, color_team, elements):
    """
    Select the character to print on the board  and its color

    Parameters
    ----------
    board : dictionnary with the coordinates of all boxes of the board which gives a list of element on this place (dict)
    element : dictionnary with the type of entity (cruiser, hub,...) with the charactere of each type (dict)
    color_team : dictionnary with the number of the team with the color of each team (dict)
    ships :  dictionnary with the statistics of ech ship (tanker or cruiser)(dict)
    peaks : dictionnary with all the peaks (dict)
    units_stats : get the location of each hub (dict)
    coordinates : tuple with the coordinate of the box

    Return
    ------
    value_to_print : character to print on a box with its color

    Version:
    --------
    specification : Johan Rochet (v1. 28/02/20)
    implementation : Johan Rochet (v1. 28/02/20)
    """
    
    if board[coordinates]['list_entity'] == ['   '] :
        
        
        value_to_print = ('   ')
        
    else : 
                
        value_to_print = [4]
        # select the units to display and the color of it. Order = hub-cruiser-tanker-peak
        for entity in board[coordinates]['list_entity']: 
           
            
            # first verifiy if the entity is a hub        
            if entity in units_stats : 
                team = color_team[entity]
                # set O and the color of the hub in value_to_print
                value_to_print = [0, team]
                
            # then check if it's a ship  
            if entity in ships: 
                #check if it's a cruiser
                if ships[entity]['type'] == 'cruiser':
                    # verify that ther is no hub already placed
                    if value_to_print[0] >0 :
                        team = ships[entity]['team']
                        color = color_team[team]
                        # set 1 and the color of the cruiser in value_to_print
                        value_to_print = [1,color]
                #check if it's a tanker        
                else : 
                    # verify that ther is no hub or cruiser  already placed
                    if value_to_print[0] >1 :
                        team = ships[entity]['team']
                        color = color_team[team]
                        # set 2 and the color of the tanker in value_to_print
                        value_to_print = [2,color]
            # finally check if it' a peak 
            elif entity in peaks : 
                # verify that ther is no hub, cruiser or tanker already placed
                if value_to_print[0] > 2 :
                    # set 2 and the color 'yellow' in value_to_print
                    value_to_print = [3, fg(10)+ attr(1)]
        # CHange the number in value_to_print by the type of entity it represents
        if value_to_print[0] == 0 :
            value_to_print[0] = 'hub'
        elif value_to_print[0] == 1 :
            value_to_print[0] = 'cruiser'
        elif value_to_print[0] == 2 :
            value_to_print[0] = 'tanker'
        elif value_to_print[0] == 3 :
            value_to_print[0] = 'peak' 
        # center the character in the box
        value_to_print[0] = ' '+ elements[value_to_print[0]] + ' '
        value_to_print = value_to_print[1] + value_to_print[0]
        
        
    
    
    return value_to_print
    
def board_display ( board, color_team, ships, peaks, units_stats, elements) :
    """ 
    Display the board 

    Parameters 
    ----------
    board : dictionnary with the coordinates of all boxes of the board which gives a list of element on this place (dict)
    element : dictionnary with the type of entity (cruiser, hub,...) with the charactere of each type (dict)
    color_team : dictionnary with the number of the team with the color of each team (dict)
    ships :  dictionnary with the statistics of ech ship (tanker or cruiser)(dict)
    peaks : dictionnary with all the peaks (dict)
    units_stats : get the location of each hub (dict)    

    Notes : 
    -------

    This function create boxes in a "damier" so that the players can easily see the difference between each boxes
    The board is surrounded by a "bordure" which contains the numbers of the boxes as when you play chess 

    Version 
    -------
    specification : Johan Rochet (v.1 22/02/20)
    """
    larg = 0
    long = 0
    bord = fg(255)
    for coordinates in board :
        if coordinates[1] > larg :
            larg = coordinates[1]
        if coordinates[0] > long :
            long = coordinates[0]
    # creation of the board
    for i in range (1, larg+2):
        #jump for each row
        bord += bg(0) + '\n'
        
        if i == 1 or i == larg +1 :
            #first and last row
            for j in range (1, long+1):
                #begin
                if j == 1 :
                    bord += bg('6')+'   ' + str(j)+'  '
                #end
                elif j == long :
                    bord+= bg('6') +'   '
                #column < 10        
                elif j<10:
                    bord+= bg(6)+str(j) +'  '
                #column < 100   
                else :
                    bord += bg(6) + str(j)+ ' '
            
        else : 
            
            #intermediate rows
            for j in range (1, long+2):
                #begin and end
                if j==1 or j==long+1:
                    bord += bg('6') + str(i-1) 
                    if i<11 : 
                        #begin
                        bord+= '  '
                    else:
                        #end
                        bord += ' '+ bg('0')
                else :
                    #grid
                    if (i+j) % 2 == 0 :
                        color= bg('231')
                    else : 
                        color = bg('115')
                    # add the character and the front color of the character and reset color to white after
                    bord += color + select_value_to_print(board, (j-1,i-1),units_stats,ships,peaks, color_team,elements)  + attr(0) + fg('255')
    bord += bg('0')       
    print(bord) 
        
def display_stats (elements, color_team, ships, units_stats, peaks):
    """
    Displays the statistics of all the ships, peaks and hubs
    
    Parameters
    ----------
    elements : dictionnary with type name and character associated (dict)
    color_team : dictionnary with team name and color associated (dict)
    ships : dictionnary with the statistics of each ship (dict)
    units_stats : dictionnary of the common statistics of each types of ship (dict)
    peaks : dictionnary with the statistics of each peak of energy (dict)
    
    Notes 
    -----
    This function displays the statistics of the peaks, the hub and all the ship on the board so that the player knows wich ship is placed on which boxes
    This function is only there to help the player managing/memorising the environnement, the name and all the stats of the ships in his own team as in the adverse team
    
    Version 
    -------
    specification : Johan Rochet (v.1 22/02/20)
    implementation : Kevin Schweitzer (v.1 28/02/20)
    
    """
    #color legend for each team
    print('\n')
    for element in color_team :
        print (color_team[element] + '[' + element + '] : \u2588\u2588') 
    #change color back to white

    ##############HUBS#################
    print(fg(255)+'\nHUBS')
    print('------------------------------')
    #for each team get hub stats
    for team_name in color_team : 
        stats = units_stats[team_name]['hub']
        
        #for each hub display stats
        hub_stats = ''
        for stat in stats :
            value = str(stats[stat])
            if stat == 'coordinates':
                stat = color_team[team_name] + '⯐ '

            elif stat == 'HP':
                stat = '❤ '

            elif stat == 'energy_point':
                stat = '⚡  '

            elif stat == 'regeneration':
                stat = '🔌  '

            hub_stats += stat +': ' + value + '   '    
        
        print(hub_stats)

    ##############Peaks###############
    print(fg(255)+'\nPEAKS')
    print('------------------------------')
    #for each peak get stats
    for stat in peaks : 
        stats = peaks[stat]

        #for each peak display stats
        peak_stats = ''
        for stat in stats :
            
            value = str(stats[stat])
            if stat == 'coordinates':
                stat = '⯐ '

            elif stat == 'storage':
                stat = '⚡  '

            peak_stats += stat + ': ' + value + '   '    

        print(peak_stats)

    ##############SHIPS################
    print(fg(255)+'\nSHIPS')
    print('------------------------------')
    #for each team get tanker stats from units_stats
    for team_name in color_team:
        team_stats = units_stats[team_name]['tanker']
        common_stats = units_stats['common']['tanker']  
        
        #for each tanker get stats from ships 
        for tanker in ships : 
            if ships[tanker]['type'] == 'tanker': #verify it's a tanker
            
                for ship in ships:
                
                    ship_stats = ships[ship]
                
                    for team_stat in team_stats:
                    
                        value = str(team_stats[team_stat])
                        if team_stat == 'storage_capacity':
                            stat_team = color_team[team_name] + '💼  ' 
                        tanker_stats_1 = stat_team +': ' + value + '   '         
                    
                    for common_stat in common_stats :

                        value = str(common_stats[common_stat])
                        if common_stat == 'creation_cost':
                            stat_common = color_team[team_name] + '💵  '
                            
                        elif common_stat == 'move':
                            stat_common = '⛽ '

                        tanker_stats_2 = stat_common +': ' + value + '  '
                        
                    for ship_stat in ship_stats:

                        value = str(ship_stats[ship_stat])
                        if ship_stat == 'coordinates':
                            stat_ship = color_team[team_name] + '⯐ '
                        
                        elif ship_stat == 'team':
                            stat_ship = '👤 '

                        elif ship_stat == 'type':
                            stat_ship = 'ѧ/ѫ'
                        
                        elif ship_stat == 'HP':
                            stat_ship = '❤ '

                        elif ship_stat == 'energy_point':
                            stat_ship = '⚡  '

                        tanker_stats_3 = stat_ship +': ' + value + '  '

    #get common stats from unit_stats
    common_stats = units_stats['common'] 
    for type in common_stats:
        #put common stats in different variables (tanker_common or cruiser_common)
        if  type == 'tanker':

            value = str (common_stats[type]['creation_cost'])
            tanker_common = ' | $:' + value

            value = str (common_stats[type]['move'])
            tanker_common += ' | ⛽ :' + value

        elif type == 'cruiser':
            
            value = str (common_stats[type]['creation_cost'])
            cruiser_common = ' | $:' + value

            value = str (common_stats[type]['cost_attack'])
            cruiser_common += ' | $/\u204c :' + value

            value = str (common_stats[type]['attack'])
            cruiser_common += ' | \u204c :' + value

            value = str (common_stats[type]['max_energy'])
            cruiser_common += ' | Max⚡ :' + value

            

    tanker_common += ' ]'
    cruiser_common += ' ]'                    

    team_stats ={}
    #for each team get tanker and cruiser stats depending on team
    for team_name in color_team:
            
        tanker_stats = units_stats[team_name]['tanker']
        cruiser_stats = units_stats[team_name]['cruiser']
        
        #for each key change icon and associate it to value
        value = str(tanker_stats['storage_capacity'])
        tanker_team_stats = ' | \U0001F50B :' + value

        value = str(cruiser_stats['range'])
        cruiser_team_stats  = ' | \u2B57 :' + value

        value = str (cruiser_stats['move'])
        cruiser_team_stats += ' | ⛽ :' + value

        team_stats[team_name] = {'cruiser_stats' : cruiser_team_stats, 'tanker_stats' : tanker_team_stats }
        
    ship_cruiser_stats =''
    ship_tanker_stats = ''

    ship_team ={}
    for team in color_team :
        ship_team[team] = {'cruiser' : [], 'tanker': []}

    for ship in ships:
        ship_stats = ship 

        value = str(ships[ship]['coordinates'])
        ship_stats += ': [ ⯐ :' + value
        
        value = str(ships[ship]['HP'])
        ship_stats += ' | ❤ :' + value
        
        value = str(ships[ship]['energy_point'])
        ship_stats += ' | ⚡  :' + value

        if ships[ship]['type'] == 'cruiser':
            value = elements['cruiser']
            ship_cruiser_stats = ship_stats + ' | type :' + value 
            ship_team[ships[ship]['team']]['cruiser'].append(ship_cruiser_stats) 
            
        elif ships[ship]['type'] == 'tanker':
            value = elements['tanker']
            ship_tanker_stats = ship_stats + ' | type :' + value 
            ship_team[ships[ship]['team']]['tanker'].append(ship_tanker_stats)

    #for each team get cruiser and tanker info from list in ship_team
    for team in color_team: 
        print(color_team[team])
        
        for cruiser in ship_team[team]['cruiser']:
            print(cruiser + team_stats[team]['cruiser_stats'] + cruiser_common)
        
        for tanker in ship_team[team]['tanker']:
            print(tanker + team_stats[team]['tanker_stats'] + tanker_common)

    print(fg(255))   
    
def range_verification (units_stats, ship_name, ships, coordinates):

    """  Verify if the ship can attend the box 

    Parameters
    ----------
    units_stats :dictionnary of the common statistics of each types of ship (dict)
    ship_name : name of the ship (str)
    ships :  dictionnary with the statistics of ech ship (tanker or cruiser)(dict)
    coordinates : coordinates of the box to attend (tuple)

    Return 
    ------
    hithin_range : true if coordinates are in range and False if not (bool)

    Notes
    -----
    This function is used for the move of the cruiser and the trnasfer of the tanker to verify if the coordinates are within the range of them (for the tanker: range = 1)

    Versions
    --------
    specification : Johan Rochet (v.1 24/02/20)
    """
    if abs(coordinates[0]-ships[ship_name]['coordinates'][0])+abs(coordinates[1]-ships[ship_name]['coordinates'][1]) <= units_stats[team]['cruiser']['range'] :
        return True
    else :
        return False

play('fichier', 'teamdegroslulu', 'fifi')