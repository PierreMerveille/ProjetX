def find_nb_rounds(team, ships, units_stats, AI_stats):
    """Finds the number of rounds you'd have to wait until you can create a new tanker (without taking into account the hub regeneration)

    Parameters
    ----------

    team : name of the team which is playing (str)   
    ships :  dictionary with the statistics of each ship (tanker or cruiser)(dict)
    units_stats :dictionary with the stats (different or common) of the teams (hub /ship) (dict)
    AI_stats : 

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

    """
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
        
