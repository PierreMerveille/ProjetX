#At game start create tanker and tranfer energy back into hub

""" general function """

def order_AI (team,ships,units_stats,peaks, ennemy_team, AI_stats) : 
    """ 
    Main fonction to get the IA orders 

    Parameters 
    ----------
    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    peaks : dictionary with all the peaks (dict)
    ennemy_team : name of the ennemy_team (str)
    AI_stats: dictionary of the specific information for the AI(s)

    Return : 
    --------
    AI_order : order from the AI

    Version :
    ---------
    specification : Johan Rochet (v.1 25/04/20)
    
    """
    alive_tanker, alive_cruiser = create_selected_list_from_ships(ships,team)
    alive_ennemy_tanker, alive_ennemy_cruiser = create_selected_list_from_ships(ships,ennemy_team)
    grouped_peaks, peak_name = find_grouped_peaks(team, peaks, units_stats)
    stance,total_peak_energy,our_total_peak_energy, favorable_peaks= stance (ships)
    
    if stance == 'control' :
        
        
        while units_stats[team]['hub']['energy_point'] > units_stats['Common']['tanker']['creation_cost'] : 
            if AI_stats[team]['nb_tanker'] != 4 or AI_stats[team]['nb_cruiser'] >0 :
                instruction = create_IA_ship('tanker',team,'nb_tanker',AI_stats)
            #create a security_cruiser
            else :
                instruction = create_IA_ship('cruiser',team,'nb_cruiser',AI_stats)
        
        transfer_instruction = AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,peak_name)

        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team)

        alert_ennemy_close_to_our_peak(favorable_peaks, units_stats, peaks, ships, ennemy_team)         
        
        # Attaquer l'intrus


        
         

    elif stance == 'offensive':
        attack_cruiser()
        
        ### note à l'attention de ce très cher Anthony, idée: attaquer en priorité un croiseur ayant plus d'énergie que les qutres et aussi ceux avec le moins d'HP
    elif stance == 'defensive' :
        attack_tanker(stance,AI_stats,ships,units_stats,team,ennemy_team,alive_tanker,alive_ennemy_tanker,alive_ennemy_tanker, alive_ennemy_cruiser)
        defense_()
    
    coordinates_to_go (ships)

def stance(ships, team, ennemy_team, peaks, units_stats, AI_stats,alive_tanker, alive_cruiser,alive_ennemy_tanker, alive_ennemy_cruiser):
    """Decide if the adopted stance by the AI should be defensive or offensive

    Parameters
    ----------

    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    team : name of the team which is playing (str) 
    ennemy_team : name of the ennemy_team (str)

    Return
    ------

    stance : sets the stance to adopt by the AI
    """
    

    control_is_worth, our_total_peak_energy, total_peak_energy, favorable_peaks = control_is_worth(team, peaks, ships, units_stats, AI_stats) 

    if alive_ennemy_cruiser == 0 or ((AI_stats[team]['nb_cruiser'] > alive_ennemy_cruiser ) and not control_is_worth):
        
        stance = 'offensive'
        
    if (alive_ennemy_cruiser >0 and alive_ennemy_tanker ==0) or (alive_ennemy_cruiser > AI_stats[team]['nb_cruiser']): # rajouter close to our hub dans la condition

        stance = 'defensive'

    elif (alive_ennemy_cruiser < alive_ennemy_tanker or AI_stats[team]['nb_cruiser'] > alive_ennemy_cruiser) and control_is_worth:
       
        stance = 'control'

    return stance,total_peak_energy,our_total_peak_energy, favorable_peaks

def create_selected_list_from_ships(ships,team):

    """
    Parameters
    ----------
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    team : name of the team which is playing (str)       

    Return
    ------
    <ship_type>_list : makes a list of the different types from the ships list for the selected team (list)

    """
    tanker_list = [] 
    cruiser_list = []
    for ship in ships:
        if ships[ship]['team'] == team : 
            if ships[ship]['type'] == 'tanker':
                tanker_list.append(ship)
            else :
                cruiser_list.append(ship)
        
    return tanker_list,cruiser_list

def coordinates_to_go (ships):
    """"""
    instructions = ''

    for ship in ships :
        if ships[ship]['coordinates_to_go'] != ships[ship]['coordinates'] :
            instructions += str(ship) + ':@'+ str(ships[ship]['coordinates_to_go']) 

