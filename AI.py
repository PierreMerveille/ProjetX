from math import *
from Play import * 

""" general function """

# note : faire attention a ne pas créer un ordre d'attaque et de déplacemt pour le meme cruiser

def order_AI (team,ships,units_stats,peaks, ennemy_team, AI_stats,grouped_peaks,cost_upgrade, max_upgrade,board) : 
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
    order_AI = []
    alive_tanker, alive_cruiser = create_ships_lists(ships,team)
    alive_ennemy_tanker, alive_ennemy_cruiser = create_ships_lists(ships,ennemy_team)
    stance,total_peak_energy,our_total_peak_energy, favorable_peaks= stance (ships)
    AI_stats[team]['virtual_energy_point'] = units_stats[team]['hub']['energy_point']
    nb_tankers_to_create(team, units_stats, favorable_peaks, peaks)
    order_AI += do_upgrades(team, units_stats, AI_stats, ships, alive_tanker, favorable_peaks, peaks, ennemy_team, cost_upgrade, max_upgrade)
    new_cruiser_group(alive_cruiser,ships,grouped_peaks,team)


    if stance == 'control' :

        create_control_ship (AI_stats,team,units_stats,alive_tanker,alive_cruiser)
        
        instruction, no_movement = AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,alive_tanker,alive_cruiser,AI_stats,stance)
        order_AI += instruction

        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team)

        go_to_group_coordinates()

        attack_cruiser_in_range(ships,alive_cruiser,alive_ennemy_cruiser + alive_ennemy_tanker,units_stats,team)

              

    elif stance == 'offensive':

        instruction, no_movement = AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,alive_tanker,alive_cruiser,AI_stats,stance)
        order_AI += instruction
        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team,alive_cruiser)

        offensive_attack()
        
        
        
        ### note à l'attention de ce très cher Anthony, idée: attaquer en priorité un croiseur ayant plus d'énergie que les qutres et aussi ceux avec le moins d'HP
    elif stance == 'defensive' :
        # rajouter list de non flee si puisement
        instruction, no_movement = AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,alive_tanker,alive_cruiser,AI_stats,stance)
        order_AI += instruction

        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team,alive_cruiser)

        place_cruiser_def(ships, board, team, ennemy_team, alive_cruiser)

        attack_cruiser_in_range(ships,alive_cruiser,alive_ennemy_cruiser,units_stats,team)


    
    order_AI += coordinates_to_go(ships)
    order_AI += target_to_shoot(alive_cruiser, ships, units_stats)
    order = ''
    for instruction in order_AI :
        order += instruction + ' '
    if len(order_AI) >0 :
        order -= ' '


    return order
def stance(ships, team, ennemy_team, peaks, units_stats, AI_stats, alive_cruiser,alive_ennemy_tanker, alive_ennemy_cruiser):
    """Decide if the adopted stance by the AI should be defensive or offensive

    Parameters
    ----------

    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    team : name of the team which is playing (str) 
    ennemy_team : name of the ennemy_team (str)
    peaks 
    units_stats
    AI_stats
    alive_cruiser
    alive_ennemy_tanker
    alive_ennemy_cruiser
    Return
    ------

    stance : sets the stance to adopt by the AI
    """
    

    control_is_worth, our_total_peak_energy, total_peak_energy, favorable_peaks = control_is_worth(team, peaks, ships, units_stats, AI_stats) 
  
        
    if alert_ennemy_close_to_our_hub(units_stats,ships,team,ennemy_team) or (alive_ennemy_cruiser > alive_cruiser and not control_is_worth): 
        stance = 'defensive'

    elif ((alive_cruiser> alive_ennemy_cruiser ) and not control_is_worth) or not control_is_worth :
        
        stance = 'offensive'

    elif (alive_ennemy_cruiser < alive_ennemy_tanker or alive_cruiser > alive_ennemy_cruiser) and control_is_worth:
       
        stance = 'control'

    return stance, total_peak_energy, our_total_peak_energy, favorable_peaks

