def write_id_to_name_file( fn, ids, all_landmark_names ):

    fid = open( fn, 'w' )

    for i, names in enumerate(all_landmark_names):
        fid.write( '%s %s\n' % (ids[i], all_landmark_names[i]) )


    fid.close()

    return ids