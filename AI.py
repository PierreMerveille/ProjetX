from math import *
from Play import * 

""" general function """

# note : faire attention a ne pas créer un ordre d'attaque et de déplacemt pour le meme cruiser

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
    order_AI = ''
    alive_tanker, alive_cruiser = create_ships_lists(ships,team)
    alive_ennemy_tanker, alive_ennemy_cruiser = create_ships_lists(ships,ennemy_team)
    grouped_peaks, peak_name = find_grouped_peaks(team, peaks, units_stats)
    stance,total_peak_energy,our_total_peak_energy, favorable_peaks= stance (ships)
    AI_stats[team]['virtual_energy_point'] = units_stats[team]['hub']['energy_point']
    nb_tankers_to_create(team, units_stats, favorable_peaks, peaks)
    
    if stance == 'control' :
        
        while AI_stats[team]['virtual_energy_point'] > units_stats['Common']['tanker']['creation_cost'] : 

            if AI_stats[team]['nb_tanker'] != 4 or AI_stats[team]['nb_cruiser'] >0 :

                instruction,name = create_IA_ship('tanker',team,'nb_tanker',AI_stats)
                order_AI += ' ' + instruction
                AI_stats[team]['virtual_energy_point'] -= units_stats['common']['tanker']['creation_cost']
                #transfer from the new tanker to hub 
                order_AI += name + ':>'+ str(units_stats[team]['hub']['coordiantes'][0]) + '-' + str(units_stats[team]['hub']['coordiantes'][1])
            #create a security_cruiser
            else :
                instruction = create_IA_ship('cruiser',team,'nb_cruiser',AI_stats)
                AI_stats[team]['virtual_energy_point'] -= units_stats['common']['cruiser']['creation_cost']
        
        transfer_instruction = AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,peak_name)

        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team)

        close_ennemy_cruiser,close_ennemy_tanker = alert_ennemy_close_to_our_peak(favorable_peaks, units_stats, peaks, ships, ennemy_team)         
        #if ships in list then alert
        if len(close_ennemy_cruiser) > 0 :
            attack_cruiser_control ()

        if len(close_ennemy_tanker) > 0 :
            attack_tanker(stance,AI_stats,ships,units_stats,team,ennemy_team, alive_cruiser,close_ennemy_tanker)
              

    elif stance == 'offensive':

        AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,peak_name)

        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team,alive_cruiser)

        attack_cruiser_control(alive_cruiser,close_ennemy_cruiser,ships,units_stats, team)

        attack_tanker(stance,AI_stats,ships,units_stats,team,ennemy_team, alive_cruiser,alive_ennemy_tanker,dangerous_ennemy_tanker)
        
        
        ### note à l'attention de ce très cher Anthony, idée: attaquer en priorité un croiseur ayant plus d'énergie que les qutres et aussi ceux avec le moins d'HP
    elif stance == 'defensive' :
        # rajouter list de non flee si puisement
        AI_transfer_and_destination (ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,peak_name)

        flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team,alive_cruiser)

        place_cruiser_def(ships, board, team, ennemy_team, alive_cruiser)

        attack_cruiser_defense(ships,alive_cruiser,alive_ennemy_cruiser,units_stats,team)

        attack_cruiser()
    
    coordinates_to_go(ships)
    target_to_shoot(alive_cruiser, ships, units_stats)

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
  
        
    if alert_ennemy_close_to_our_hub(units_stats,ships,team,ennemy_team) or (alive_ennemy_cruiser > alive_cruiser and not control_is_worth): 
        stance = 'defensive'

    elif ((alive_cruiser> alive_ennemy_cruiser ) and not control_is_worth) or not control_is_worth :
        
        stance = 'offensive'

    elif (alive_ennemy_cruiser < alive_ennemy_tanker or alive_cruiser > alive_ennemy_cruiser) and control_is_worth:
       
        stance = 'control'

    return stance,total_peak_energy,our_total_peak_energy, favorable_peaks