def count_distance (coord_1, coord_2):
    """
    Calculate the distance between coordinates

    Parameters
    ----------
    coord_1 : first coordinate to compare (tuple)
    coord_2: second coordinate to compare (tuple)

    Return
    ------
    distance: distance between the coordinates

    Version
    -------
    specification : Johan Rochet (v.1 24/04/20)
    implementation : Johan Rochet (v.1 24/04/20)
    """

    distance = max (abs(coord_1[0]-coord_2[0]), abs(coord_1[1]-coord_2[1]))
    return distance

def create_IA_ship (type, team, nb_ship,AI_stats):
    """
    Create an instruction to create a new ship 

    Parameters
    ----------
    type : type of the ship to create
    team : name of the IA team (int/str)
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    count_created : dictionary with the created tanker and cruiser per turn (dict)
    nb_ship : nb_IA_tanker or nb_IA_cruiser depending on the type
    Return 
    ------
    instruction: the instruction of creation of the ship (str)

    Version
    -------
    specification : Johan Rochet (v.1 24/04/20)
    implementation : Johan Rochet (v.1 24/04/20)

    """
    
    instruction = (type + '_'+ str(team) +'_' + str(AI_stats[team][nb_ship]) + ':' + type)
    AI_stats[team][nb_ship] += 1
    
    


    return instruction

def flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team):
    """
    Parameters
    ----------
   
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    team : name of the team which is playing (str)   
    ennemy_team : name of the ennemy_team (str)

    Return
    ------
    instruction : move tanker out of ennemy cruiser range + 1 (str)
    
    """
    for tanker in alive_tanker :
        for ennemy_cruiser in alive_ennemy_cruiser:
            
            distance = count_distance(ships[tanker]['coordinates'], ships[ennemy_cruiser]['coordinates'])

            if distance <= (units_stats[ennemy_team]['cruiser']['range'] + 1): 

                if ships[tanker]['coordinates'][0] < ships[ennemy_cruiser]['coordinates'][0] :
                    x = -1
                elif ships[tanker]['coordinates'][0] > ships[ennemy_cruiser]['coordinates'][0] :
                    x = 1
                else : 
                    x = 0 
                if ships[tanker]['coordinates'][1] < ships[ennemy_cruiser]['coordinates'][1] :
                    y = -1
                elif ships[tanker]['coordinates'][1] < ships[ennemy_cruiser]['coordinates'][1] :
                    y = 1
                else : 
                    y = 0
                ships[tanker]['coordinates_to_go'] = (ships[tanker]['coordinates'][0] + x, ships[tanker]['coordinates'][1] + y)

def attack_tanker (stance,AI_stats,ships,units_stats,team,ennemy_team, alive_cruiser,alive_ennemy_tanker):
    """Command to a cruiser to attack the first tanker's ennemy if the AI is offensive.

    Parameters
    ----------
    stance : if we are defensive or offensive (str).
    AI_stats : the dictionnary with all the stats of the AI (dict).
    ships : the dictionnary with all the ships (dict).
    units_stats : the dictionnary with the info of the hub (dict).
    team = the name of our team (str).
    ennemy_team = the name of the ennemy team (str).

    Notes
    -----
    If the ennemy is an attacker the AI don't use this function

    Version
    -------
    specification : Anthony Pierard (v.1 24/04/20)
    implementation : Anthony Pierard (v.1 27/04/20)
    """
    #verify if the ennemy is a defensive
    ############" rajouter d'abord attaquer les plus proches et puis les plus éloignés en paramètre"
    if stance=="offensive":
        
        nbr_ship=1
               
        for cruiser in alive_cruiser:
            for tanker in alive_ennemy_tanker:
                
                if nbr_ship==1:
                    cruiser_target=cruiser
                    tanker_target=tanker
                    distance_min = count_distance(ships[cruiser_target]['coordinates'],ships[tanker_target]['coordinates'] )
                    
                else :
                    if count_distance (ships[cruiser]['coordinates'], ships[tanker]['coordinates']) < distance_min :
                        cruiser_target =cruiser
                        tanker_target=tanker
                        distance_min = count_distance (ships[cruiser]['coordinates'], ships[tanker]['coordinates'])
                nbr_ship+=1

        if range_verification (units_stats,cruiser_target,ships,tanker_target_coordinate,team):
            order = cruiser_target + ':*' + tanker_target_coordinate[0] + '-' + tanker_target_coordinate[1] + '=' + ships[cruiser_target]['energy_point']/ (2 * units_stats['common']['cruiser']['cost_attack']) 
            return order
        else :
            x = ships[cruiser_target]['coordinate'][0]
            y = ships[cruiser_target]['coordinate'][1]
            if x < ships[tanker_target]['coordinate'][0] :
                x += 1
            elif x > ships[tanker_target]['coordinate'][0] :
                x -= 1 
            if y < ships[tanker_target]['coordinate'][1] :
                y += 1
            elif y > ships[tanker_target]['coordinate'][1] :
                y -= 1
            order = cruiser_target +':@' + str(x) + '-' + str(y)
            return order