def create_ships_lists(ships,team):

    """Creates a list per type containing the ships from the team

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
        
    return tanker_list, cruiser_list

def coordinates_to_go (ships,no_movement):
    """
    Create the move oreder for all the ships

    Parameters 
    ----------
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    no_movement : list with the name of the ships which musn't move (list)
    """
    instructions = []

    for ship in ships :
        if ships[ship]['coordinates_to_go'] != ships[ship]['coordinates'] and ship not in no_movement :

            x = ships[ship]['coordinates'][0]
            y = ships[ship]['coordinates'][1]
            if x < ships[ship]['coordinates_to_go'][0] :
                x += 1
            elif x > ship[ship]['coordinates_to_go'][0] :
                x -= 1 
            if y < ships[ship]['coordinates_to_go'][1] :
                y += 1
            elif y > ships[ship]['coordinates_to_go'][1] :
                y -= 1
            instructions.append(str(ship) + ':@'+ str(ships[ship]['coordinates_to_go']))
    
    return instructions

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
    name = type + '_'+ str(team) +'_' + str(AI_stats[team][nb_ship])
    instruction = (name + ':' + type)
    AI_stats[team][nb_ship] += 1

    return instruction, name
    
def AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,alive_tanker,alive_cruiser,AI_stats,stance) :
    """ Identify the ideal coordinates where the tankers should go and store it in ships and create transfer_instruction for them 

    Parameters
    ----------
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    peaks : dictionary with informations about each peak (dict)
    team : name of the team which is playing (str)   
    units_states : states of each unit (dict)
    total_peak_energy : total of energy available on the map (int)
    grouped_peaks : dictionnary with all the peaks around each peak (example: {1:[peak_1,peak_2]; 2: [peak_3, peak_1]}) (dict)
    alive_tanker : list with the name of the tanker of the team which are alive (list)
    alive_cruiser : list with the name of the cruiser of the team which are alive (list)
    favorable_peaks : list with the name of peaks situated closer to our hub (our side of the map) (list)

    Return :
    --------
    transfer_instruction : AI order for transfer (str)
    no_movement : list with the name of the ships which musn't move (list)
    """
    #######################rajouter puiser dans le hub pour offensif et défensif 
    #initialise the variable
    best_profitability = 0
    transfer_instruction = []
    no_movement =[]
    
    #change the rate depending on the stance 
    if stance=='control':
        rate = 1/5
    elif stance == 'defense': 
        rate = 2/5
    elif stance == 'attack' :
        rate = 1/2
   
    for tanker in alive_tanker :

         # verfify in the target peak is not empty 
        if ships[tanker]['target'] in peaks :
            if peaks[ships[tanker]['target']]['storage'] == 0 :
                ships[tanker]['coordinates_to_go'] = ships[tanker]['coordinates']

        # verify if the target cruiser isn't full        
        elif ships[tanker]['target'] in ships :
            if ships[ships[tanker]['target']]['energy_point'] >= units_stats['common']['cruiser']['max_energy'] * rate :
                ships[tanker]['coordinates_to_go'] = ships[tanker]['coordinates']
            if ships[ships[tanker]['target']]['coordinates'] != ships['tanker']['coordinates_to_go'] :
                 ships['tanker']['coordinates_to_go'] = ships[ships[tanker]['target']]['coordinates']


        #verify if the target cruiser is dead 
        elif  ships[tanker]['target'] != 'hub' :
            ships[tanker]['coordinates_to_go'] = ships[tanker]['coordinates']


        # if the tanker has drawn or given his energy
        if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <=1 :

            low_fuel_cruiser = []
            for cruiser in alive_cruiser :
                if ships[cruiser]['energy_point'] <= rate * units_stats['common']['cruiser']['max_energy'] :
                    low_fuel_cruiser.append()
            
            #go to draw energy 
            if (ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 and total_peak_energy >0 ): # reflechir aux conditions
                # si le tanker a moins de 60 % , calculer combien d'énergie restant, pour voir si plus rentable d'aller au hub ou au peak puis de rmeplir avec une totalité de réserve
                ###########################rajouter la différentitation en focntion des phases 
                for peak in peaks :
                    if peaks[peak]['storage'] > 0 :
                    #calculate the distance between the peak and the tanker
                        distance = count_distance (peaks[peak]['coordinates'], ships[tanker]['coordinates']) 
                        #formula of profitability
                        
                        profitability = (peaks[peak]['storage']/distance) 
                        
                        #select the peak if it's the most profitable
                        if profitability >= best_profitability :
                            best_profitability = profitability
                            peak_coordinates = peaks[peak]['coordinates']
                            target = peak
                ships[tanker]['coordinates_to_go'] = peak_coordinates
                ships[tanker]['target'] = target

                    #if the new peak is in range ==> draw 
                if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2 :
                    transfer_instruction .append(str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'] )

            elif ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 :

                # if one of the cruiser has a low fuel
                if len(low_fuel_cruiser)!= 0 :
                    # draw in the hub 
                    ships[tanker]['coordinates_to_go']= units_stats[team]['hub']['coordinates']
                if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2 and AI_stats[team['virtual_energy_point']] > 0 :
                    transfer_instruction .append(str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'])
                    count = 0
                    while  AI_stats[team['virtual_energy_point']] > 0 and count <(units_stats[team]['tanker']['max_energy'] - ships[tanker]['energy_point']):
                        AI_stats[team['virtual_energy_point']]-= 1
                        count+= 1
            # go to give energy 
            else : 
                
                #if one of the cruiser has a low fuel
                if len(low_fuel_cruiser)!= 0 :
                    destination = ''
                    for cruiser in low_fuel_cruiser :
                        distance = count_distance (ships[cruiser]['coordiantes'],ships[tanker]['coordinates'])
                        if low_fuel_cruiser.index(cruiser) == 0:
                            min_distance = distance
                            destination = cruiser
                        else :
                            if distance < min_distance :
                                min_distance = distance 
                                destination  = cruiser
                 
                                     

                    ships[tanker]['coordinates_to_go'] = ships[destination]['coordinates']
                    ships[tanker]['target'] = destination
                # else: give to hub 
                else :
                    destination = 'hub'
                    ships[tanker]['coordinates_to_go'] = units_stats[team]['hub']['coordinates']
                    ships[tanker]['target'] = 'hub'

                if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2:
                
                    transfer_instruction.append(str(tanker) + ':>'+ ships[tanker]['target'])
                    no_movement.append(ships[tanker]['target'])
        #if the tanker has not yet given or drawn energy
        else :
            if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) ==2 :
                if ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 and total_peak_energy >0 :
                    transfer_instruction.append(str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'])
                else : 
                    for cruiser_destination in alive_cruiser :
                        if ships[cruiser]['coordinates'] == ships[tanker]['coordinates_to_go']:
                            cruiser_destination = cruiser
                    transfer_instruction.append(str(tanker) + ':>'+ cruiser_destination)
                    no_movement.append(cruiser_destination)
    #delete the space at the end of transfer_instruction                
    
    return transfer_instruction, no_movement


""" control function"""



def control_is_worth (team, ennemy_team, peaks, units_stats, AI_stats):
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

def find_grouped_peaks(team, peaks, units_stats,grouped_peaks):
    """creates a dictionary with the grouped peaks

    Parameters
    ----------
    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    grouped_peaks : dictionary for the grouped peaks (dict)

    Notes
    -----
    grouped_peaks takes the following form : grouped_peaks = {'grouped_peaks_1' : [peak_1, peak_2, peak_3], 'grouped_peaks_2' : [peak_4, peak_5, peak_6], ...}

    Version
    -------
    specification : Kevin Schweitzer (v.1 24/04/20)

    """
    
    favorable_peaks = peaks_on_our_map_side(team,units_stats,peaks)
    for peak in favorable_peaks :
        if peaks[peak]['strorage'] != 0 :
            group_nb = 1 
            if grouped_peaks[team] == {} :
                grouped_peaks[team] = {group_nb :{'name' : [peak], 'coord' : (), 'nb_cruiser' : 0}} 
            else :
                value = False
                for group_peaks in grouped_peaks : 
                    for element in grouped_peaks[group_peaks] :
                        if count_distance (peaks[peak]['coordinates'], peaks[element]['coordinates']) < 3 :
                            grouped_peaks.append(peak)
                            value = True  
                if not value :

                    group_nb += 1
                    grouped_peaks[team] = {group_nb :{'name' : [peak], 'coord' : (), 'nb_cruiser' : 0}}
                    
    for group_peaks in grouped_peaks : 
        coord = []
        for element in grouped_peaks[group_peaks]['name'] :
            coord.append (peaks[element]['coordinates'])
        coord = order_coord(coord,units_stats[team]['hub']['coordinates'])

        grouped_peaks[group_peaks]['coord'] = coord[-1]

    return grouped_peaks


def peaks_on_our_map_side(team, units_stats, peaks):
    """ Makes a list containing the names of peaks on our map side

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

def flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team, alive_cruiser,long,larg):
    """ Makes a tanker flee if he senses danger coming

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

        if ships[tanker]['target'] not in alive_cruiser and ships[tanker]['target'] != 'hub' :

            for ennemy_cruiser in alive_ennemy_cruiser:
                
                distance = count_distance(ships[tanker]['coordinates'], ships[ennemy_cruiser]['coordinates'])

                if distance <= (units_stats[ennemy_team]['cruiser']['range'] + 1): 

                    if ships[tanker]['coordinates'][0] < ships[ennemy_cruiser]['coordinates'][0] and ships[tanker]['coordinates'][0] !=0 :
                        x = -1
                    elif ships[tanker]['coordinates'][0] > ships[ennemy_cruiser]['coordinates'][0] and ships[tanker]['coordinates'][0]!= long:
                        x = 1
                    else : 
                        x = 0 
                    if ships[tanker]['coordinates'][1] < ships[ennemy_cruiser]['coordinates'][1] and ships[tanker]['coordinates'][1] != 0:
                        y = -1
                    elif ships[tanker]['coordinates'][1] < ships[ennemy_cruiser]['coordinates'][1] and ships[tanker]['coordinates'][0] != larg :
                        y = 1
                    else : 
                        y = 0
                    ships[tanker]['coordinates_to_go'] = (ships[tanker]['coordinates'][0] + x, ships[tanker]['coordinates'][1] + y)

    return ships
def alert_ennemy_close_to_our_hub(units_stats, ships, team, ennemy_team):
    """ Sends an alert if an ennemy tanker or cruiser gets close to our hub

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

    return close_ennemy_hub_tanker,close_ennemy_hub_cruiser
     
""" offensive function"""

def attack_hub (ships, units_stats, alive_cruiser, ennemy_team):
    """ Command all the cruiser to attack the ennemy hub 

    Parameters
    ----------
    ships : the dictionnary with all the ships (dict)
    units_stats : the dictionnary with the info of the hub (dict) 
    alive_cruiser : the list of the cruiser (list)
    ennemy_team : the name of the ennemy team (str)

    Notes 
    -----
    if the total cruiser dammage is bigger than the health point of the ennemy hub all the cruiser attack him.
    
    Version
    -------
    specification : Anthony Pierard (v.1 27/04/20)
    implementation : Anthony Pierard (v.1 27/04/20)
                     Anthony Pierard (v.2 29/04/20)
    """

    
    move_list = []
    hub_coordinate = units_stats[ennemy_team]['hub']['coordinate']
    for cruiser in alive_cruiser:
        
        cruiser_coordinate = ships[cruiser]['coordinate']
        distance = count_distance(cruiser_coordinate,hub_coordinate)
                
        ships[cruiser]['target'] = 'hub'
        ships[cruiser]['coordinates_to_go'] = hub_coordinate
       
    
    
        
    
def attack_cruiser_in_range(ships,alive_cruiser ,alive_ennemy_cruiser,units_stats,team) :
    """ Assign the most profitable target in range to cruisers

    Parameters
    ----------
    
    ships : the dictionnary with all the ships (dict)
    alive_cruiser : the list of the cruiser (list)
    alive_ennemy_cruiser : list with the name of the alive cruiser of the ennemy_team (list)
    units_stats : the dictionnary with the info of the hub (dict) 
    team : name of the team which is playing (str) 
    
    """
            
    attacked_cruiser =[]

    for ally_cruiser in alive_cruiser :

        if ships[ally_cruiser]['coordinates'] == ships[ally_cruiser]['coordinates_to_go'] or ships[ally_cruiser]['target'] == 'hub' and ships[ally_cruiser]['energy_point'] !=0 :
            target_ships =[]
            #get the cruisers in range that aren't already attacked
            for cruiser in alive_ennemy_cruiser :
                if range_verification(units_stats, ally_cruiser,ships, ships[cruiser]['coordinates'],team) and cruiser not in attacked_cruiser :
                    target_ships.append (cruiser) 
            if target_ships != [] : 
                #order the tanker depending on their HP and energy
                HP_list = order_ship_by_caracteristic(target_ships, 'HP')
                energy_list = order_ship_by_caracteristic(target_ships, 'energy_point')

                attack_dico ={}
                for cruiser in target_ships :
                    attack_dico[cruiser] = len(HP_list) - HP_list.index(cruiser) + energy_list.index(cruiser)
                
                #select the profitbale cruiser to attack 
                key_nb = 0 
                for cruiser in attack_dico :
                    if key_nb == 0 :
                        target = cruiser
                    else :
                        if attack_dico[cruiser]> attack_dico[target] :
                            target = cruiser 
                    key_nb += 1 
                attacked_cruiser.append(target)

                ships[ally_cruiser]['target'] = target
               