def create_ships_lists(ships,team):

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

def coordinates_to_go (ships,no_movement):
    """
    Create the move oreder for all the ships

    Parameters 
    ----------
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    no_movement : list with the name of the ships which musn't move (list)
    """
    instructions = ''

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
            instructions += str(ship) + ':@'+ str(ships[ship]['coordinates_to_go']) + ' '
    if instructions != '':
        instructions= instructions[:-1]
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
    
def AI_transfer_and_destination(ships,peaks,team,units_stats,total_peak_energy,grouped_peaks,peak_name,alive_tanker,alive_cruiser,AI_stats,stance) :
    """ Identify the ideal coordinates where the tankers should go ans tore it in ships and create transfer_instruction for them 

    Parameters
    ----------
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    peaks : dictionary with informations about each peak (dict)
    team : name of the team which is playing (str)   
    units_states : states of each unit (dict)
    total_peak_energy : total of energy available on the map (int)
    grouped_peaks : dictionnary with all the peaks around each peak (example: {1:[peak_1,peak_2]; 2: [peak_3, peak_1]}) (dict)
    peak_name : list of peaks with the corresponding to the groupe_peaks dictionnary (list)
    alive_tanker : list with the name of the tanker of the team which are alive (list)
    alive_cruiser : list with the name of the cruiser of the team which are alive (list)

    Return :
    --------
    transfer_instruction : AI order for transfer (str)
    no_movement : list with the name of the ships which musn't move (list)
    """
    #######################rajouter puiser dans le hub pour offensif et défensif 
    #initialise the variable
    best_profitability = 0
    transfer_instruction = ''
    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)
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
                for peak in peak_name :
                    if peaks[peak]['storage'] > 0 :
                    #calculate the distance between the peak and the tanker
                        distance = count_distance (peaks[peak]['coordinates'], ships[tanker]['coordinates']) 
                        #formula of profitability
                        profitability = (peaks[peak]['storage']/distance) * len(grouped_peaks[peak_name.index(peak)]) 
                        
                        #select the peak if it's the most profitable
                        if profitability >= best_profitability :
                            best_profitability = profitability
                            peak_coordinates = peaks[peak]['coordinates']
                            target = peak
                ships[tanker]['coordinates_to_go'] = peak_coordinates
                ships[tanker]['target'] = target

                    #if the new peak is in range ==> draw 
                if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2 :
                    transfer_instruction += str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'] + ' '

            elif ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 :

                # if one of the cruiser has a low fuel
                if len(low_fuel_cruiser)!= 0 :
                    # draw in the hub 
                    ships[tanker]['coordinates_to_go']= units_stats[team]['hub']['coordinates']
                if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) <= 2 and AI_stats[team['virtual_energy_point']] > 0 :
                    transfer_instruction += str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'] + ' '
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
                
                    transfer_instruction += str(tanker) + ':>'+ ships[tanker]['target'] + ' '
                    no_movement.append(ships[tanker]['target'])
        #if the tanker has not yet given or drawn energy
        else :
            if count_distance(ships[tanker]['coordinates_to_go'], ships[tanker]['coordinates']) ==2 :
                if ships[tanker]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 and total_peak_energy >0 :
                    transfer_instruction += str(tanker) + ':<'+ ships[tanker]['coordinates_to_go'] + ' '
                else : 
                    for cruiser_destination in alive_cruiser :
                        if ships[cruiser]['coordinates'] == ships[tanker]['coordinates_to_go']:
                            cruiser_destination = cruiser
                    transfer_instruction += str(tanker) + ':>'+ cruiser_destination + ' '
                    no_movement.append(cruiser_destination)
    #delete the space at the end of transfer_instruction                
    if len (transfer_instruction) != 0:
        transfer_instruction = transfer_instruction[:-1]
    return transfer_instruction


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

