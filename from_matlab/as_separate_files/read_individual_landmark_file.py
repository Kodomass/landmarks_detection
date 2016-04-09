import sys

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