def attack_cruisers (alive_cruiser, alive_ennemy_cruiser, ships,units_stats, team):
    """ Assign a target to a cruiser without target during offensive stance

    Parameters
    ----------
    alive_cruiser : the list of the cruiser (list)
    alive_ennemy_cruiser : list with the name of the alive cruiser of the ennemy_team (list)
    ships : the dictionnary with all the ships (dict)
    units_stats : the dictionnary with the info of the hub (dict) 
    team : name of the team which is playing (str)
    
    """

    targeted_cruiser = []
    ally_attacker =[]
    coord =[]
    #select cruiser which don't have yet targeted a ennemy and the ennemy_cruiser which hadn't yet been targeted
    for ally_cruiser in alive_cruiser:
        if ships[ally_cruiser]['target'] != [] :
            #store the ennemy which has already been targeted
            targeted_cruiser.append (ships[ally_cruiser]['target'])
        else :
            #store the name and coord of the cruiser which don't have a target
            ally_attacker.append(ally_cruiser)
            coord.append(ships[ally_cruiser]['coordinates']) 

    for ennemy in alive_ennemy_cruiser :

        if ennemy not in targeted_cruiser :

            energy = 0
            energy_to_kill = ships[ennemy]['HP'] * units_stats['common']['cruiser']['cost_attack']
            #sort the coordinates
            order_coord = order_coord (coord, ships[ennemy]['coordinates'])
            order_cruiser =[]
            #associate the cooridnates with their cruiser
            for coord in order_coord :
                for ally_cruiser in ally_attacker :
                    if ships[ally_cruiser]['coordinates'] == coord and ally_cruiser not in order_cruiser :
                        order_cruiser.append (ally_cruiser)
            # add a target to the cruisers while energy> energy_to_kill
            for ally_cruiser in order_cruiser :
                if ships[ally_cruiser]['energy_point'] !=0 and energy < energy_to_kill :
                    
                    energy += ships[ally_cruiser]['energy_point'] - count_distance(ships[ally_cruiser]['coordinates'], ships[ennemy]['coordiantes']) * units_stats[team]['cruiser']['move']
                    ships[ally_cruiser]['coordinates_to_go'] = ships[ennemy]['coordinates']
                    ships[ally_cruiser]['target'] = ennemy 

def attack_tanker (AI_stats,ships,team,ennemy_team, alive_cruiser,alive_ennemy_tanker,dangerous_ennemy_tanker):
    """Command to a cruiser to attack the first tanker's ennemy if the AI is offensive.

    Parameters
    ----------
    AI_stats : the dictionnary with all the stats of the AI (dict)
    ships : the dictionnary with all the ships (dict)
    team = the name of our team (str)
    ennemy_team = the name of the ennemy team (str)

    Notes
    -----
    If the ennemy is an attacker the AI don't use this function

    Version
    -------
    specification : Anthony Pierard (v.1 24/04/20)
    implementation : Anthony Pierard (v.1 27/04/20)
    """
    #verify if the ennemy is a defensive
    
    for tanker in dangerous_ennemy_tanker : 
        not_already_targeted =[]
        ally_attacker =[]
        #select the closer cruiser
        for ally_cruiser in alive_cruiser :
            if tanker not in ships[ally_cruiser]['target'] :
                not_already_targeted.append(tanker)
                ally_attacker.append(ally_cruiser)
        

        if tanker not in not_already_targeted :
            for cruiser in alive_cruiser :
                #if cruiser in standby
                if ships[cruiser]['coordinates'] == ships[cruiser]['coordinates_to_go'] and ships[cruiser]['energy_point'] != 0 :
                    if alive_cruiser.index(cruiser)== 0 :
                        attacking_cruiser = cruiser
                        target_tanker = tanker
                        distance = count_distance(ships[attacking_cruiser]['coordinates'],ships[tanker]['coordinates'] )
                    elif count_distance(ships[attacking_cruiser]['coordinates'],ships[tanker]['coordinates'] ) < distance :
                        attacking_cruiser = cruiser
                        target_tanker = tanker
                        distance = count_distance(ships[attacking_cruiser]['coordinates'],ships[tanker]['coordinates'] )
                        
            ships[cruiser_target]['coordinates_to_go'] = ships[target_tanker]['coordinates']
            ships[cruiser_target]['target'] = target_tanker
        else :
            for cruiser in ally_attacker :
                
                # if ennemy has move, change the coordinates_to_go
                if ships[cruiser]['coordinates_to_go'] != ships[tanker]['coordinates']:
                    ships[ally_cruiser]['coordinates_to_go'] = ships[tanker]['coordinates']    