def find_grouped_peaks(team, peaks, units_stats):
    """
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
    
    peaks_coord = []
    peak_name = []
    grouped_peaks ={}
    #peaks = {name_entity : {'coordinates' : (int(info_peak[0]), int(info_peak[1])), 'storage' : int(info_peak[2])}}
    #peaks on our map side
   
    #check if there are other peaks in range of our favorable peaks, from less probable groupement (ex : 3x3) to most probable 
    #get favorable_peak coordinates
    for peak in peaks: #################### idée de changer cette fonction en récupérant tous groupes de peaks et de mettre la fonction favorable dans go-to-profitable_peaks(dans la formule)
        peaks_coord.append(peaks[peak]['coordinates'])
        peak_name.append (peak)
    
    for index_1 in range(len(peaks_coord)) :

        grouped_peaks[index_1] =[]

        if peaks[peak_name[index_1]]['storage']!=0 :

            for index_2 in range (len(peaks_coord)) :

                if count_distance (peaks_coord[index_1], peaks_coord[index_2]) < 4 and peaks and peaks[peak_name[index_2]]['storage']!=0 :
                    grouped_peaks[index_1].append(peak_name[index_2])
               
    return grouped_peaks, peak_name

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

def flee_tanker(alive_tanker, alive_ennemy_cruiser, ships, units_stats, team, ennemy_team,alive_cruiser):
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

    return close_ennemy_cruiser,close_ennemy_tanker, alert_cruiser,alert_tanker

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

def attack_hub (stance, AI_stats, ships, units_stats, alive_cruiser, ennemy_team, board, team):
    """ Command all the cruiser to attack the ennemy hub 

    Parameters
    ----------
    team : name of the team which is playing (str) 
    stance : the stance of the AI (string).
    AI_stats : the dictionnary with all the info of the AI (dictionnary).
    ships : the dictionnary with all the ships (dictionnary).
    units_stats : the dictionnary with the info of the hub (dictionnary). 
    alive_cruiser : the list of the cruiser (list).
    ennemy_team : the name of the ennemy team (string).
    board : dictionnary with all the case of the board (dictionnary).

    Notes 
    -----
    if the total cruiser dammage is bigger than the health point of the ennemy hub all the cruiser attack him.
    
    Version
    -------
    specification : Anthony Pierard (v.1 27/04/20)
    implementation : Anthony Pierard (v.1 27/04/20)
                     Anthony Pierard (v.2 29/04/20)
    """
    total_dammage=0
    #calculate all the dammage of the cruiser
    for cruiser in alive_cruiser :
        total_dammage += ships[cruiser]['energy_point']/units_stats['common']['cruiser']['cost_attack']
    #attack the hub if we have double of health of the ennemy hub because we can lose cruiser.
    if total_dammage/2 < units_stats[ennemy_team]['hub']['HP'] :
        attack_list = []
        move_list = []
        for cruiser in alive_cruiser:
            hub_coordinate = units_stats[ennemy_team]['hub']['coordinate']
            cruiser_coordinate = ships[cruiser]['coordinate']
            #if the cruiser is in range create an attack
            if range_verification (units_stats, cruiser, ships, hub_coordinate, team):
                instruction = cruiser + ':*' + hub_coordinate[0] + '-' + hub_coordinate[1] + '=' + ships[cruiser]['energy_point']
                attack_list.append (instruction)
            #else move the cruiser close to the hub and check if an other cruiser is on the nearest case. 
            else :
                x = cruiser_coordinate[0]
                y = cruiser_coordinate[1]
                if x < hub_coordinate[0] and ((x+1,y) in move_list) :
                    x += 1 
                elif x > hub_coordinate[0] and ((x-1,y) in move_list) :
                    x -= 1
                if y < hub_coordinate[1] and ((x,y+1) in move_list) :
                    y += 1 
                elif y > hub_coordinate[1] and ((x,y-1) in move_list) :
                    y -= 1
                move_list.append ((x,y))
                ships[cruiser]['coordinates_to_go']=(x,y)
        return attack_list 
    
def attack_cruiser_defense(ships,alive_cruiser,alive_ennemy_cruiser,units_stats,team) :

            
        attacked_cruiser =[]

        for ally_cruiser in alive_cruiser :

            if ships[ally_cruiser]['coordinates'] == ships[ally_cruiser]['coordinates_to_go'] and ships[ally_cruiser]['energy_point'] !=0 :
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
               

def attack_cruiser_control (alive_cruiser,close_ennemy_cruiser,ships,units_stats, team):

    for ennemy in close_ennemy_cruiser :
        not_already_targeted =[]
        ally_attacker =[]

        #select the cruiser which has not yet been targeted by an alive_cruiser
        for ally_cruiser in alive_cruiser :
            if ennemy not in ships[ally_cruiser]['target'] :
                not_already_targeted.append(ennemy)
                ally_attacker.append(ally_cruiser)
        
        # select cruiser(s) to attack the cruiser
        if ennemy in not_already_targeted :
            energy = 0
            energy_to_kill = ships[ennemy]['HP'] * units_stats['common']['cruiser']['cost_attack']
            for ally_cruiser in alive_cruiser :
                if ships[ally_cruiser]['coordinates'] == ships[ally_cruiser]['coordinates_to_go'] and ships[ally_cruiser]['energy_point'] !=0 and energy < energy_to_kill :
                    
                    energy += ships[ally_cruiser]['energy_point'] - count_distance(ships[ally_cruiser]['coordinates'], ships[ennemy]['coordiantes']) * units_stats[team]['cruiser']['move']
                    ships[ally_cruiser]['coordinates_to_go'] = ships[ennemy]['coordinates']
                    ships[ally_cruiser]['target'] = ennemy 
                
        else :
            for ally_cruiser in ally_attacker :
                
                # if ennemy has move, change the coordinates_to_go
                if ships[ally_cruiser]['coordinates_to_go'] != ships[ennemy]['coordinates']:
                    ships[ally_cruiser]['coordinates_to_go'] = ships[ennemy]['coordinates']

def attack_tanker (stance,AI_stats,ships,units_stats,team,ennemy_team, alive_cruiser,alive_ennemy_tanker,dangerous_ennemy_tanker):
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

def target_to_shoot (alive_cruiser, ships, units_stats) :

    for cruiser in alive_cruiser :
        if ships[cruiser]['target'] != '' :
            target_coord = ships[cruiser]['coordinates_to_go']
            if range_verification(units_stats,cruiser,target_coord,team) :
                order = cruiser + ':*' + target_coord[0] + '-' + target_coord[1] + '=' + ships[cruiser]['energy_point']/ (2 * units_stats['common']['cruiser']['cost_attack'])      
                ships[cruiser]['target'] = ''
                ships[cruiser]['coordinates_to_go'] = ships[cruiser]['coordinates']
             

""" Upgrade functions """

def find_nb_rounds(team, ships, units_stats, AI_stats, alive_tanker):
    
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
    order_tanker = order_full_tanker(team, ships, units_stats, alive_tanker)

    #nb_rounds = number of rounds to wait for the closest FULL tanker to come back #current energy + 1 tanker haul          
    if AI_stats[team]['virtual_energy_point'] + (units_stats[team]['tanker']['max_energy']*60/100) >= 1000:

        #take the closest from order_tanker list
        tanker = order_tanker[0]
        
    #nb_rounds = number of rounds to wait for the two closest FULL tankers to come back #current energy + 2 tanker hauls
    else :
        
        #take the second closest order_tanker list
        tanker = order_tanker[1]
    
    #nb_rounds = calc distance between FIRST closest full tanker and hub OR SECOND closest full tanker and hub. Depending on if condition before the operation.
    nb_rounds = count_distance(ships[tanker]['coordinates'], units_stats[team]['hub']['coordinates'])   

    return nb_rounds     

def order_full_tanker(team, ships, units_stats, alive_tanker):

    """ Creates a list of full tankers ordered from closest to furthest away from hub

    Parameters
    ----------
    
    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)

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
    
    order_coord = order_coord(coord,units_stats,team)

    order_tanker = []
    
    for coord in order_coord :
        for ship in full_tankers :
            if ships[ship]['coordinates'] == coord and ship not in order_tanker :
                order_tanker.append(ship)

    return order_tanker

