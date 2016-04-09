import pdb
import sys
import os
import math
import matplotlib.pyplot as plt
from enum import Enum

class Landmark():

    labels = [ 
                'BaseOfTongue',
                'Columella',
                'EpiglottisTip',
                'LeftAlaRim',
                'NasalSpine',
                'NoseTip',
                'PosteriorInferiorVomerCorner',
                'PyrinaAperture',
                'RightAlaRim',
                'Subglottic',
                'TVC',
                'TracheaCarina',
             ]

    landmark_code_base = 101
    
    remap_labels = {
        'Subglottis' : 'Subglottic',
        'Sunglottis' : 'Subglottic',
        'TongueBase' : 'BaseOfTongue',
        'PosterInferiorVomerCorner' : 'PosteriorInferiorVomerCorner'
                    }
    
    @classmethod
    def get_code_by_label(cls, lmk_name):

        if lmk_name not in cls.labels:
            print('Landmark name is not correct %s'% lmk_name)
            sys.exit(1)
        else:
            return str(cls.landmark_code_base + cls.labels.index(lmk_name))

    @classmethod
    def get_label_by_code(cls, code):
        
        try:
            index = int(code)
        except ValueError:
            print('Incorrect landmark code value: %. Must be integer' % code)
            sys.exit(1)
            
        index = index - 101
        try:
            landmark = cls.labels[index]
        except IndexError as e:
            print('Incorrect landmark code value: %s.' % code)
            print(e)
            sys.exit(1)

        return landmark

    @classmethod
    def is_valid_label(cls, label):
        return label in cls.labels

    @classmethod
    def is_valid_code(cls, code):
        try:
            label = cls.get_label_by_code(code)
            return True
        except Exception as e:
            return False
    
    @classmethod
    def __str__(cls):
        output_str = ''
        for name in cls.labels:
            output_str += ('%s:%s\n' % (name, cls.get_code_by_label(name)))
        return output_str

    @classmethod
    def remap_label(cls, label):
        if label in cls.remap_labels:
            return cls.remap_labels[label]
        else:
            return label


class DatasetType(Enum):
    fcsv = 1
    individual = 2
    combined = 3