def target_to_shoot (AI_stats, alive_cruiser, ships, units_stats,team) :
    """ Gives the attack instruction for each alive cruiser
    Parameters
    ----------
    AI_stats : the dictionnary with all the stats of the AI (dict)
    alive_cruiser : the list of the cruiser (list)
    ships : the dictionnary with all the ships (dict)
    units_stats : the dictionnary with the info of the hub (dict) 
    team : name of the team which is playing (str)

    Return
    ------
    orders : list of attack instructions (list)

    """
    orders =[]
    for cruiser in alive_cruiser :
        if ships[cruiser]['target'] != '' :
            target_coord = ships[cruiser]['coordinates_to_go']
            if range_verification(units_stats,cruiser,target_coord,team) :
                orders.append(cruiser + ':*' + target_coord[0] + '-' + target_coord[1] + '=' + ships[cruiser]['energy_point']/ (2 * units_stats['common']['cruiser']['cost_attack']))      
                ships[cruiser]['target'] = ''
                ships[cruiser]['coordinates_to_go'] = ships[cruiser]['coordinates']
            
            AI_stats [team]['conflict'] = True
    return orders

""" Upgrade functions """

def find_nb_rounds(team, ships, units_stats, AI_stats, alive_tanker):
    
    """Finds the number of rounds you'd have to wait until you can create a new tanker (without taking into account the hub regeneration)

    Parameters
    ----------

    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    AI_stats: dictionary of the specific information for the AI(s) (dict)
    alive_tanker : list containing the alive tankers from the team (list)


    Return
    ------
    nb_rounds : number of rounds to wait until hub has enough energy to create a new tanker (int)
    
    """
    order_tanker = order_full_tanker(team, ships, units_stats, alive_tanker)
    hub_energy = AI_stats[team]['virtual_energy_point']

    for tanker in order_tanker:
        if hub_energy < units_stats['common']['tanker']['creation_cost']:
                     
            hub_energy += ships[tanker]['storage'] 
 
    nb_rounds = count_distance(ships[tanker]['coordinates'], units_stats[team]['hub']['coordinates'])   

    return nb_rounds     

def order_full_tanker(team, ships, units_stats, alive_tanker):

    """ Creates a list of full tankers ordered from closest to furthest away from hub

    Parameters
    ----------
    
    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    alive_tanker : list containing the alive tankers from the team (list)

    Return
    ------
    order_tanker : list with full tankers in proximity order to our hub (list)

    """
    full_tankers = []
    distance_list = []
    proximity_order_full_tankers_our_hub = []
    tanker_number = 0
    
    for ship in alive_tanker: 

        if (ships[ship]['energy_point'] >= units_stats[team]['tanker']['max_energy']*60/100) and ships[ship]['target'] == 'hub':
        
            full_tankers.append(ship)

    coord = []
    for ship in full_tankers:
        coord.append(ships[ship]['coordinates']) 
    
    order_coord = order_coord(coord,units_stats[team]['hub']['coordinates'])

    order_tanker = []
    
    for coord in order_coord :
        for ship in full_tankers :
            if ships[ship]['coordinates'] == coord and ship not in order_tanker :
                order_tanker.append(ship)

    return order_tanker

def nb_hauls(storage_without_upgrade, storage_with_upgrade, team, units_stats, peaks, max_upgrade):
    """ Calculates nb of average hauls needed to emtpy a peak
    Parameters
    ----------

    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    average_nb_hauls : average hauls needed for a tanker to empty a peak on the map depending on the actual upgrade (list)

    """
    hauls_list = []

    for times_upgraded in range (0,(max_upgrade['max_capacity_upgrade'] - storage_without_upgrade)/100 + 1 ):

        for peak in peaks:

            if peaks[peak]['storage'] % (storage_with_upgrade*60/100) == 0:

                nb_hauls = peaks[peak]['storage']/(storage_with_upgrade*60/100)
                hauls_list.append(nb_hauls)
    
    average_nb_hauls = ceil(sum(hauls_list)/len(hauls_list))

    return average_nb_hauls