def alert_ennemy_close_to_our_peak(favorable_peaks, units_stats, peaks, ships, ennemy_team):

    """
    Parameters
    ----------
    
    favorable_peaks : list of peaks situated on our side of the map (list)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    peaks : dictionary with informations about each peak (dict)
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    ennemy_team : name of the ennemy_team (str)

    Return
    ------
    alert_cruiser : If cruisers are closing in on one of our peaks True, else False (bool)
    nb_cruisers : number of cruisers for the alert (int)
    alert_tanker : If tankers are closinig in on one of our peaks True, else False (bool)
    nb_tankers : number of tankers for the alert (int)

    """
    alert_tanker = False
    alert_cruiser = False
    close_ennemy_tanker = []
    close_ennemy_cruiser = []
    
    
            
    #get coordinates of each ennemy ship
    
    for ship in ships:
        if ships[ship]['team'] == ennemy_team :
            for peak in favorable_peaks :

                    distance = count_distance (peaks[peak]['coordinates'], ships[ship]['coordinates'])  
                
                    if distance <= 10  : # reflechir a une formule adequate 

                        if ships[ship]['type'] == 'tanker' : 
                            close_ennemy_tanker.append(ship)

                        elif ships[ship]['type'] == 'cruiser'  :
                            close_ennemy_cruiser.append(ship)

    if len(close_ennemy_tanker) > 0: 
        alert_tanker = True

    if len(close_ennemy_cruiser) > 0:
        alert_cruiser = True

def alert_ennemy_close_to_our_hub(units_stats, ships, team, ennemy_team):
    """
    Parameters
    ----------
 
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    team : name of the team which is playing (str)   
    ennemy_team : name of the ennemy_team (str)
    
    Return
    ------
    alert_hub_cruiser : If cruisers are closing in on our hub True, else False (bool)
    nb_hub_cruisers : number of cruisers for the alert (int)
    alert_hub_tanker : If tankers are closinig in on our hub True, else False (bool)
    nb_hub_tankers : number of tankers for the alert (int)

    """
    alert_hub_tanker = False
    alert_hub_cruiser = False
    close_ennemy_hub_tanker = []
    close_ennemy_hub_cruiser = []

    for ship in ships:
        if ships[ship]['team'] == ennemy_team:
            #calc dist between ennemy ships and hub
            distance = count_distance(units_stats[team]['hub']['coordinates'], ships[ship]['coordinates'])

            if distance <= 10: #réfléchir à une formule pour changer 10
                #check ship type
                if ships[ship]['type'] == 'tanker' : 
                    close_ennemy_hub_tanker.append(ship)

                elif ships[ship]['type'] == 'cruiser'  :
                    close_ennemy_hub_cruiser.append(ship)
    #if ships in list then alert
    if len(close_ennemy_hub_tanker) > 0: 
        alert_hub_tanker = True

    if len(close_ennemy_hub_cruiser) > 0:
        alert_hub_cruiser = True




""" control function"""

def control_is_worth (team, ennemy_team, peaks, ships, units_stats,AI_stats):
    """
    Calculate if farming the energy out of peaks (staying in control) is worth the time

    Parameters
    ----------
    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    AI_stats: dictionary of the specific information for the AI(s) (dict)

    Return
    ------
    control_is_worth : True if it's still worth farming the energy out of peaks, False if not (bool)
    
    Versions
    --------
    specification : Kevin Schweitzer (v.1 24/04/20)

    """
    

    our_total_peak_energy = 0
    total_peak_energy = 0
    #not worth if total_peak_energy from our half of the map < total_tanker_storage + 900 
    control_is_worth = True

    total_tanker_storage = AI_stats[team]['nb_tanker'] * units_stats[team]['tanker']['max_energy'] #change nb_tanker to nb_current_tanker
    #get total energy from peaks in our half of the map
    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)
    for favorable_peak in favorable_peaks:
        our_total_peak_energy += peaks[favorable_peak]['storage']
    
    for peak in peaks:
        total_peak_energy += peaks[peak]['storage']
    
    #if (ennemy has more energy on his side of the map) and (ennemy has currently more energy in his hub than we do) and (has more tankers and cruisers), control is not worth
    if ((total_peak_energy - our_total_peak_energy)>(total_peak_energy/2)) and ((units_stats[ennemy_team]['hub']['energy_point']/units_stats['common']['hub']['max_energy_point']) > (units_stats[team]['hub']['energy_point']/units_stats['common']['hub']['max_energy_point'])) and ((AI_stats[ennemy_team]['nb_tanker'] > AI_stats[team]['nb_tanker']) and (AI_stats[ennemy_team]['nb_cruiser'] > AI_stats[team]['nb_cruiser'])):
        control_is_worth = False

    if our_total_peak_energy < total_tanker_storage + units_stats[team]['tanker']['max_energy']:
        control_is_worth = False # --> stop making tankers

    return control_is_worth, our_total_peak_energy, total_peak_energy, favorable_peak

def AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,peak_name,alive_tanker,alive_cruiser) :
    """ fonction used in control
    """

    #initialise the variable
    most_profitable = 0
    transfer_instruction = ''
    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)

    for tanker in alive_tanker :
        # if the tanker has drawn or given his energy
        if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <=1 :

            #go to draw energy 
            if ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 and total_peak_energy >0 : # reflechir aux conditions
                # si le tanker a moins de 60 % , calculer combien d'énergie restant, pour voir si plus rentable d'aller au hub ou au peak puis de rmeplir avec une totalité de réserve

                for index in peak_name :
                    if peaks[peak_name[index]]['storage'] > 0 :
                    #calculate the distance between the peak and the tanker
                        distance = count_distance (peaks[peak_name[index]]['coordinates'], ships[tanker]['coordinates']) 
                        #formula of profitability
                        profitability = (peaks[peak_name[index]]['storage']/distance) * len(grouped_peaks[index]) 
                        
                        #select the peak if it's the most profitable
                        if profitability >= most_profitable :
                            profitable_distance = distance
                            most_profitable = profitability
                            peak_coordinates = peaks[peak_name[index]]['coordinates']
                   
                ships[ship]['coordinates_to_go'] = peak_coordinates

                    #if the new peak is in range ==> draw 
                if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2 :
                    transfer_instruction += str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'] + ' '
            # go to give energy 
            else : 
                if stance=='control':
                    empty_cruiser = []
                    for index in alive_cruiser :
                        if ships[alive_cruiser[index]]['energy_point'] == 0 :
                            empty_cruiser.append()
                    #if one of the cruiser is empty
                    if len(empty_cruiser)!= 0 :
                        destiantion = ''
                        for index in empty_cruiser :
                            distance = count_distance (ships[empty_cruiser[index]]['coordiantes'],ships[tanker]['coordinates'])
                            if index == 0:
                               min_distance = distance
                               destination = empty_cruiser[index]
                            else :
                                if distance < min_distance :
                                    min_distance = distance 
                                    destination  = empty_cruiser[index]
                                     

                        ships[tanker]['coordinates_to_go'] = ships[destination]['coordinates']
                    # else: give to hub 
                    else :
                        destination = 'hub'
                        ships[tanker]['coordinates_to_go'] = units_stats[team]['hub']['coordinates']

                    if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2:
                   
                        transfer_instruction += str(tanker) + ':>'+ destination + ' '
                     

                        
                

        #if the tanker has not yet given or drawn energy

        else :
            if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) ==2 :
                if ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 and total_peak_energy >0 :
                    transfer_instruction += str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'] + ' '
                else : 
                    for index in alive_cruiser :
                        if ships[alive_cruiser[index]]['coordinates'] == ships[tanker]['coordinates_to_go']:
                            cruiser_destination = alive_cruiser[index]
                    transfer_instruction += str(tanker) + ':>'+ cruiser_destination + ' '

    #delete the space at the end of transfer_instruction                
    if len (transfer_instruction) != 0:
        transfer_instruction = transfer_instruction[:-1]
    return transfer_instruction