# class that represents lmk data for a set of images
class LandmarksDataset():
 
    def __init__(self, path_to_datasets, dataset_type, 
                 exclude_landmarks = None):

        self.exclude = exclude_landmarks
        
        if not os.path.exists(path_to_datasets):
            print("Folder '%s' does not exist" % path_to_datasets )
            sys.exit(1)
        
        try:
            self.type = dataset_type
        except Exception as e:
            print(e)
            sys.exit(1)

        if self.type == DatasetType.fcsv:
            self.data = self.read_fcsv_in_folder( path_to_datasets )
        elif self.type == DatasetType.individual:
            self.data = self.read_individual_files_in_folder( 
                    path_to_datasets )
        elif self.type == DatasetType.combined:
            self.data = self.read_combined_files_in_folder( 
                    path_to_datasets )
        
        if not self.type == DatasetType.fcsv:
            self.inver_x_y_coordinates()
        pass

    def read_individual_files_in_folder(self, path):
        data = {}
        files = ( f for f in os.listdir(path) if 
                    f.startswith('out_') and f.endswith('.txt') )
        for f in files:
            dataset_id = f.split('_')[2].split('.')[0]
            lmk_label  = f.split('_')[1]
            with open( ('%s/%s' % (path,f) ), 'r' ) as infile:
                line = infile.readline().split()
                code = line[0]
                x = float( line[4] )
                y = float( line[5] )
                z = float( line[6] )

            try:
                code == Landmark.get_code_by_label(lmk_label)
            except Exception as e:
                print('Lanmdark label %s and code %s mismatch' % 
                        (lmk_label, code))
                pritn(e)
                sys.exit(1)
            if dataset_id not in data:
                data[dataset_id] = {}
            data[dataset_id][lmk_label] = [x, y, z]
        
        return data

    def read_combined_files_in_folder(self, path):
        data = {}
        files = ( f for f in os.listdir(path) if 
                    f.startswith('out_all') and f.endswith('.txt') )
        for f in files:
            dataset_id = f.split('_')[2].split('.')[0]
            with open( ('%s/%s' % (path,f) ), 'r' ) as infile:
                for line in infile.readlines():
                    line = line.split()
                    code = line[0]
                    x = float( line[4] )
                    y = float( line[5] )
                    z = float( line[6] )
                
                    lmk_label = Landmark.get_label_by_code(code)
                    if dataset_id not in data:
                        data[dataset_id] = {}
                    data[dataset_id][lmk_label] = [x, y, z]
        
        return data

    def read_fcsv_in_folder(self, path):
        
        data = {}        
        
        files = ( f for f in os.listdir(path) if f.endswith('.fcsv') )

        for f in files:
            dataset_id = f.split('_')[0]
            lmk_data = self.read_single_fcsv( ('%s/%s' % (path, f)) )
            
            if self.exclude:
                to_exclude = []
                for lmk in lmk_data:
                    if self.exclude.contains(lmk, dataset_id):
                        to_exclude.append(lmk)
                for lmk in to_exclude:    
                    del(lmk_data[lmk])
            
            if lmk_data: 
                data[dataset_id] = lmk_data

        return data

    def read_single_fcsv(self, path):

        landmarks = {}
        with open(path, 'r') as infile:
            for i in range(3):
                skip = infile.readline()

            for line in infile.readlines():

                # check that there are 13 commas (to make a viable string)
                if (13 != line.count(',')):
                    print('fcsv file % has different structure' % path) 
                    sys.exit(1)

                x = float(line.split(',')[1].strip())
                y = float(line.split(',')[2].strip())
                z = float(line.split(',')[3].strip())
                lmk = line.split(',')[11].strip()
                lmk = Landmark.remap_label(lmk)
                
                landmarks[ lmk ] = [x, y, z]

        return landmarks
    
    def inver_x_y_coordinates(self):
        for dataset_id in self.data:
            for lmk  in self.data[dataset_id]:
                self.data[dataset_id][lmk][0] = - self.data[dataset_id][lmk][0]
                self.data[dataset_id][lmk][1] = - self.data[dataset_id][lmk][1]
                

    def get_dataset_ids(self):
        """Returns a list of dataset ids
        """
        return sorted([ key for key in self.data ])

    def __str__(self):
        output = '{\n'
        for key, value in self.data.items():
            output += ( "\t'%s':%s\n" % (key, value) )
        output += '}'
        return output
    
    def write_all_fcsv(self, path_to_folder, subname=None):
        if path_to_folder[-1] == '/':
            path_to_folder = path_to_folder[:-1]
        for dataset_id in sorted(self.data.keys()):
            self.write_one_fcsv(dataset_id, path_to_folder, subname)

    def write_one_fcsv(self, dataset_id, path_to_folder, subname=None):
        
        if not os.path.exists(path_to_folder):
            print("Incorrect folder '%s' " % path_to_folder )
            sys.exit(1)

        if dataset_id not in self.data:
            print('Dataset %s is missing' % dataset_id)
            sys.exit(1)

        if subname:
            file_name = ( '%s_%s.fcsv' % ( dataset_id, subname) )
        else:
            file_name = ( '%s_lmks.fcsv' % dataset_id )
        
        file_path = '%s/%s' % (path_to_folder, file_name )

        fcsv = open(file_path, 'w')

        fcsv_header = ( '# Markups fiducial file version = 4.4\n'
                        '# CoordinateSystem = 0\n'
                        '# columns = id,x,y,z,ow,ox,oy,oz,vis,'
                        'sel,lock,label,desc,associatedNodeID\n' )
        fcsv.write(fcsv_header)
        fcsv.close()

        fcsv = open(file_path,'a')
        for lmk in sorted(self.data[dataset_id].keys()):
            
            [x, y, z] = self.data[dataset_id][lmk]
            line =( 'vtkMRMLMarkupsFiducialNode_1,%.4f,%.4f,%.4f,'
                    '0,0,0,1,1,1,0,%s,,vtkMRMLScalarVolume1\n' % (x,y,z,lmk) )
            
            fcsv.write(line)

        fcsv.close()

        print('File '+file_path+' has been created')




class LandmarksToExclude():

    def __init__(self):
        self.data = {}

    def read_existence_file(self, label, path):
        if Landmark.is_valid_code(label):
            label = Landmark.get_label_by_code(label)
        if label not in self.data:
            self.data[label] = []

        with open(path, 'r') as infile:
            skip = infile.readline()
            for line in infile:
                if not line.strip():
                    continue
                [dataset_name, flag] = line.split()
                dataset_id = dataset_name.split('_')[0]
                if not int(flag):
                    self.data[label].append(dataset_id)

    def add_landmark_dataset_pair(self, label, dataset_id):
        if Landmark.is_valid_code(label):
            label = Landmark.get_label_by_code(label)
        if label not in self.data:
            self.data[label] = [ dataset_id ]
        else:
            self.data[label].append( dataset_id )

    def contains(self, label, dataset_id):
        if label not in self.data:
            return False
        else:
            if dataset_id not in self.data[label]:
                return False
            else:
                return True