def best_nb_upgrades( team, ships, ennemy_team, peaks, AI_stats, units_stats, nb_rounds, favorable_peaks, cost_upgrade, max_upgrade, alive_tanker):

    """ Calculates best nb of upgrades

    Parameters
    ----------
    
    team : name of the team which is playing (str) 
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    ennemy_team : name of the ennemy_team (str)
    peaks : dictionary with all the peaks (dict)
    AI_stats: dictionary of the specific information for the AI(s) (dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    nb_rounds : number of rounds to wait for THE closest FULL tanker to come back or number of rounds to wait for the TWO closest FULL tankers to come back (int)
    favorable_peaks : list with the name of peaks situated closer to our hub (our side of the map) (list)
    max_upgrade : dictionary containing the values for each upgrade (dict)
    cost_upgrade : dictionary containing the price for each upgrade (dict)
    nb_tanker_to_create_this_round : nb of tankers the AI should create during this round (int) 
    alive_tanker : list with the name of the tanker of the team which are alive (list)

    Return
    ------
    nb_range_upgrades : optimal number of range upgrades to keep a range >= to the ennemy team (int)
    nb_storage_upgrades : optimal number of storage upgrades to reach max profitability (int)
    nb_regen_upgrades : optimal number of regen upgrades to reach max profitability (int)
    storage_or_regen : name of the upgrade that is currently worth more (str)

    """

    #control upgrades are tanker_capacity, regen and range   
    nb_range_upgrades = 0
    regen_without_upgrade = units_stats[team]['hub']['regeneration']
    lost_money_without_regen_upgrade_list = []
    money_lost_tanker_creation_list = []
    average_nb_hauls_list = []

    ######################check regen###################### 
    for times_upgraded in  range (1, (max_upgrade['max_regen_upgrade'] - regen_without_upgrade)/5 + 1):

        regen_with_upgrade = regen_without_upgrade + 5 * times_upgraded

        money_normal_regen = nb_rounds * regen_without_upgrade
        money_upgraded_regen = nb_rounds * regen_with_upgrade

        lost_money = money_upgraded_regen - money_normal_regen
        lost_money_without_regen_upgrade_list.append(lost_money)
    
    min_lost_money = min(lost_money_without_regen_upgrade_list)

    #find the best nb of regen upgrades for actual nb_rounds  
    nb_regen_upgrades = lost_money_without_regen_upgrade_list.index(min_lost_money) + 1 

    ###########check storage################
    storage_without_upgrade = units_stats[team]['tanker']['max_energy']

    for times_upgraded in range (0,(max_upgrade['max_capacity_upgrade'] - storage_without_upgrade)/100 + 1 ):

        storage_with_upgrade = storage_without_upgrade + 100 * times_upgraded
        
        #calc money_back_from_tankers = nb_tankers_to_create * units_stats[team]['tanker']['max_energy']
        money_back_from_tankers = (nb_tankers_to_create - len(alive_tanker)) * storage_with_upgrade 
        
        #calc price for creating nb_tankers_to_create
        price_to_create_nb_tankers = (nb_tankers_to_create - len(alive_tanker))* units_stats['common']['tanker']['creation_cost'] #tankers qui doivent encore être créés
        
        #calc money_lost_after_nb_tanker_to_create
        money_lost_tanker_creation = price_to_create_nb_tankers - money_back_from_tankers
        
        #use money_lost_tanker_creation_list to calc if worth upgrading more : if money_lost_tanker_creation_list[1] - money_lost_tanker_creation_list[2] - cost_upgrade['cost_storage_upgrade'] > 0
        money_lost_tanker_creation_list.append(money_lost_tanker_creation)

        #see what nb_upgrade would be optimal to reduce the nb of average hauls
        average_nb_hauls = nb_hauls(storage_without_upgrade, storage_with_upgrade, team, units_stats, peaks, max_upgrade)
        average_nb_hauls_list.append(average_nb_hauls)
    
    #see if upgrade is worth it for the money during tanker creation else don't do upgrade
    if money_lost_tanker_creation_list[1] - money_lost_tanker_creation_list[2] - cost_upgrade['cost_storage_upgrade'] > 0:
        
        nb_storage_upgrades = average_nb_hauls_list.index(min(average_nb_hauls_list))

    ###############check storage_or_regen###################
    storage_with_upgrade = storage_without_upgrade + 100 * nb_storage_upgrades
    money_from_storage = storage_with_upgrade * (nb_tankers_to_create - len(alive_tanker))
    regen_with_upgrade = regen_without_upgrade + nb_regen_upgrades * 5
    money_from_regen = regen_with_upgrade * nb_rounds
   
    if money_from_regen <= money_from_storage:
        storage_or_regen = 'storage'

    else : 
        storage_or_regen = 'regen'
        
    ##################check range########################### indépendant de la stance
    #bool a mettre en paramètre et qui vient d'une fonction qui calcule si on attaque #check if their cruisers have a better range than ours  

    if AI_stats[team]['conflict'] == True : 
        
        if units_stats[team]['cruiser']['range'] == 1 : 
        
            nb_range_upgrades += 1 

        if units_stats[ennemy_team]['cruiser']['range'] >= units_stats[team]['cruiser']['range']:

            nb_range_upgrades += units_stats[ennemy_team]['cruiser']['range'] - units_stats[team]['cruiser']['range'] #si >= à la condition au dessus alors + 1

    return nb_range_upgrades, nb_storage_upgrades, nb_regen_upgrades, storage_or_regen

def nb_tankers_to_create(team, units_stats, favorable_peaks, peaks) :

    """ Calculates the ideal number of tankers to create during the game

    Parameters
    ---------- 
    team : name of the team which is playing (str) 
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    peaks : dictionary with all the peaks (dict)
    favorable_peaks : list with the name of peaks situated closer to our hub (our side of the map) (list)

    Return
    ------

    nb_tankers_to_create : number of tankers to create determined from the number of energy in the peaks on our side of them map (int)
    
    """
    our_total_energy = 0

    for peak in favorable_peaks: 

        our_total_energy += peaks[peak]['storage'] 
    
    nb_tankers_to_create = int(our_total_energy/(units_stats[team]['tanker']['max_energy_point'])*units_stats)