def find_grouped_peaks(team, peaks, units_stats):
    """
    Parameters
    ----------
    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    grouped_peaks : dictionary for the favorable grouped peaks (dict)

    Notes
    -----
    grouped_peaks takes the following form : grouped_peaks = {'grouped_peaks_1' : [peak_1, peak_2, peak_3], 'grouped_peaks_2' : [peak_4, peak_5, peak_6], ...}

    Version
    -------
    specification : Kevin Schweitzer (v.1 24/04/20)

    """
    
    peaks_coord = []
    peak_name = []
    grouped_peaks ={}
    #peaks = {name_entity : {'coordinates' : (int(info_peak[0]), int(info_peak[1])), 'storage' : int(info_peak[2])}}
    #peaks on our map side
   
    #check if there are other peaks in range of our favorable peaks, from less probable groupement (ex : 3x3) to most probable 
    #get favorable_peak coordinates
    for peak in peaks: #################### idée de changer cette fonction en récupérant tous groupes de peaks et de mettre la fonction favorable dans go-to-profitable_peaks(dans la formule)
        peaks_coord .append(peaks[peak]['coordinates'])
        peak_name.append (peak)
    
    for index_1 in range(len(peaks_coord)) :

        grouped_peaks[index_1] =[]

        if peaks[peak_name[index_1]]['storage']!=0 :

            for index_2 in range (len(peaks_coord)) :

                if count_distance (peaks_coord[index_1], peaks_coord[index_2]) < 4 and peaks and peaks[peak_name[index_2]]['storage']!=0 :
                    grouped_peaks[index_1].append (peak_name[index_2])
               
    return grouped_peaks,peak_name

def peaks_on_our_map_side(team, units_stats, peaks):
    """
    Parameters
    ----------

    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    favorable_peaks : list with the name of peaks situated closer to our hub (our side of the map) (list)

    Notes
    -----
    get distance between the two hubs and the peaks find the ones with minimal distance to each hub
   
    """

    our_hub_coordinates = units_stats[team]['hub']['coordinates']
    their_hub_coordinates = units_stats[team]['hub']['coordinates']
    favorable_peaks = []

    for peak in peaks:
        #get peek coordinates and get distance between our hub and peak and then between their hub and peak
        peak_coordinates = peaks[peak]['coordinates']
        distance_our_hub_and_peak = count_distance (our_hub_coordinates, peak_coordinates)
        distance_their_hub_and_peak = count_distance (their_hub_coordinates, peak_coordinates)

        if distance_our_hub_and_peak <= distance_their_hub_and_peak:
            #if our distance to peak is smaller then peak is on our side of the map
            favorable_peaks.append(peak)
        
    return favorable_peaks
    #favorable_peaks = [peak_1, peak_2]

"""defense function"""


""" offensive function"""
                


""" Upgrade functions """

def find_nb_rounds(team, ships, units_stats, AI_stats):
    
    """Finds the number of rounds you'd have to wait until you can create a new tanker (without taking into account the hub regeneration)

    Parameters
    ----------

    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    AI_stats: dictionary of the specific information for the AI(s) (dict)

    Return
    ------

    nb_rounds : number of rounds to wait for THE closest FULL tanker to come back or number of rounds to wait for the TWO closest FULL tankers to come back (int)
    
    """
    proximity_order_full_tankers_our_hub = create_proximity_order_full_tankers_our_hub(team, ships, units_stats)

    #nb_rounds = number of rounds to wait for the closest FULL tanker to come back #current energy + 1 tanker haul          
    if AI_stats[team]['virtual_energy_point'] + units_stats[team]['tanker']['max_energy'] >= 1000:

        #take the closest from proximity_order_full_tankers_our_hub list
        tanker = proximity_order_full_tankers_our_hub[0]
        
    #nb_rounds = number of rounds to wait for the two closest FULL tankers to come back #current energy + 2 tanker hauls
    else :
        
        #take the second closest from proximity_order_full_tankers_our_hub list
        tanker = proximity_order_full_tankers_our_hub[1]
    
    #nb_rounds = calc distance between FIRST closest full tanker and hub OR SECOND closest full tanker and hub. Depending on if condition before the operation.
    nb_rounds = count_dist(ships[tanker]['coordinates'], units_stats[team]['hub']['coordinates'])   

    return nb_rounds     

def create_proximity_order_full_tankers_our_hub(team, ships, units_stats):

    """ Creates a list of full tankers ordered from closest to furthest away from hub

    Parameters
    ----------
    
    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------

    proximity_order_full_tankers_our_hub : list with full tankers in proximity order to our hub (list)

    """
    full_tankers = []
    distance_list = []
    proximity_order_full_tankers_our_hub = []
    tanker_number = 0

    for ship in ships: 

        if (ships[ship]['team'] == team) and (ships[ship]['type'] == 'tanker') and (ships[ship]['energy_point'] == units_stats[team]['tanker']['max_energy']):
        
            full_tankers.append(ship)

    for ship in full_tankers:

            distance = count_distance(ships[ship]['coordinates'], units_stats[team]['hub']['coordinates'])
            distance_list.append(distance) #distance_list = [5, 10, 4]
        
    #make a list in order of closest tankers
    
    for distance in distance_list:

        closest_distance = min(distance_list)
        tanker_number += 1  #tanker_number = 1...2...3

        if distance == closest_distance: 
            
            proximity_order_full_tankers_our_hub.append(full_tankers[tanker_number]) # add tanker_3 to proximity list
        
            distance_list.delete(distance)

    return proximity_order_full_tankers_our_hub