class Difference():

    def __init__(self, set1, set2):
        self.set1 = set1
        self.set2 = set2
        self.distance = {}
        self.x = {}
        self.y = {}
        self.z = {}
        self.compute_difference()

        self.boxplot_labels = Landmark.labels[:]
        for i, lbl in enumerate(self.boxplot_labels):
            if lbl == 'PosteriorInferiorVomerCorner':
                self.boxplot_labels[i] = 'PIVomerCorner'

    def compute_difference(self):
        for dataset_id in self.set1.data:
            if dataset_id not in self.set2.data:
                continue
            for lmk in self.set1.data[dataset_id]:
                if lmk not in self.set2.data[dataset_id]:
                    continue
                [x1, y1, z1] = self.set1.data[dataset_id][lmk]
                [x2, y2, z2] = self.set2.data[dataset_id][lmk]

                if lmk not in self.distance:
                    self.distance[lmk] = []
                    self.x[lmk] = []
                    self.y[lmk] = []
                    self.z[lmk] = []

                x = x1 - x2
                y = y1 - y2
                z = z1 - z2
                distance = math.sqrt(x*x+y*y+z*z)
                
                self.x[lmk].append(x)
                self.y[lmk].append(y)
                self.z[lmk].append(z)
                self.distance[lmk].append(distance)
    
    def pp(self):
        for dataset_id in sorted(self.set1.data.keys()):
            if dataset_id not in self.set2.data:
                continue

            print('---- Dataset: %s ----' % dataset_id)
            diff = ''
            for lmk in sorted(self.set1.data[dataset_id].keys()):
                if lmk not in self.set2.data[dataset_id]:
                    continue
                [x1, y1, z1] = self.set1.data[dataset_id][lmk]
                [x2, y2, z2] = self.set2.data[dataset_id][lmk]

                x = x1 - x2
                y = y1 - y2
                z = z1 - z2
                distance = math.sqrt(x*x+y*y+z*z)
                
                diff = ('%s:[%.2f, %.2f, %.2f, %.2f],  ' % 
                        (Landmark.get_code_by_label(lmk), x, y, z, distance))
                print(diff)


    def convert_to_list_of_lists(self, dic):
        data = []
        for label in Landmark.labels:
            if label in dic:
                data.append(dic[label])
            else:
                data.append([])
        return data
    
    def make_boxplot(self, title, data, labels):
        """Create box plot
        data -  a 'list' or 'list of lists'
            in case of a 'list of lists' there will be
            separete box plots within a figure for each sublits
        labels - a 'list' of labels
        title - a string of title
        There is a line passing through x = 0
        
        The function resuires 'plt.show()' after it has been called
        """    
        fig = plt.figure(figsize=(10, 6))
        fig.subplots_adjust(left=0.2)
        ax = fig.add_subplot(111)
        ax.boxplot(data, vert=0)
        ax.plot([0,0],[0,13], color='k')
        ax.set_title(title)
        ax.set_yticklabels(labels)

    def plot_x(self):
        data = self.convert_to_list_of_lists(self.x)
        self.make_boxplot('difference in x', data, self.boxplot_labels)
        plt.show()
    
    def plot_y(self):
        data = self.convert_to_list_of_lists(self.y)
        self.make_boxplot('difference in y', data, self.boxplot_labels)
        plt.show()

    def plot_z(self):
        data = self.convert_to_list_of_lists(self.z)
        self.make_boxplot('difference in z', data, self.boxplot_labels)
        plt.show()
        
    def plot_distance(self):
        data = self.convert_to_list_of_lists(self.distance)
        self.make_boxplot('difference in distance', data, self.boxplot_labels)
        plt.show()

def main():

    print('----main start----')
    
    exclude = LandmarksToExclude()
    path_to_existence_map = (
            '~/992/soft/matlab_to_python'
            '/matlab/trachea_carina.txt' )
    exclude.read_existence_file('TracheaCarina', path_to_existence_map )
    exclude.add_landmark_dataset_pair('1013_LOWER-1', '1013')
    # print(exclude.data)

    path_to_manual_datasets = (
        '~/992/test_data/static_data_landmarks' )
    manual = LandmarksDataset(path_to_manual_datasets, DatasetType.fcsv,
                              exclude)
    manual_all = LandmarksDataset(path_to_manual_datasets, DatasetType.fcsv)
    
    # print('Manual 1006 = ', manual.data['1006'])
    # print('M  all 1006 = ', manual_all.data['1006'])
    # print('1013 = ', manual.data['1013']) 

    path_to_detected = (
    '~/992/soft/matlab_to_python/'
    'matlab/lms_manual_split/testResults' )
    detected = LandmarksDataset(path_to_detected, DatasetType.individual)

    path_to_segmented = (
        '~/992/test_data/'
        'detect_with_mask/one_file_for_all_landmarks' )

    detected_segmented = LandmarksDataset(path_to_segmented, 
                                          DatasetType.combined)
    detected.write_one_fcsv('1074', '~/992/output/detected_to_fcsv')
    detected.write_all_fcsv('~/992/output/detected_to_fcsv/', 'lmk')
    # print( manual)
    # print(detected)
    # print(detected_segmented)

    # print ('detected datasets: ', detected.get_dataset_ids())
    # print ('segmented datasets', detected_segmented.get_dataset_ids())
    
    difference = Difference(manual, detected)
    # difference.plot_x()
    # difference.plot_y()
    # difference.plot_z()
    # difference.plot_distance()
    # difference.pp()

    # difference2 = Difference(manual, detected_segmented)
    # difference2.plot_x()
    # difference2.plot_y()
    # difference2.plot_z()
    # difference2.plot_distance()
    print('----main end----')


if __name__ == '__main__':
    main()
