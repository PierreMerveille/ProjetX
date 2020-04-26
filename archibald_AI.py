def control_is_worth (team, peaks, ships, units_stats) :
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
    #not worth if total_peak_energy from our half of the map <= total_tanker_storage + units_stats[team]['tanker']['max_energy'] (for each tanker storage = units_stats[team]['tanker']['max_energy'])
    control_is_worth = True
    nb_tanker = 0
    our_peak_energy = 0
    for ship in ships :

        if ships[ship]['type'] == 'tanker':
            nb_tanker += 1

    total_tanker_storage = nb_tanker * units_stats[team]['tanker']['max_energy']

    favorable_peaks = peaks_on_our_map_side(team, units_stats, peaks)
    
    for peak in favorable_peaks:

        our_peak_energy += peaks[peak]['storage']

    if our_peak_energy > total_tanker_storage + units_stats[team]['tanker']['max_energy']:
        
        is_worth = False # not worth making tankers anymore
    
    #create cruisers if soon reach the hub's storage limit
    tanker_list = []
    total_tankers_current_energy = 0
    
    for ship in ships: 

        if ships[ship]['type'] == 'tanker':
            tanker_list.append(ship)

    for tanker in tanker_list:

        total_tankers_current_energy += ships[tanker]['energy_point']

    if units_stats[team]['hub']['energy_point'] + total_tanker_current_energy >= units_stats['common']['hub']['max_energy_point']:
        create_cruiser(team, units_stats, ships)
    

    

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
    #get favorable_peak names and add them to the peak_name list. Also add their coordinates to the peaks_coord list
    for peak in favorable_peaks:
       
        peaks_coord.append(peaks[peak]['coordinates'])
        peak_name.append(peak)
    
    #index the lenght of peaks_coord list
    for index in range(len(peaks_coord)) :
       
        number = 1
        our_grouped_peaks[number] = [] 

        for index_2 in range (len(peaks_coord)) :
            #check if distance between peaks is smaller than 4
            if count_distance (peaks_coord[index], peaks_coord[index_2]) < 4 :
                our_grouped_peaks[number].append (peak_name[index_2])
               
    return our_grouped_peaks

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

def create_cruiser(team, units_stats, ships):
    """
    Parameters
    ----------
    team : name of the team which is playing (str)   
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    instruction_list : adds instruction to create the wished cruiser to the instruction_list (str)
    
    """
    used_cruiser_indexes = []
    
    #get all cruisers from ships into a list
    create_selected_type_list_from_ships(ships, 'cruiser')
    #go through all cruisers to create a list of all used cruiser indexes
    for cruiser in cruiser_list:

        split_cruiser_names = cruiser.split('_')
        select_cruiser_index = split_cruiser_names[1]
        used_cruiser_indexes.append(select_cruiser_index)

    #add team name and 1 to the highest used index for the next created cruiser
    next_index_to_use = max(used_cruiser_indexes) + 1
    cruiser_name = 'cruiser_%s_%s',team, next_index_to_use
    created_cruiser = 'cruiser:' + cruiser_name
    #add the creation instruction to the instruction_list
    instruction_list.append(created_cruiser)

def create_tanker(team, units_stats, ships):
    """
    Parameters
    ----------
    team : name of the team which is playing (str)   
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats : dictionary with the stats (different or common) of the teams (hub /ship) (dict)

    Return
    ------
    instruction_list : adds instruction to create the wished tanker to the instruction_list (str)
    
    """
    used_tanker_indexes = []
    
    #get all cruisers from ships into a list
    tanker_list = create_selected_type_list_from_ships(ships, 'tanker')
    #go through all cruisers to create a list of all used cruiser indexes
    for tanker in tanker_list:

        split_tanker_names = tanker.split('_')
        select_tanker_index = split_tanker_names[1]
        used_tanker_indexes.append(select_tanker_index)

    #add team name and 1 to the highest used index for the next created cruiser
    next_index_to_use = max(used_tanker_indexes) + 1
    tanker_name = 'tanker_%s_%s',team, next_index_to_use
    created_tanker = 'cruiser:' + tanker_name
    #add the creation instruction to the instruction_list
    instruction_list.append(created_tanker)

def create_selected_type_list_from_ships(ships, type):
    """
    Parameters
    ----------
    ships : dictionary with the statistics of each ship (tanker or cruiser)(dict)
    type : ship type (tanker or cruiser) you want  (str)

    Return
    ------
    <selected_type>_list : makes a list of the selected type from the ships list (list)

    """
    if type == 'tanker':
        tanker_list = []        
        for ship in ships:

            if ships[ship]['type'] == type:      
            
                tanker_list.append(ship)
        
        return tanker_list
    
    if type == 'cruiser':
        cruiser_list = []
        for ship in ships:

            if ships[ship]['type'] == type:

                cruiser_list.append(ship)
        
        return cruiser_list
    

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
    favorable_peaks_coordinates = []
    #get coordinates of each favorable peak
    for peak in favorable_peaks : 
        
        favorable_peaks_coordinates.append(peaks[peak]['coordinates'])
        
    #get coordinates of each ennemy ship
    for ship in ships:
        
        if ships[ship]['team'] == ennemy_team and ships[ship]['type'] == 'tanker':
           ennemy_tanker_coordinates = []
           ennemy_tanker_coordinates.append(ships[ship]['coordinates'])

        elif ships[ship]['team'] == ennemy_team and ships[ship]['type'] == 'cruiser':
            ennemy_cruiser_coordinates = []
            ennemy_cruiser_coordinates.append(ships[ship]['coordinates'])

    #check distance between each ennemy tanker and our peaks
    for tanker_coordinates in ennemy_tanker_coordinates:

        for peak_coordinates in favorable_peaks_coordinates:

            distance = count_distance (peak_coordinates, tanker_coordinates)  
            
            if distance <= 10 :

                alert_tanker = True
                nb_tankers += 1
                
    #check distance between each ennemy cruiser and our peaks
    for cruiser_coordinates in ennemy_cruiser_coordinates:

        for peak_coordinates in favorable_peaks_coordinates:

            distance = count_distance(peak_coordinates, tanker_coordinates)

            if distance <= 10 :
                
                alert_cruiser = True
                nb_cruisers += 1
