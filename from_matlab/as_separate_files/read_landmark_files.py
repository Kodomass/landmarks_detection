import os

data_dir = '~/992/test_data/nrrd_sample'

(res, landmarks_count_map, exs_TC) = read_all_landmark_data(data_dir)

all_landmark_names = sorted(list(landmarks_count_map.keys()))
ids = create_ids( all_landmark_names )

num_folds = 5

for i, lmk_name in enumerate(all_landmark_names):
    
    current_counts = landmarks_count_map[lmk_name]
    
    # based on the current fold create training and testing ids
    folds_indices = create_training_testing_ids( current_counts, num_folds )

    for f in range(num_folds):

        target_dir_name = 'lms_fold_%02d_of_%02d' % ((f+1), num_folds)

        if not os.path.exists(target_dir_name):
            os.makedirs(target_dir_name)

        write_id_to_name_file( ('%s/names' % target_dir_name ), ids, all_landmark_names )
        
        create_configuration_files_for_landmark(ids[i], lmk_name,
            folds_indices[f], res, target_dir_name, data_dir, exs_TC, f)
