import os
import numpy as np
import main as m
import matplotlib.pyplot as plt

def evaluate_landmark_detection_results():

    data_dir = ''
    evaluate_test_train = False

    (res, count_map, exs_tc) = m.read_all_landmark_data(data_dir)

    results_map = {}
    for key in count_map:
        results_map[key] = []

    for i in range(1,2):

        if evaluate_test_train:
            current_res_dir = ( 'lms_fold_%02d_of_05/testTrainResults' % i )
        else:
            # current_res_dir = ( 'lms_fold_%02d_of_05/testResults' % i )
            current_res_dir = ( 'lms_manual_split/testResults' )


        d = ( f for f in os.listdir(current_res_dir) if f.startswith('out_')
             and f.endswith('.txt') )

        for f in d:

            fid = open( ('%s/%s' % (current_res_dir, f)), 'r' )
            info = fid.readline()
            fid.close()
            vals = info.split()
            xyz = [ float(x) for x in vals[4:] ]
            xyz[0] = -xyz[0]
            xyz[1] = -xyz[1]

            landmark_name = f.split('_')[1]
            file_number = f.split('_')[2].split('.')[0]

            data = res[file_number + '_LANDMARKS.fcsv']

            for lmk in data:
                if lmk['label'] == landmark_name:

                    vals = {}
                    vals['manual'] = [ lmk['x'], lmk['y'], lmk['z'] ]
                    vals['detected'] = xyz
                    results_map[landmark_name].append( vals )

    # now do actual evaluation

    d_list = []
    x_list = []
    y_list = []
    z_list = []

    for lmk_name in sorted(results_map):

        manual_vals = []
        detected_vals = []

        for val in results_map[lmk_name]:
            manual_vals.append(val['manual'])
            detected_vals.append(val['detected'])

        np_manual_vals = np.array(manual_vals)
        np_detected_vals = np.array(detected_vals)

        diffs = np_manual_vals - np_detected_vals
        mean_diffs = np.mean( diffs, axis = 0)
        distances = np.sqrt( np.sum( np.square(diffs), axis=1 ) )

        print( 'Results for landmark: %s', lmk_name )
        print( 'Means: x = %f, y = %f, z = %f' %
                (mean_diffs[0], mean_diffs[1], mean_diffs[2]) )

        d_list.append(distances)
        x_list.append(diffs[:,0])
        y_list.append(diffs[:,1])
        z_list.append(diffs[:,2])

    lmks = [name for name in sorted(count_map) ]
    lmks[6] = 'PIVomerCorner'

    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(left=0.2)
    ax = fig.add_subplot(111)
    ax.boxplot(d_list, vert=0)
    ax.plot([0,0],[0,13], color='k')
    ax.set_title('distances')
    ax.set_yticklabels(lmks)

    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(left=0.2)
    ax = fig.add_subplot(111)
    ax.boxplot(x_list, vert=0)
    ax.plot([0,0],[0,13], color='k')
    ax.set_title('differences in x')
    ax.set_yticklabels(lmks)

    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(left=0.2)
    ax = fig.add_subplot(111)
    ax.boxplot(y_list, vert=0)
    ax.plot([0,0],[0,13], color='k')
    ax.set_title('differences in y')
    ax.set_yticklabels(lmks)

    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(left=0.2)
    ax = fig.add_subplot(111)
    ax.boxplot(z_list, vert=0)
    ax.plot([0,0],[0,13], color='k')
    ax.set_title('differences in z')
    ax.set_yticklabels(lmks)

    plt.show()


if __name__ == "__main__":
    evaluate_landmark_detection_results()

