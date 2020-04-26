#At game start create tanker and tranfer energy back into hub
def order_AI (team,ships,units_stats,peaks, ennemy_team,AI_stats) : 
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
    stance= stance (ships)
    if stance == 'control' :
        find_grouped_peaks(team, peaks, units_stats)
        
        go_to_profitable_peak (ships,peaks,team,units_stats,total_peak_energy) 

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

    control_is_worth, total_peak_energy = control_is_worth(team, peaks, ships, units_stats,AI_stats)

    if ennemy_cruiser == 0 or ((AI_stats[team]['nb_cruiser'] > ennemy_cruiser ) and not control_is_worth):

        return 'offensive'

    elif (ennemy_cruiser >0 and ennemy_tanker ==0) or (ennemy_cruiser > AI_stats[team]['nb_cruiser']):

        return 'defensive'

    elif (ennemy_cruiser < ennemy_tanker or AI_stats[team]['nb_cruiser'] > ennemy_cruiser) and control_is_worth:
        return 'control'


def go_to_profitable_peak(ships,peaks,team,units_stats,total_peak_energy,our_grouped_peaks,peak_name) :

    #initialise the variable
    most_profitable = 0
    instructions = ''
    for ship in ships :
        if ships[ship]['type'] == 'tanker':
            if ships[ship]['energy_point'] <= (units_stats[team]['tanker']['max_energy']/100 ) * 60 and total_peak_energy !=0 : 

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

                    instructions += instruction
                
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

def create_IA_ship (type, team, nb_ship):
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
    
    instruction = (type + '_'+ str(team) +'_' + str(nb_ship) + ':' + type)
    nb_ship += 1
   

    return instruction, nb_ship

def go_to_profiatble_target () :
    """"""
def control_is_worth (team, peaks, ships, units_stats,AI_stats) :
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
    total_peak_energy = 0
    #not worth if total_peak_energy from our half of the map <= total_tanker_storage + 900 (for each tanker storage = units_stats[team]['tanker']['max_energy'])
    control_is_worth = True
    

    total_tanker_storage = AI_stats[team]['nb_tanker'] * units_stats[team]['tanker']['max_energy']

    for peak in peaks :
        total_peak_energy += peaks[peak]['storage']

    if total_peak_energy <= total_tanker_storage:
        control_is_worth = False # --> stop making tankers

    return control_is_worth, total_peak_energy

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
    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)
    #check if there are other peaks in range of our favorable peaks, from less probable groupement (ex : 3x3) to most probable 
    #get favorable_peak coordinates
    for peak in favorable_peaks:
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