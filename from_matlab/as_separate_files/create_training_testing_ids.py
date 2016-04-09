import numpy as np

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