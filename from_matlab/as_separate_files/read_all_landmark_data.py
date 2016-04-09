import os

def read_all_landmark_data( data_dir ):
  
    res = {}
    d = ( f for f in os.listdir(data_dir) if f.endswith('.fcsv') )
    
    for f in d:
        print ('Reading', f)
        res[f] = read_individual_landmark_file( data_dir + '/' + f )
    
    tc_existence_map = read_existence_file( 'trachea_carina.txt')
    
    remap_array = {
            'Subglottis' : 'Subglottic',
            'Sunglottis' : 'Subglottic',
            'TongueBase' : 'BaseOfTongue',
            'PosteriorInferiorVomerCorner ' : 'PosteriorInferiorVomerCorner',
            'PosterInferiorVomerCorner' : 'PosteriorInferiorVomerCorner'
                }
    
    remove_array = [ '1013_LOWER-1' ]

    (landmarks_count_map, res) = determine_all_landmark_names( res,
            remap_array, remove_array, tc_existence_map )
    
    
    return res, landmarks_count_map, tc_existence_map