def nb_hauls(storage_without_upgrade, storage_with_upgrade, team, units_stats, peaks, max_upgrade):
    """
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

def best_nb_upgrades(decided_to_attack, team, ships, ennemy_team, peaks, AI_stats, units_stats, nb_rounds, favorable_peaks, cost_upgrade, max_upgrade, nb_tankers_to_create_this_round, alive_tanker):

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
    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)

    #control upgrades are tanker_capacity, regen and range   
    nb_range_upgrades = 0
    current_hub_energy = AI_stats[team]['virtual_energy_point']
    regen_without_upgrade = units_stats[team]['hub']['regeneration']
    lost_money_without_regen_upgrade_list = []
    peaks_modulo_yes = []
    rest_modulo_list = []
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
    nb_regen_upgrades = lost_money_without_regen_upgrade_list.index(min_lost_money)

    ###########check storage################
    storage_without_upgrade = units_stats[team]['tanker']['max_energy']

    for times_upgraded in range (0,(max_upgrade['max_capacity_upgrade'] - storage_without_upgrade)/100 + 1 ):

        storage_with_upgrade = storage_without_upgrade + 100 * times_upgraded
        
        #calc money_back_from_tankers = nb_tankers_to_create * units_stats[team]['tanker']['max_energy']
        money_back_from_tankers = nb_tankers_to_create * storage_with_upgrade #tankers qui doivent encore être créés
        
        #calc price for creating nb_tankers_to_create
        price_to_create_nb_tankers = nb_tankers_to_create * units_stats['common']['tanker']['creation_cost'] #tankers qui doivent encore être créés
        
        #calc money_lost_after_nb_tanker_to_create
        money_lost_tanker_creation = price_to_create_nb_tankers - money_back_from_tankers
        
        #use money_lost_tanker_creation_list to calc if worth upgrading more : if money_lost_tanker_creation_list[1] - money_lost_tanker_creation_list[2] - cost_upgrade['cost_upgrade_capacity'] > 0
        money_lost_tanker_creation_list.append(money_lost_tanker_creation)

        #see what nb_upgrade would be optimal to reduce the nb of average hauls
        average_nb_hauls = nb_hauls(storage_without_upgrade, storage_with_upgrade, team, units_stats, peaks, max_upgrade)
        average_nb_hauls_list.append(average_nb_hauls)
    
    #see if upgrade is worth it for the money during tanker creation else don't do upgrade
    if money_lost_tanker_creation_list[1] - money_lost_tanker_creation_list[2] - cost_upgrade['cost_upgrade_capacity'] > 0:

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

    if decided_to_attack == True : 
        
        if units_stats[team]['cruiser']['range'] == 1 : 
        
            nb_range_upgrades += 1 

        if units_stats[ennemy_team]['cruiser']['range'] >= units_stats[team]['cruiser']['range']:

            nb_range_upgrades += units_stats[ennemy_team]['cruiser']['range'] - units_stats[team]['cruiser']['range'] #si >= à la condition au dessus alors + 1

    return nb_range_upgrades, nb_storage_upgrades, nb_regen_upgrades, storage_or_regen

def nb_tankers_to_create(team, units_stats, favorable_peaks, peaks) :

    """
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

