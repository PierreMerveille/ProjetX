#At game start create tanker and tranfer energy back into hub
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
    stance,total_peak_energy = stance (ships)
    
    if stance == 'control' :
        
        
        while units_stats[team]['hub']['energy_point'] > units_stats['Common']['tanker']['creation_cost'] : 
            if AI_stats[team]['nb_tanker'] != 4 or AI_stats[team]['nb_cruiser'] >0 :
                instruction = create_IA_ship('tanker',team,'nb_tanker',AI_stats)
            #create a security_cruiser
            else :
                instruction = create_IA_ship('cruiser',team,'nb_cruiser',AI_stats)
                
        find_grouped_peaks(team, peaks, units_stats)
        
        peak_instructions = go_to_profitable_peak (ships,peaks,team,units_stats,total_peak_energy) 
        

def stance (ships,team,ennemy_team,peaks,units_stats,AI_stats):
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
    ennemy_cruiser = 0
    ennemy_tanker = 0

    for ship in ships:
        if ships[ship]['team'] == ennemy_team :
            
            if ships[ship][ennemy_team]['type'] == 'cruiser' :
                ennemy_cruiser += 1
            else:
                ennemy_tanker += 1

    control_is_worth, total_peak_energy = control_is_worth(team, peaks, ships, units_stats, AI_stats) 

    if ennemy_cruiser == 0 or ((AI_stats[team]['nb_cruiser'] > ennemy_cruiser ) and not control_is_worth):
        
        stance = 'offensive'
        
    elif (ennemy_cruiser >0 and ennemy_tanker ==0) or (ennemy_cruiser > AI_stats[team]['nb_cruiser']):

        stance = 'defensive'

    elif (ennemy_cruiser < ennemy_tanker or AI_stats[team]['nb_cruiser'] > ennemy_cruiser) and control_is_worth:
       
        stance = 'control'

    return stance,total_peak_energy


def go_to_profitable_peak(ships,peaks,team,units_stats,total_peak_energy,our_grouped_peaks,peak_name) :

    #initialise the variable
    most_profitable = 0
    instructions = ''
    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)
    for ship in ships :
        if ships[ship]['type'] == 'tanker':
            if ships[ship]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 or total_peak_energy !=0 : # reflechir aux conditions
                # si le tanker a moins de 60 % , calculer combien d'énergie restant, pour voir si plus rentable d'aller au hub ou au peak puis de rmeplir avec une totalité de réserve

                for index in peak_name :
                    if peaks[peak_name[index]]['storage'] > 0 :
                    #calculate the distance between the peak and the tanker
                        distance = count_distance (peaks[peak_name[index]]['coordinates'], ships[ship]['coordinates']) 
                        #formula of profitability
                        profitability = (peaks[peak_name[index]]['storage']/distance) * len(our_grouped_peaks[index]) 
                        
                        #select the peak if it's the most profitable
                        if profitability >= most_profitable :
                            profitable_distance = distance
                            most_profitable = profitability
                            peak_coordinates = peaks[peak_name[index]]['coordinates']

                if most_profitable != 0:

                    if profitable_distance <=1 :
                
                        instruction = ship +':@' + str(peak_coordinates[0]) + '-' + str(peak_coordinates[1])
                    else : 
                        if peak_coordinates[0] < ships[ship]['coordinates'][0] :
                            x = -1
                        elif peak_coordinates[0] > ships[ship]['coordinates'][0] :
                            x = 1
                        else : 
                            x = 0 
                        if peak_coordinates[1] < ships[ship]['coordinates'][1] :
                            y = -1
                        elif peak_coordinates[1] > ships[ship]['coordinates'][1] :
                            y = 1
                        else : 
                            y = 0
                        instruction = ship +':@' + str(x) + '-' + str(y)

                    instructions += instruction + ' '
                
                
            else : 
                give_to_profitable ()

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
    
    instruction = (type + '_'+ str(team) +'_' + str(AI_stats[team][nb_ship]) + ':' + type)
    AI_stats[team][nb_ship] += 1
    
    return instruction

def go_to_profiatble_target () :
    """"""
