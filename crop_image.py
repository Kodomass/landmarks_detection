import os
import sys
import nrrd
import numpy as np

class CropImage():

    def __init__(self, path_to_image):
    
        if not os.path.exists(path_to_image):
            print("Incorrect image path: '%s' " %  path_to_image)
            sys.exit(1)

        self.path = path_to_image
        [self.data, self.head] = nrrd.read(path_to_image)

        self.size1 = int(self.head['sizes'][0])
        self.size2 = int(self.head['sizes'][1])
        self.size3 = int(self.head['sizes'][2])

        self.origin1 = float(self.head['space origin'][0])
        self.origin2 = float(self.head['space origin'][1])
        self.origin3 = float(self.head['space origin'][2])

        self.spacing1 = float(self.head['space directions'][0][0])
        self.spacing2 = float(self.head['space directions'][1][1])
        self.spacing3 = float(self.head['space directions'][2][2])

    def write(self, path_to_output_image):
        nrrd.write(path_to_output_image, self.data, self.head)
        print('write: %s' % path_to_output_image)
    
    def crop(self, dims):
        [dim1, dim2, dim3] = dims
        
        if dim1:
            from1 = dim1[0]
            to1   = dim1[1]
            if to1 == 'max':
                to1 = self.size1
        else:
            from1 = 0
            to1   = self.size1

        if dim2:
            from2 = dim2[0]
            to2   = dim2[1]
            if to2 == 'max':
                to2 = self.size2
        else:
            from2 = 0
            to2   = self.size2

        if dim3:
            from3 = dim3[0]
            to3   = dim3[1]
            if to3 == 'max':
                to3 = self.size3
        else:
            from3 = 0
            to3   = self.size3
        
        new_size1 = to1 - from1
        new_size2 = to2 - from2
        new_size3 = to3 - from3

        new_origin1 = self.origin1 + from1 * self.spacing1
        new_origin2 = self.origin2 + from2 * self.spacing2
        new_origin3 = self.origin3 + from3 * self.spacing3

        self.data = self.data[ from1:to1, from2:to2, from3:to3 ] 
        self.head['sizes'][0] = new_size1
        self.head['sizes'][1] = new_size2
        self.head['sizes'][2] = new_size3

        self.head['space origin'][0] = new_origin1
        self.head['space origin'][1] = new_origin2
        self.head['space origin'][2] = new_origin3

        print('Crop from [0:%d, 0:%d, 0:%d] to [%d:%d, %d:%d, %d:%d]' %
                (self.size1, self.size2, self.size3, 
                   from1, to1, from2, to2, from3, to3) )
        print('Size changed from [%d, %d, %d] to [%d, %d, %d]' %
                (self.size1, self.size2, self.size3,
                   new_size1, new_size2, new_size3) )
        
        print('Origin changes from [%f, %f, %f] to [%f, %f, %f]' %
                (self.origin1, self.origin2, self.origin3,
                    new_origin1, new_origin2, new_origin3) )

def main():
    
    path = '~/992/test_data/nrrd_sample/1074_INPUT.nrrd'
    out_path = '~/992/output/croped_images/1074_cropped.nrrd'
    out_path2 = '~/992/output/croped_images/1074_cropped_2.nrrd'
    
    # data, head = nrrd.read(path)
    # crop_data = data[:,:,]
    # head['sizes'][2] = 380
    # nrrd.write(out_path, crop_data, head)

    ci = CropImage(path)
    ci.crop([[],[],[80,'max']])
    ci.write(out_path2)

if __name__ == "__main__":
    main()