def do_upgrades(team, units_stats, AI_stats, ships, alive_tanker, favorable_peaks, peaks, ennemy_team, cost_upgrade, max_upgrade):          
    
    """ Creates instructions to make desired upgrades
    
    Parameters
    ----------
    team : name of the team which is playing (str) 
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    nb_range_upgrades : optimal number of range upgrades to keep a range >= to the ennemy team (int)
    nb_storage_upgrades : optimal number of storage upgrades to reach max profitability (int)
    nb_regen_upgrades : optimal number of regen upgrades to reach max profitability (int)
    AI_stats: dictionary of the specific information for the AI(s) (dict)
    storage_or_regen : name of the upgrade that is currently worth more (str)
    favorables_peaks : peaks on the map side of the team (list)
    alive_tanker : list with the name of the alive tanker of the team (list)
    Return
    ------
    instruction : instruction to make the number of the desired upgrades

    """      
    nb_rounds = find_nb_rounds(team, ships, units_stats, AI_stats, alive_tanker)
    nb_tankers_to_create = nb_tankers_to_create(team, units_stats, favorable_peaks, peaks)
    nb_range_upgrades, nb_storage_upgrades, nb_regen_upgrades, storage_or_regen = best_nb_upgrades( team, ships, ennemy_team, peaks, AI_stats, units_stats, nb_rounds, favorable_peaks, cost_upgrade, max_upgrade, alive_tanker)

    instruction = []

    if nb_range_upgrades > 0:
        upgrade = 'range'
       
        for nb in nb_range_upgrades :
            if AI_stats[team]['virtual_energy_point'] >= cost_upgrade['cost_range_upgrade'] :
                instruction.append('upgrade:' + str(upgrade))
                AI_stats[team]['virtual_energy_point'] -= cost_upgrade['cost_range_upgrade']
    
    if storage_or_regen == 'storage' : 
        nb_upgrades = nb_storage_upgrades
        cost = cost_upgrade['cost_storage_upgrade']

    elif storage_or_regen == 'regen' :
        nb_upgrades = nb_regen_upgrades
        cost = cost_upgrade['cost_regen_upgrade']

    if len(alive_tanker) > 3 * nb_upgrades : 
 
        #if storage more profitable than regen:
        for nb in nb_upgrades :
            if AI_stats[team]['virtual_energy_point'] >= cost :
                instruction.append('upgrade:' + str(storage_or_regen))
                AI_stats[team]['virtual_energy_point'] -= cost

def place_cruiser_def(ships, board, team, ennemy_team, alive_cruiser,cruiser_place,units_stats,AI_stats):
    """
    This function create a defensive block before the team hub to protect him

    Parameters :
    ------------
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    board : dictionary with the coordinates of all boxes of the board which gives a list of element on this place (dict)
    team : name of the team which is playing (str)  
    ennemy_team : name of the ennemy_team (str)
    alive_cruiser : list with the name of the alive cruiser of the team (list)
    cruiser_place : 
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    AI_stats: dictionary of the specific information for the AI(s)
    
    """
    ally_hub = units_stats[team]['hub']['coordinates']
    ennemy_hub = units_stats[ennemy_team]['hub']['coordinates']
    nb_cruiser = len(alive_cruiser)
    coord = []

    nb_line = 1
    go_on = True
    result = 0
    while go_on  :
        result += nb_line *4 + 1 
        if result <nb_cruiser :
            
           nb_line += 1 
        else : 
            go_on = False 
    

    if ally_hub[0] - ennemy_hub[0] >= 0:
        column_shift = -1
        
    else:
        column_shift = 1

    if ally_hub[1] - ennemy_hub[1] >= 0:
        row_shift = -1
        
    else:
        row_shift = 1
     
   
    
    for y in range (1, (nb_line+1)*column_shift, column_shift) :
        for x in range(-abs(y),abs(y)+1) :

            coord.append((ally_hub[0] + x, ally_hub[1]+ y ))

    for x in range (1, (nb_line+1)*row_shift, row_shift) :
        for y in range(-abs(x),abs(x)+1) :

            coord.append((ally_hub[0] + x, ally_hub[1]+ y ))


    coord = order_coord(coord,units_stats[team]['hub']['coordinates'])
    coord_empty = verif_if_ship_on_coord(coord, alive_cruiser)
    cruiser_place = place_ship(coord_empty, cruiser_place, alive_cruiser)
      
def verif_if_ship_on_coord(coord,alive_cruiser, ships,board):
    """ 
    Select the coordinates which has not already been assigned to a cruiser 

    Parameters
    ----------
    coord : list with the coordinates to assign (list)
    alive_cruiser :list with the name of the alive cruiser of the team (list)
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)

    Return 
    ------
    coord_empty : list with the coordinates  which has not already been assigned to a cruiser (list)
    """
    
    coord_empty = []
    for coordinate in coord:
        coordinate_not_empty = False

        for cruiser in alive_cruiser :
            if ships[cruiser]['coordinate_to_go'] == coordinate:
                coordinate_not_empty = True
        
        if not coordinate_not_empty and coordinate in board:
            coord_empty.append(coordinate)

    return coord_empty

def order_coord(coord,destination) :

    """ 
    Sorting algorithm which sorts different coordinates by distance from other coordinates

    Parameters
    ----------
    coord : list with the coordinates to order  (list)
    destination : coordinates of the stable point (tuple)

    Return:
    -------
    order_coord : list with the ordered coordinates depending on the proximity from the ally hub (list)

    Version :
    ---------
    specification: Johan Rochet (v.1 29/04/20)
    implementation: Johan Rochet (v.1 29/04/20)
    """
    b= []
    c=[]
    if len(coord) <= 1 :
        return coord
    if len(coord) == 2 :
        if count_distance(coord[0],destination)> count_distance(coord[1],destination) :
            swap = coord[0]
            coord[0]= coord[1]
            coord[1]= swap
        return coord
    else :
        index = randint (0, len(coord)-1)
        
        pivot= coord[index]
        pivot_distance = count_distance(pivot,destination)
        del(coord[index])
        for element in coord :
            if count_distance(element,destination) < pivot_distance : 
                b.append(element)
                
            else :
                c.append(element)
        
        return order_coord(b,destination)+ [pivot]+ order_coord(c,destination)
    

def place_ship(coord_empty, cruiser_place, alive_cruiser):
    """"""
    for coord in coord_empty:
        full = True
        for cruiser in alive_cruiser:
            if cruiser not in cruiser_place and  full :
                ships[cruiser]['coordinate_to_go'] = coord
                cruiser_place.append(cruiser)
                full = False
            

    return cruiser_place
           
