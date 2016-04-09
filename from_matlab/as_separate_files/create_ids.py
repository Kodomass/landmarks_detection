def create_ids(all_landmark_names):
    ids = []

    for i in range(len(all_landmark_names)):
        ids.append('1%02d' % (i+1))
    
    return ids