def attack_tanker (stance,AI_stats,ships,units_stats,team,ennemy_team):
    """Command to a cruiser to attack the first tanker's ennemy if the AI is offensive.

    Parameters
    ----------
    stance : if we are defensive or offensive (string).
    AI_stats : the dictionnary with all the stats of the AI (dictionnary).
    ships : the dictionnary with all the ships (dictionnary).
    units_stats : the dictionnary with the info of the hub (dictionnary).
    team = the name of our team (string).
    ennemy_team = the name of the ennemy team (string).

    Notes
    -----
    If the ennemy is an attacker the AI don't use this function

    Version
    -------
    specification : Anthony Pierard (v.1 24/04/20)
    implementation : Anthony Pierard (v.1 27/04/20)
    """
    #verify if the ennemy is a defensive
    if stance=="offensive":
        cruiser_list=[]
        tanker_list=[]
        nbr_ship=1
        for ship in ships:
            if ships[ship]['type']=='tanker' and ships[ship]['team']==ennemy_team :
                tanker_list.append(ship)
            if ships[ship]['type']=='cruiser' and ships[ship]['team']==team :
                cruiser_list.append(ship)
        for cruiser in cruiser_list:
            cruiser_coordinate=ships[cruiser]['coordinate']
            for tanker in tanker_list:
                tanker_coordinate=ships[tanker]['coordinate']
                if nbr_ship==1:
                    cruiser_target=cruiser
                    cruiser_target_coordinate=ships[cruiser_target]['coordinate']
                    tanker_target=tanker
                    tanker_target_coordinate=ships[tanker_target]['coordinate']
                    distance_min= max (abs(cruiser_target_coordinate[0]-tanker_target_coordinate[0]), abs(cruiser_target_coordinate[1]-tanker_target_coordinate[1]))
                else :
                    if max (abs(cruiser_coordinate[0]-tanker_coordinate[0]), abs(cruiser_coordinate[1]-tanker_coordinate[1])) < distance_min:
                        cruiser_target=cruiser
                        cruiser_target_coordinate=ships[cruiser_target]['coordinate']
                        tanker_target=tanker
                        tanker_target_coordinate=ships[tanker_target]['coordinate']
                        distance_min = max (abs(cruiser_target_coordinate[0]-tanker_target_coordinate[0]), abs(cruiser_target_coordinate[1]-tanker_target_coordinate[1]))
                nbr_ship+=1
        if range_verification (units_stats,cruiser_target,ships,tanker_target_coordinate,team):
            order = cruiser_target + ':*' + tanker_target_coordinate[0] + '-' + tanker_target_coordinate[1]
            return order
        else :
            x=cruiser_target_coordinate[0]
            y=cruiser_target_coordinate[1]
            if cruiser_target_coordinate[0] < tanker_target_coordinate[0] :
                x += 1
            elif cruiser_target_coordinate[0] > tanker_target_coordinate[0] :
                x -= 1 
            if cruiser_target_coordinate[1] < tanker_target_coordinate[1] :
                y += 1
            elif cruiser_target_coordinate[1] > tanker_target_coordinate[1] :
                y -= 1
            order = cruiser_target +':@' + str(x) + '-' + str(y)
            return order

def control_is_worth (team, ennemy_team, peaks, ships, units_stats,AI_stats) :
    """Calculate if farming the energy out of peaks (staying in control) is worth the time

    Parameters
    ----------
    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

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

    return control_is_worth, our_total_peak_energy

def find_grouped_peaks(team, peaks, units_stats):
    """
    Parameters
    ----------
    team : name of the team which is playing (str)   
    peaks : dictionary with informations about each peak (dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    our_grouped_peaks : dictionary for the favorable grouped peaks (dict)

    Notes
    -----
    our_grouped_peaks takes the following form : our_grouped_peaks = {'grouped_peaks_1' : [peak_1, peak_2, peak_3], 'grouped_peaks_2' : [peak_4, peak_5, peak_6], ...}

    Version
    -------
    specification : Kevin Schweitzer (v.1 24/04/20)

    """
    
    peaks_coord = []
    peak_name = []
    our_grouped_peaks ={}
    #peaks = {name_entity : {'coordinates' : (int(info_peak[0]), int(info_peak[1])), 'storage' : int(info_peak[2])}}
    #peaks on our map side
   
    #check if there are other peaks in range of our favorable peaks, from less probable groupement (ex : 3x3) to most probable 
    #get favorable_peak coordinates
    for peak in peaks: #################### idée de changer cette fonction en récupérant tous groupes de peaks et de mettre la fonction favorable dans go-to-profitable_peaks(dans la formule)
        peaks_coord .append(peaks[peak]['coordinates'])
        peak_name.append (peak)
    
    for index_1 in range(len(peaks_coord)) :

        our_grouped_peaks[index_1] =[]

        if peaks[peak_name[index_1]]['storage']!=0 :

            for index_2 in range (len(peaks_coord)) :

                if count_distance (peaks_coord[index_1], peaks_coord[index_2]) < 4 and peaks and peaks[peak_name[index_2]]['storage']!=0 :
                    our_grouped_peaks[index_1].append (peak_name[index_2])
               
    return our_grouped_peaks,peak_name

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
    
            
    #distance between each ennemy ship and our favorable peaks
    
    for ship in ships:
        if ships[ship]['team'] == ennemy_team :
            for peak in favorable_peaks :
                    #calc dist between favorable peaks and ennemy ships
                    distance = count_distance (peaks[peak]['coordinates'], ships[ship]['coordinates'])  
                
                    if distance <= 10  : # reflechir a une formule adequate 
                        #check ship type
                        if ships[ship]['type'] == 'tanker' : 
                            close_ennemy_tanker.append(ship)

                        elif ships[ship]['type'] == 'cruiser'  :
                            close_ennemy_cruiser.append(ship)
    #if ships in list then alert
    if len(close_ennemy_tanker) > 0 : 
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

    
        


            

    
 