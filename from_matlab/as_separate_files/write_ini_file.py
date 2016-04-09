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