def order_ship_by_caracteristic(ship_list, caracteristic,ships) :
    """
    Sorting function which sort the ships by caracteristic (HP or energy_point) (recursive function)

    Parameters 
    ----------
    ships_list : list of the name of the ship to sort (list)
    caracteristic : name of the caracteristic (str)
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    
    Return
    ------
    order_coord : list with the ordered coordinates (list)
    """
    
    b= []
    c=[]
    if len(ship_list) <= 1 :
        return ship_list
    if len(ship_list) == 2 :
        if ships[ship_list[0]]['caracteristic']> ships[ship_list[1]]['caracteristic'] :
            swap = ship_list[0]
            ship_list[0]= ship_list[1]
            ship_list[1]= swap
        return ship_list
    else :
        index = randint (0, len(ship_list)-1)
        
        pivot= ship_list[index]
        del(ship_list[index])
        for element in ship_list :
            if ships[element]['caracteristic'] < ships[ship_list]['caracteristic'] :  
                b.append(element)
                
            else :
                c.append(element)
        
        return order_ship_by_caracteristic(b)+ [pivot]+ order_ship_by_caracteristic(c)

def offensive_attack(alive_cruiser,ships,units_stats,ennemy_team,alive_ennemy_cruiser,AI_stats,board,team)  :
    """ 
    This function handles the function calls for the attack in offensive stance

    Parameters
    ----------
    alive_cruiser : list with the name of the alive cruiser of the team (list)
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    ennemy_team : name of the ennemy_team (str)
    alive_ennemy_cruiser : list with the name of the alive cruiser of the ennemy_team (list)
    AI_stats: dictionary of the specific information for the AI(s)
    board : dictionary with the coordinates of all boxes of the board which gives a list of element on this place (dict)
    team : name of the team which is playing (str)  
    """

    

    total_dammage=0
    #calculate all the dammage of the cruiser
    for cruiser in alive_cruiser :
        total_dammage += ships[cruiser]['energy_point']/units_stats['common']['cruiser']['cost_attack']
    #attack the hub if we have double of health of the ennemy hub because we can lose cruiser.
    if total_dammage/2 < units_stats[ennemy_team]['hub']['HP'] or len(alive_ennemy_cruiser) == 0 : 
        attack_hub(stance, AI_stats, ships, units_stats, alive_cruiser, ennemy_team, board, team, alive_ennemy_cruiser)
        attack_cruiser_in_range (ships,alive_cruiser ,alive_ennemy_cruiser,units_stats,team)
    else : 
        attack_cruisers()

def create_control_ship (AI_stats,team,units_stats,alive_tanker,alive_cruiser) :
    """
    This function creates the creation of ships in the control stance 

    Parameters :
    ------------
    AI_stats: dictionary of the specific information for the AI(s)
    team : name of the team which is playing (str)  
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    alive_tanker : list with the name of the alive tanker of the team (list)
    alive_cruiser : list with the name of the alive cruiser of the team (list)

    Return
    ------
    instructions : list with the different instructions (list)
    """
    instructions =[]
    while AI_stats[team]['virtual_energy_point'] > units_stats['common']['tanker']['creation_cost'] :

        if alive_tanker <= 2* alive_cruiser and alive_tanker < nb_tankers_to_create :

            instruction,name = create_IA_ship('tanker',team,'nb_tanker',AI_stats)
            instructions.append(instruction)
            
            AI_stats[team]['virtual_energy_point'] -= units_stats['common']['tanker']['creation_cost']
            #transfer from the new tanker to hub 
            instructions.append('%s:>%d-%d' % (name,units_stats[team]['hub']['coordiantes'][0],units_stats[team]['hub']['coordiantes'][1] ))
        #create a security_cruiser
        else :
            instruction,name = create_IA_ship('cruiser',team,'nb_cruiser',AI_stats)
            instructions.append(instruction)
            AI_stats[team]['virtual_energy_point'] -= units_stats['common']['cruiser']['creation_cost']
    return instructions
        
def new_cruiser_group (alive_cruiser,ships,grouped_peaks,team):
    nb_group = 0
    for group in grouped_peaks[team]: 
        nb_group += 1


    for cruiser in alive_cruiser :
        
        if ships[cruiser]['group'] == -1 :
                placed = False
                for index in range(nb_group-1, -1, -1) :
                    if not placed :

                        if index == 0 :
                            grouped_peaks[team][index]['nb_cruiser'] += 1
                            ships[cruiser]['group'] = index 
                            
                            placed = True

                        elif grouped_peaks[team][index]['nb_cruiser'] <  grouped_peaks[team][index -1]['nb_cruiser'] :

                            grouped_peaks[team][index]['nb_cruiser'] += 1
                            ships[cruiser]['group'] = index
                             
                            placed = True
    return ships

def go_to_group_coordinates (grouped_peaks, ships, team) :
    for group in grouped_peaks[team]:
        coord_group.append(grouped_peaks[team][index]['coord'])
        for x in range(-2, 3) :
            for y in range(-2, 3) :

                coord_group.append((grouped_peaks[team][index]['coord'][0] + x,grouped_peaks[team][index]['coord'][0] + y))

        coord_empty = verif_if_ship_on_coord(coord_group,alive_cruiser, ships)
        for cruiser in alive_cruiser:

            if ships[cruiser]['group'] == group and ships[cruiser]['coordinates_to_go'] == ships[cruiser]['coordinates'] and coord_empty != [] :
                ships[cruiser]['coordinates_to_go'] = choice(coord_empty)
                index_coord_empty = coord_empty.index(ships[cruiser]['coordinates_to_go'])
                del(coord_empty[index_coord_empty])
                
""" general secondary function"""

                   
                
           

            

#une fonction qui en fonction du groupe la met sur la coord et quand il est placé ==> attack_cruiser in range
