if range_verification (units_stats, distance, ships, team):
            ships[cruiser]['target'] = 'hub'
            ships[cruiser]['coordinate_to_go'] = hub_coordinate
        #else move the cruiser close to the hub and check if an other cruiser is on the nearest case. 
        else :
            instruction = attack_cruiser_offensive (cruiser,alive_ennemy_cruiser, ships)
            if not(instruction) : 
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