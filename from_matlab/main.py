import os
import sys
import numpy as np

def main():

    data_dir = ''

    (res, landmarks_count_map, exs_TC) = read_all_landmark_data(data_dir)

    all_landmark_names = sorted(list(landmarks_count_map.keys()))
    ids = create_ids( all_landmark_names )

    num_folds = 10

    for i, lmk_name in enumerate(all_landmark_names):

        current_counts = landmarks_count_map[lmk_name]

        # based on the current fold create training and testing ids
        folds_indices = create_training_testing_ids( current_counts, num_folds )

        for f in range(num_folds):

            target_dir_name = 'lms_fold_%02d_of_%02d' % ((f+1), num_folds)

            if not os.path.exists(target_dir_name):
                os.makedirs(target_dir_name)

            write_id_to_name_file( ('%s/names' % target_dir_name ), 
                                    ids, all_landmark_names )

            create_configuration_files_for_landmark(ids[i], lmk_name,
                folds_indices[f], res, target_dir_name, data_dir, exs_TC, f)


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


def read_individual_landmark_file(fname):
    
    fid = open(fname, 'r')
    for i in range(3):
        skip = fid.readline()
        
    ret = []
    lines = fid.readlines()

    for r in lines:

        # first check that there are 13 commas (to make a viable string)
        if (13 != r.count(',')):
            sys.exit()
        
        # columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID
        (id, x, y, z, ow, ox, oy, oz, vis, sel, lock, label,
         desc, associatedNodeID) = r.split(',')

        ret.append({
                    'x' : float(x), 
                    'y' : float(y), 
                    'z' : float(z), 
                    'ow' : float(ow),
                    'ox' : float(ox),
                    'oy' : float(oy),
                    'oz' : float(oz),
                    'label' : label
                    })
    fid.close()
    
    return ret

def read_existence_file(fName):
    fid = open(fName, 'r')
    skip = fid.readline()

    lmk_exists = {}
    for line in fid.readlines():
        if line.strip():
            (fn, ex) = line.split()
            lmk_exists[fn[:4]] = bool(int(ex))
    
    fid.close()
    
    return lmk_exists


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

def create_ids(all_landmark_names):
    ids = []

    for i in range(len(all_landmark_names)):
        ids.append('1%02d' % (i+1))
    
    return ids

def create_training_testing_ids(num_counts, num_folds):
    
    elements_per_fold = num_counts//num_folds
    fold_elements = [elements_per_fold] * num_folds

    remaining = num_counts-sum( fold_elements )
    
    for i in range(remaining):
        fold_elements[i] += 1

    id_tos = np.cumsum( fold_elements )
    id_froms = [1] + [x+1 for x in id_tos[:-1]];
    
    folds_indices = [{ 'indx_training' : [], 
                       'indx_testing' : [] } for i in range(num_folds)]

    for i in range(num_folds):
        
        folds_indices[i]['indx_testing'] = list(range(id_froms[i], id_tos[i]+1))
        folds_indices[i]['indx_training'] = []

        for j in range(i):
            folds_indices[i]['indx_training'] +=  list(range( id_froms[j], id_tos[j]+1 ))

        for j in range(i+1,num_folds):
            folds_indices[i]['indx_training'] +=  list(range( id_froms[j], id_tos[j]+1 ))

    return folds_indices

def write_ini_file(lm_id, lm_file, ini_dir, 
                   detectors_dir, scale, 
                   spacing, box_radius, 
                   training_sample_number_per_radius ):

    ini_file_name = ( '%s/landmark_%s_R%d.ini' % (ini_dir, lm_id, scale) )

    fid = open( ini_file_name, 'w' )

    fid.write( '[General]\n' )
    fid.write( 'Name=%s\n' % lm_id )
    fid.write( 'Annotation=%s\n' % lm_file )
    fid.write( 'RootFolder=%s\n'% detectors_dir )
    fid.write( 'Level=0\n' )
    fid.write( 'Scale=%d\n' % scale )
    fid.write( 'Spacing=%d %d %d\n' % (spacing, spacing, spacing ))
    fid.write( 'BoxRadius=%d\n' % box_radius )
    fid.write( 'TrainingSampleNumberPerRadius=%d\n' % training_sample_number_per_radius )
    fid.write( 'RadiusStep=1\n' )
    fid.write( 'ContextDetectorNames=\n' )
    fid.write( '[Forest]\n' )
    fid.write( 'NumTrees=1\n' )
    fid.write( 'MaxTreeDepth=20\n' )
    fid.write( 'NumThresholds=100\n' )
    fid.write( 'NumWeakLearners=1000\n' )
    fid.write( 'MinLeafNum=8\n' )
    fid.write( 'MinInfoGain=0\n' )
    fid.write( '[Intensity]\n' )
    fid.write( 'Weight=1\n' )
    fid.write( 'FilterSize=3 5\n' )
    fid.write( 'PatchSize=30 30 30\n' )
    fid.write( 'Normalization=NONE\n' )

    fid.close()
    
def write_id_to_name_file( fn, ids, all_landmark_names ):

    fid = open( fn, 'w' )

    for i, names in enumerate(all_landmark_names):
        fid.write( '%s %s\n' % (ids[i], all_landmark_names[i]) )


    fid.close()

    return ids