def tankers_this_round(team, AI_stats, units_stats, alive_tanker, nb_tanker_to_create, nb_range_upgrades, nb_storage_upgrades, nb_regen_upgrades):
    
    """
    Parameters
    ----------
    team : name of the team which is playing (str) 
    AI_stats: dictionary of the specific information for the AI(s) (dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    alive_tanker : list with the name of the tanker of the team which are alive (list)
    nb_tanker_to_create : number of tankers to create determined from the number of energy in the peaks on our side of them map (int)
    nb_range_upgrades : optimal number of range upgrades to keep a range >= to the ennemy team (int)
    nb_storage_upgrades : optimal number of storage upgrades to reach max profitability (int)
    nb_regen_upgrades : optimal number of regen upgrades to reach max profitability (int)

    Return
    ------
    nb_tankers_to_create_this_round : number of tankers to create during this round (int)

    """
    if (nb_range_upgrades == 0 and nb_storage_upgrades == 0 and nb_regen_upgrades == 0) and len(alive_tanker) < nb_tanker_to_create :
        
        nb_tankers_to_create_this_round = int(AI_stats[team]['virtual_energy_point']/units_stats['common']['tanker']['creation_cost'])

def do_upgrades(team, units_stats, nb_range_upgrades, nb_storage_upgrades, nb_regen_upgrades, AI_stats, nb_tankers_to_create_this_round, storage_or_regen):          
    
    """
    Parameters
    ----------
    team : name of the team which is playing (str) 
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    nb_range_upgrades : optimal number of range upgrades to keep a range >= to the ennemy team (int)
    nb_storage_upgrades : optimal number of storage upgrades to reach max profitability (int)
    nb_regen_upgrades : optimal number of regen upgrades to reach max profitability (int)
    AI_stats: dictionary of the specific information for the AI(s) (dict)
    nb_tanker_to_create_this_round : nb of tankers the AI should create during this round (int)
    storage_or_regen : name of the upgrade that is currently worth more (str)

    Return
    ------
    instruction : instruction to make the number of the desired upgrades

    """      
    instruction = ''

    if nb_range_upgrades > 0:
        upgrade = 'range'
       
        for nb in nb_range_upgrades:
            instruction += 'upgrade:' + str(upgrade) + ' ' 

    #if storage more profitable than regen:
    if storage_or_regen == 'storage' :
        upgrade = 'storage'

        for nb in nb_storage_upgrades:
            instruction += 'upgrade:' + str(upgrade) + ' '

    else :
        upgrade = 'regeneration'

        for nb in nb_regen_upgrades:
            instruction += 'upgrade:' + str(upgrade) + ' '    

