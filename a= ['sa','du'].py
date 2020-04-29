    nbr_cruiser = 0
    if nbr_cruiser != 0 : 
        nb_line = 1 
        
        if nbr_cruiser > 5: 
            nb_line+= 1 
            if nbr_cruiser > 14 :
                nb_line+= 1
    if column_str == 'left' :
        column_shift = -1
    else :
        column_shift = 1
    if row_str == 'up' :
        row_shift = -1
    else :
        row_shift = 1 
    
    for y in range (1, (nb_line+1)*column_shift, column_shift) :
        for x in range(-abs(y),abs(y)+1) :
            coord += ((ally_hub[0] + x, ally_hub[1]+ y )

    for x in range (1, (nb_line+1)*row_shift, row_shift) :
        for y in range(-abs(x),abs(x)+1) :
            coord += ((ally_hub[0] + x, ally_hub[1]+ y )

def order_coord(coord, units_stats) :

    for coordinates in coord :
        for other_coordinates in coord :
            if count_distance(coordinates,units_stats[team]['hub']['coordinates']) > count_distance(other_coordinates,units_stats[team]['hub']['coordinates'])  :
                coordinates = other_coordinates
        order_coord.append(coordinates)
    return order_coord

coord = order_coord(coord,units_stats)
coord_void = verif_if_ship_on_coord(coord, alive_cruiser)
cruiser_place = place_ship(coord_void, cruiser_place, alive_cruiser)