def create_configuration_files_for_landmark(lm_id, lm_name, fold_indices, res,
                                            target_dir_name, data_dir, exs_TC , f):

    if not os.path.exists(target_dir_name):
            os.makedirs(target_dir_name)

    ini_dir = '%s/ini' % target_dir_name
    detectors_dir = '%s/detectors' % target_dir_name

    if not os.path.exists(ini_dir):
            os.makedirs(ini_dir)

    if not os.path.exists(detectors_dir):
            os.makedirs(detectors_dir)

    test_results_dir = '%s/testResults' % target_dir_name
    if not os.path.exists(test_results_dir):
            os.makedirs(test_results_dir)

    test_train_results_dir = '%s/testTrainResults' % target_dir_name
    if not os.path.exists(test_train_results_dir):
            os.makedirs(test_train_results_dir)

    # create landmark file for training 
    # and file for testing

    root_folder = '%s/detectors' % target_dir_name

    lm_file_name = '%s/Landmark_%s.txt' % (target_dir_name, lm_id)
    fid = open( lm_file_name, 'w' )

    tst_lm_file_name = '%s/test_Landmark_%s.bash' % (target_dir_name, lm_id)
    tst_lm_file_name_old = '%s/test_Landmark_%s.txt' % (target_dir_name, lm_id )
    # remove old file if it exist
    if os.path.exists(tst_lm_file_name_old):
        os.remove(tst_lm_file_name_old)

    fid_tst = open( tst_lm_file_name, 'w' )
    fid_tst.write('#! /usr/bin/env bash\n\n' )
    fid_tst.write('source ~/.bash_profile\n\n' )


    # also open a file so we run the detection on the training data
    lm_test_train_file_name = ('%s/testTrain_Landmark_%s.bash' % 
                               (target_dir_name, lm_id ))
    fid_tst_train = open( lm_test_train_file_name, 'w' )
    fid_tst_train.write('#! /usr/bin/env bash\n\n' )
    fid_tst_train.write('source ~/.bash_profile\n\n' )

    current_id = 1
    
    for key in sorted(res):
        data = res[key]
        
        for j,rec in enumerate(data):
            
            if lm_name == rec['label']:
                c_name = key[:4]

                image_path = '%s/%s_INPUT.nrrd' % (data_dir, c_name)

                TC_exists = exs_TC[c_name]

                # make sure that if we are looking at the trachea carina,
                # it actually exists in the dataset
                if not 'TracheaCarina' == lm_name or TC_exists:
                    
                    # check if the current id should be
                    # in the training or testing set
                    
                    if current_id in fold_indices['indx_training']:

                        fid.write('%s/%s_INPUT.nrrd\n' % (data_dir, c_name ))
                        fid.write('Annotator\t %s\t -1\t -1\t -1\t %f\t %f\t %f\n' % 
                            (lm_id, -rec['x'], -rec['y'],rec['z'] ))
             
                        # also do it for testTrain, incase we want to test i
                        # on the training data as a sanity check
                        bsub_command = ('bsub -M 16 -R "span[hosts=1]" -q day  '
                                '-e %s/testTrainResults/err_test_%s_%s.txt '
                                '-o %s/testTrainResults/out_test_%s_%s.txt' %
                                (target_dir_name, lm_name, c_name, 
                                 target_dir_name, lm_name, c_name )) 

                        test_command = ('%s ContextLandmarkDetection --lm '
                            '--vote --image %s --root %s --names %s '
                            '--level 0'' --maxscale 3 --minscale 1 '
                            '--out %s/testTrainResults/out_%s_%s.txt' % 
                            (bsub_command, image_path, root_folder, lm_id, 
                             target_dir_name, lm_name, c_name ))
    
                        fid_tst_train.write('%s\n' % test_command )
             
                    else: # must be testing

                        bsub_command = ('bsub -M 16 -R "span[hosts=1]" -q day  '
                            '-e %s/testResults/err_test_%s_%s.txt '
                            '-o %s/testResults/out_test_%s_%s.txt' % 
                            (target_dir_name, lm_name, c_name,
                             target_dir_name, lm_name, c_name ))
                        
                        test_command = ('%s ContextLandmarkDetection --lm '
                            '--vote --image %s --root %s --names %s --level 0 '
                            '--maxscale 3 --minscale 1 '
                            '--out %s/testResults/out_%s_%s.txt' % 
                            (bsub_command, image_path, root_folder, lm_id, 
                             target_dir_name, lm_name, c_name ))
    
                        fid_tst.write('%s\n' % test_command )
             
                        # sanity check
                        if not current_id in fold_indices['indx_testing']:
                            print( 'Expected to find id in the testing id set,'
                                   'but could not find it.\n' )
             
                    current_id += 1
    
    fid_tst_train.close()
    fid_tst.close()
    fid.close()
  
    # create ini files
    scales = [1, 2, 3]
    spacings = [1, 2, 4]
    box_radii = [15, 30, 300]
    training_sample_numbers_per_radius = [400, 200, 150]
    
    for i in range(3):
        write_ini_file( lm_id, lm_file_name, ini_dir, 
                        detectors_dir, scales[i], spacings[i], 
                        box_radii[i], training_sample_numbers_per_radius[i] )

    # now write the scripts necessary for the training

    script_file_name = ('%s/train_Landmark_%s.bash' % (target_dir_name, lm_id ))
    fid_train = open( script_file_name, 'w' )

    fid_train.write( '#! /usr/bin/env bash\n\n' )
    fid_train.write( 'source ~/.bash_profile\n\n' )

    for scale in range(1,4):
        fid_train.write( 'for((i=1;i<=10;++i))\n' )
        fid_train.write( 'do\n' )
        fid_train.write( '  bsub -n 4 -M 16 -R "span[hosts=1]" -q day '
                   '-e %s/err_%s_%d_seed_$i.txt -o %s/out_%s_%d_seed_$i.txt '
                   'ContextLandmarkTrain --file %s/landmark_%s_R%d.ini '
                   '--type short --seed $i\n' % (target_dir_name, lm_id, scale, 
                       target_dir_name, lm_id, scale, ini_dir, lm_id, scale ))

        fid_train.write( 'done\n\n' )

    fid_train.close()

if __name__ == "__main__":
    main()
