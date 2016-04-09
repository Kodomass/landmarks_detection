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
                   '--type ushort --seed $i\n' % (target_dir_name, lm_id, scale, 
                       target_dir_name, lm_id, scale, ini_dir, lm_id, scale ))

        fid_train.write( 'done\n\n' )

    fid_train.close()