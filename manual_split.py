import main as m
import re
import os

def main():

    data_dir = '/Users/Abzhan/992/test_data/nrrd_sample'

    testing_data_dir = '/Users/Abzhan/992/test_data/Centerline_Data'

    ds_index_pattern = re.compile("[0-9]{4}")
    d = ( f for f in os.listdir(testing_data_dir) if ds_index_pattern.match(f) )

    testing_set_indices = [f[:4] for f in d]

    print(len(testing_set_indices),
            'Testing dataset indices: ', testing_set_indices)

    (res, landmarks_count_map, exs_TC) = m.read_all_landmark_data(data_dir)

    all_landmark_names = sorted(list(landmarks_count_map.keys()))
    ids = m.create_ids( all_landmark_names )

    for i, lm_name in enumerate(all_landmark_names):

        target_dir_name = 'lms_manual_split'

        if not os.path.exists(target_dir_name):
            os.makedirs(target_dir_name)

        m.write_id_to_name_file( ('%s/names' % target_dir_name ), ids, all_landmark_names )

        create_config_files(ids[i], lm_name, res, target_dir_name,
                data_dir,exs_TC, testing_set_indices)



    print('Done!')


def create_config_files(lm_id, lm_name, res, 
                        target_dir_name, data_dir,exs_TC,
                        testing_set_indices):
 
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

    # create landmark file for training
    # and file for testing

    root_folder = '%s/detectors' % target_dir_name

    lm_file_name = '%s/Landmark_%s.txt' % (target_dir_name, lm_id)
    fid = open( lm_file_name, 'w' )

    tst_lm_file_name = '%s/test_Landmark_%s.bash' % (target_dir_name, lm_id)

    fid_tst = open( tst_lm_file_name, 'w' )
    fid_tst.write('#! /usr/bin/env bash\n\n' )
    fid_tst.write('source ~/.bash_profile\n\n' )

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
 
                    if not c_name in testing_set_indices:

                        fid.write('%s/%s_INPUT.nrrd\n' % (data_dir, c_name ))
                        fid.write('Annotator\t %s\t -1\t -1\t -1\t %f\t %f\t %f\n' % 
                            (lm_id, -rec['x'], -rec['y'],rec['z'] ))
 
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
 
    fid_tst.close()
    fid.close()
 
    # create ini files
    scales = [1, 2, 3]
    spacings = [1, 2, 4]
    box_radii = [15, 30, 300]
    training_sample_numbers_per_radius = [400, 200, 150]
 
    for i in range(3):
        m.write_ini_file( lm_id, lm_file_name, ini_dir,
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
 
# end create_config_files

if __name__ == "__main__":
    main()

