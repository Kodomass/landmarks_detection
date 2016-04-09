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