def place_cruiser_def(ships, board, team, ennemy_team, alive_cruiser,cruiser_place,units_stats,AI_stats):
    """"""
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


    coord = order_coord(coord,units_stats)
    coord_empty = verif_if_ship_on_coord(coord, alive_cruiser)
    cruiser_place = place_ship(coord_empty, cruiser_place, alive_cruiser)
      
def verif_if_ship_on_coord(coord,alive_cruiser):
    
    for coordinate in coord:
        coordinate_not_empty = False

        for cruiser in alive_cruiser :
            if ships[cruiser]['coordinate_to_go'] == coordinate:
                coordinate_not_empty = True
        
            if not coordinate_not_empty:
                coord_empty.append(coordinate)

    return coord_empty

def order_coord(coord, units_stats,team) :

    """ 
    Sorting algorithm which sorts the coordinates by distance from the hub 

    Parameters
    ----------
    coord : list with the coordinates to order  (list)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)

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
        if count_distance(coord[0],units_stats[team]['hub']['coordinates'])> count_distance(coord[1],units_stats[team]['hub']['coordinates']) :
            swap = coord[0]
            coord[0]= coord[1]
            coord[1]= swap
        return coord
    else :
        index = randint (0, len(coord)-1)
        
        pivot= coord[index]
        pivot_distance = count_distance(pivot,units_stats[team]['hub']['coordinates'])
        del(coord[index])
        for element in coord :
            if count_distance(element,units_stats[team]['hub']['coordinates']) < pivot_distance : 
                b.append(element)
                
            else :
                c.append(element)
        
        return order_coord(b,units_stats,team)+ [pivot]+ order_coord(c,units_stats,team)
    

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

        
    
        


            

    
 
