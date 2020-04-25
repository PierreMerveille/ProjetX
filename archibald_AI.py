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
    #not worth if total_peak_energy from our half of the map <= total_tanker_storage + 900 (for each tanker storage = units_stats[team]['tanker']['max_energy'])
    control_is_worth = True
    for ship in ships :
        if ships[ship]['type'] == 'tanker':
            nb_tanker += 1

    total_tanker_storage = nb_tanker * units_stats[team]['tanker']['max_energy']

    for peak in peaks :
        total_peak_energy += peaks[peak]['storage']

    if total_peak_energy <= total_tanker_storage:
        is_worth = False # --> stop making tankers

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