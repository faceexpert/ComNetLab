# import this file

import face_operation as fo

#def get_attributes(path):
#    return fo.get_attribute(path)

def get_score_for_male(path):
    return fo.score_for_male(path)

def get_score_for_female(path):
    return fo.score_for_female(path)

# These two functions return [a, b], where a is the expected value, and b is the gender
# a = -1 if no person in photo
# a = -2 if >=2 persons in photo
# b = 1 if gender is the same as required
# b = 0 if gender is wrong

#get_score_for_male('/home/chao/testdata/1.jpg')
#get_score_for_female('/home/chao/testdata/1.jpg')
#get_score_for_male('/home/chnlich/testdata/2.jpg')
#get_score_for_female('/home/chnlich/testdata/2.jpg')
#get_score_for_male('/home/chnlich/testdata/3.jpg')
#get_score_for_female('/home/chnlich/testdata/3.jpg')
#get_score_for_male('/home/chnlich/testdata/4.JPEG')
#get_score_for_female('/home/chnlich/testdata/4.JPEG')
#get_score_for_male('/home/chnlich/testdata/5.jpg')
#get_score_for_female('/home/chnlich/testdata/5.jpg')

