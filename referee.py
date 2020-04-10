import remote_play

def start_referee(group_1, group_2):
    """Starts a referee between two groups.
    
    Parameters
    ----------
    group_1: id of the first group (int)
    group_2: id of the second group (int)
    
    Notes
    -----
    The referee will run forever, unless you stop it (Ctrl+C or close the terminal).
    
    """
    
    # create connections
    connections = remote_play.bind_referee(group_1, group_2, verbose=True)

    # main loop (until one of/or both players exits)
    stop = False
    while not stop:
        try:
            for player_id in (1, 2):
                msg = remote_play.get_remote_orders(connections[player_id])
                print('player %d sent: "%s"' % (player_id, msg))
                remote_play.notify_remote_orders(connections[3-player_id], msg)
                
            print('\n------------------------\n')
        except:
            stop = True
            print('\n at least one of the players has exited -> referee will stop')
    
    # close connections
    for player_id in (1, 2):
        remote_play.close_connection(connections[player_id])