def what_upgrade_to_use(team, ships, ennemy_team, peaks, AI_stats, units_stats, nb_rounds, stance, favorable_peaks,cost_upgrade, max_upgrade):

    """ Decides which upgrades to use, and when to use them

    Parameters
    ----------

    team : name of the team which is playing (str) 
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    ennemy_team : name of the ennemy_team (str)
    peaks : dictionary with all the peaks (dict)
    AI_stats: dictionary of the specific information for the AI(s) (dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    nb_rounds : number of rounds to wait for THE closest FULL tanker to come back or number of rounds to wait for the TWO closest FULL tankers to come back (int)
    stance :
    favorable_peaks : 

    Return
    ------
    instruction : instruction to make the selected upgrade 

    """
    stance = stance(ships, team, ennemy_team, peaks, units_stats, AI_stats)
    
    if stance == 'control':

        #control upgrades are tanker_capacity, regen and range
        #check regen:    
        
        current_hub_energy = AI_stats[team]['virtual_energy_point']
        regen_without_upgrade = units_stats[team]['hub']['regeneration']
        lost_money_without_regen_upgrade_list = []
        lost_money_without_storage_upgrade_list = []
        
        for times_upgraded in  range (1, (max_upgrade['max_regen_upgrade'] - regen_without_upgrade)/5 + 1):

            regen_with_upgrade = regen_without_upgrade + 5 * times_upgraded

            money_normal_regen = nb_rounds * regen_without_upgrade
            money_upgraded_regen = nb_rounds * regen_with_upgrade

            lost_money = money_upgraded_regen - money_normal_regen
            lost_money_without_regen_upgrade_list.append(lost_money)
        
        min_lost_money = min(lost_money_without_regen_upgrade_list)

        #find the best nb of regen upgrades for actual nb_rounds  
        best_nb_regen_upgrades = lost_money_without_regen_upgrade_list.index(min_lost_money)
      
        #calc energy won with best_nb_regen_upgrades during nb_rounds
        money_with_best_nb_regen_upgrades = nb_rounds * (regen_without_upgrade + best_nb_regen_upgrades * 5) - best_nb_regen_upgrades * cost_upgarde['cost_regen_upgrade'] 

        #check tanker:
        storage_without_upgrade = units_stats[team]['tanker']['max_energy']


        for times_upgraded in range (1,(max_upgrade['max_capacity_upgrade'] -storage_without_upgrade)/100 + 1 ):

            storage_with_upgrade = storage_without_upgrade + 100 * times_upgraded

            money_normal_storage = nb_rounds * regen_without_upgrade
            money_upgraded_storage = nb_rounds * regen_with_upgrade

            lost_money = money_upgraded_regen - money_normal_regen
            lost_money_without_regen_upgrade_list.append(lost_money)
        
        min_lost_money = min(lost_money_without_regen_upgrade_list)

        #find the best nb of regen upgrades for actual nb_rounds  
        best_nb_regen_upgrades = lost_money_without_regen_upgrade_list.index(min_lost_money)
      
        #calc energy won with best_nb_regen_upgrades during nb_rounds
        money_with_best_nb_regen_upgrades = nb_rounds * (regen_without_upgrade + best_nb_regen_upgrades * 5) - best_nb_regen_upgrades * cost_upgarde['cost_regen_upgrade'] 




        

            




    # peak 1 2000 peak 2 2000 peak_3 2000

    #don't do any tanker upgrades, take max and then go to next if peak_energy < tanker_max_energy
    #if for more than half of the favorable peaks (len(favorable_peaks)/2) are tested positive for a tanker upgrade, do it, else don't 
    #if for each peak, peak_energy % max_tanker_energy != 0 then check if peak_energy % max_tanker_energy + tanker_upgrade = 0 if yes do the amount of upgrades




    #deplacer tous sauf 1

    #Si ils sont plic ploc



        
    
        


            

    
 