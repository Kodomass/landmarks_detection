def determine_all_landmark_names(data, remap_array, remove_array, tc_exs_map):

    string_count_map = {}
    
    for key in sorted(data):
        
        #  because it is an ID of the form 1108_...
        current_case_name = key.split('_')[0]
        tc_exists = tc_exs_map[ current_case_name ]

        for j, landmark in enumerate(data[key]):

            c_label = landmark['label']

            if c_label in remap_array:
                print('Remapping label: %s -> %s' % (c_label,remap_array[c_label]))
                c_label = remap_array[c_label]
                data[key][j]['label'] = c_label

            if not c_label in remove_array:
                # make sure we do not count fake trache carinas
                if not 'TracheaCarina' == c_label  or  tc_exists:
                    if not c_label in string_count_map:
                        print('Found label %s' % c_label )
                        string_count_map[c_label] = 1
                    else:
                        string_count_map[c_label] += 1

    print( '\nFrequency of landmarks:' )
    print( '-----------------------' )

    for key in sorted(string_count_map):
        print( '%s -> %d' % (key, string_count_map[key]) )

    return string_count_map, data