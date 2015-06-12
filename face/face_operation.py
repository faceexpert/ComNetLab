
# Do not import this file directly, import face_interface instead

from facepp import API, File
from pprint import pformat
import numpy as np

API_KEY = 'a886c2c73eb9d594297c492b064aa912'
API_SECRET = 'YmagXkR2-zSp-FQmnlZSycUp_V9yPk30'

EYE_WEIGHT = 150
EYE_MAX = 100

MOUTH_WEIGHT_1 = 10
MOUTH_1_MAX = 25
MOUTH_WEIGHT_2 = 10
MOUTH_2_MAX = 25

EYEBROW_MAX = 100
EYEBROW_WEIGHT = 10

CHIN_THRESHOLD = 70
CHIN_WEIGHT = 2
CHIN_MAX = 100

FACE_THRESHOLD = 70
FACE_WEIGHT = 5
FACE_MAX = 100

NOSE_THRESHOLD = 60
NOSE_WEIGHT = 4
NOSE_MAX = 100


def print_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj

    print hint
    result = encode(result)
    print '\n'.join(['  ' + i for i in pformat(result, width=75).split('\n')])


api = API(API_KEY, API_SECRET)

# change here
# IMAGE_DIR = '/home/chnlich/workspace/ComNetLab/face/'

def call_detect(path):
    return api.detection.detect(img=File(path))


def call_landmark(id):
    return api.detection.landmark(face_id=id)


def distance(a, b):
    def sqr(x):
        return x * x

    return sqr(a[u'x'] - b[u'x']) + sqr(a[u'y'] - b[u'y'])


def fix_value(x, limit):
    if x > limit:
        return limit
    if x < -limit:
        return -limit
    return x


def check_female_eye(attr, land):
    tar = land[u'result'][0][u'landmark']
    left_center = tar[u'left_eye_center']
    left_left = tar[u'left_eye_left_corner']
    right_center = tar[u'right_eye_center']
    right_right = tar[u'right_eye_right_corner']

    def get_value(dx, dy):
        if dx == 0:
            return 0
        return dy / dx

    lvalue = get_value(abs(left_center[u'x'] - left_left[u'x']), left_center[u'y'] - left_left[u'y'])
    rvalue = get_value(abs(right_center[u'x'] - right_right[u'x']), right_center[u'y'] - right_right[u'y'])
    final_value = (lvalue + rvalue) * EYE_WEIGHT
    return fix_value(final_value, EYE_MAX)


def check_female_mouth(attr, land):
    smile_value = attr[u'face'][0][u'attribute'][u'smiling'][u'value']
    tar = land[u'result'][0][u'landmark']
    # mouth 1
    left_mouth_point = tar[u'mouth_upper_lip_left_contour1']
    right_mouth_point = tar[u'mouth_upper_lip_right_contour1']
    left_nose_point = tar[u'nose_left']
    right_nose_point = tar[u'nose_right']

    value1 = abs(distance(left_nose_point, right_nose_point) / distance(left_mouth_point,
                                                                        right_mouth_point) - 1) * MOUTH_WEIGHT_1
    value1 = fix_value(value1, MOUTH_1_MAX)
    # mouth 2
    left_mouth_point = tar[u'mouth_left_corner']
    right_mouth_point = tar[u'mouth_right_corner']
    up_mouth_point = tar[u'mouth_upper_lip_top']
    down_mouth_point = tar[u'mouth_lower_lip_bottom']

    value2 = (3 * distance(up_mouth_point, down_mouth_point) / distance(left_mouth_point,
                                                                        right_mouth_point) - 1) * MOUTH_WEIGHT_2
    value2 = fix_value(value2, MOUTH_2_MAX)
    return smile_value / 2 + value1 + value2


def check_female_eyebrow(attr, land):
    tar = land[u'result'][0][u'landmark']
    left_point = tar[u'left_eyebrow_left_corner']
    right_point = tar[u'left_eyebrow_right_corner']
    left_eye = tar[u'left_eye_left_corner']
    right_eye = tar[u'left_eye_right_corner']
    value = fix_value(
        (distance(left_point, right_point) / distance(left_eye, right_eye) - 1) * EYEBROW_WEIGHT, EYEBROW_MAX / 2.0)

    left_point = tar[u'right_eyebrow_left_corner']
    right_point = tar[u'right_eyebrow_right_corner']
    left_eye = tar[u'right_eye_left_corner']
    right_eye = tar[u'right_eye_right_corner']
    value += fix_value(
        (distance(left_point, right_point) / distance(left_eye, right_eye) - 1) * EYEBROW_WEIGHT, EYEBROW_MAX / 2.0)
    return value


def get_angle(x, y):
    lx = np.sqrt(x.dot(x))
    ly = np.sqrt(y.dot(y))
    if lx == 0 or ly == 0:
        return 0
    cos_angle = x.dot(y) / np.sqrt(x.dot(x) * y.dot(y))
    return np.arccos(cos_angle) * 180 / np.pi


def check_female_chin(attr, land):
    tar = land[u'result'][0][u'landmark']
    left_point = tar[u'contour_left9']
    right_point = tar[u'contour_right9']
    middle_point = tar[u'contour_chin']

    x = np.array([left_point[u'x'] - middle_point[u'x'], right_point[u'x'] - middle_point[u'x']])
    y = np.array([left_point[u'y'] - middle_point[u'y'], right_point[u'y'] - middle_point[u'y']])
    value = (get_angle(x, y) - CHIN_THRESHOLD) * CHIN_WEIGHT
    #print 'chin: ', get_angle(x,y), ' ',CHIN_THRESHOLD, ' ',CHIN_WEIGHT
    return fix_value(value, CHIN_MAX)


def check_female_face(attr, land):
    tar = land[u'result'][0][u'landmark']
    left_point = tar[u'contour_left1']
    right_point = tar[u'contour_right1']
    dy = right_point[u'y'] - left_point[u'y']
    dx = right_point[u'x'] - left_point[u'x']
    if dx == 0:
        return 0
    value = (90 - FACE_THRESHOLD - np.tan(abs(dy / dx)) * 180 / np.pi) * FACE_WEIGHT
    #print 'face: ', np.tan(dy/dx)*180/np.pi, FACE_WEIGHT
    value = fix_value(value, FACE_MAX)
    return value


def score_for_female(path):
    attr = call_detect(path)
    n = len(attr[u'face'])
    if n == 0:
        return [-1, 0]
    if n >= 2:
        return [-2, 0]
    #print attr
    land = call_landmark(attr[u'face'][0][u'face_id'])
    #print land
    eye_value = check_female_eye(attr, land)
    mouth_value = check_female_mouth(attr, land)
    eyebrow_value = check_female_eyebrow(attr, land)
    chin_value = check_female_chin(attr, land)
    face_value = check_female_face(attr, land)
    print 'eye_value = ', eye_value, ' mouth_value = ', mouth_value, ' eyebrow_value = ', eyebrow_value, \
        ' chin_value = ', chin_value, ' face_value = ', face_value
    total_value = ((eye_value + mouth_value + eyebrow_value + chin_value + face_value) / 5 + 100) / 2
    print 'total_value = ', total_value
    gender = attr[u'face'][0]['attribute']['gender']
    isfemale = gender['value'] == u'Female'
    if (gender['confidence'] < 90):
        isfemale = 1
    print isfemale
    return [total_value, isfemale]


def check_male_mouth(attr, land):
    return check_female_mouth(attr, land)


def check_male_eyebrow(attr, land):
    tar = land[u'result'][0][u'landmark']
    up_eye = tar[u'left_eye_top']
    down_eye = tar[u'left_eye_bottom']
    up_eyebrow = tar[u'left_eyebrow_upper_middle']
    down_eyebrow = tar[u'left_eyebrow_lower_middle']
    value = fix_value(
        (2 * distance(up_eyebrow, down_eyebrow) / distance(up_eye, down_eye) - 1) * EYEBROW_WEIGHT, EYEBROW_MAX / 2.0)

    #print 'eyebrow left: ', 2 * distance(up_eyebrow, down_eyebrow) / distance(up_eye, down_eye), ' ',value

    up_eye = tar[u'right_eye_top']
    down_eye = tar[u'right_eye_bottom']
    up_eyebrow = tar[u'right_eyebrow_upper_middle']
    down_eyebrow = tar[u'right_eyebrow_lower_middle']
    value += fix_value(
        (2 * distance(up_eyebrow, down_eyebrow) / distance(up_eye, down_eye) - 1) * EYEBROW_WEIGHT, EYEBROW_MAX / 2.0)
    #print 'eyebrow right: ', 2 * distance(up_eyebrow, down_eyebrow) / distance(up_eye, down_eye)

    return value


def check_male_nose(attr, land):
    tar = land[u'result'][0][u'landmark']
    left_up = tar[u'nose_contour_left1']
    left_down = tar[u'nose_contour_left3']
    right_up = tar[u'nose_contour_right1']
    right_down = tar[u'nose_contour_right3']
    x = np.array([left_down[u'x'] - left_up[u'x'], right_down[u'x'] - right_up[u'x']])
    y = np.array([left_down[u'y'] - left_up[u'y'], right_down[u'y'] - right_up[u'y']])
    #print 'nose: ', get_angle(x,y), ' ',NOSE_WEIGHT, ' ',NOSE_MAX,' ',(90 - get_angle(x, y) - NOSE_THRESHOLD)
    value = fix_value((90 - get_angle(x, y) - NOSE_THRESHOLD) * NOSE_WEIGHT, NOSE_MAX)
    return value


def score_for_male(path):
    attr = call_detect(path)
    n = len(attr[u'face'])
    if n == 0:
        return [-1, 0]
    if n >= 2:
        return [-2, 0]
    #print attr
    land = call_landmark(attr[u'face'][0][u'face_id'])
    #print land
    mouth_value = check_male_mouth(attr, land)
    eyebrow_value = check_male_eyebrow(attr, land)
    nose_value = check_male_nose(attr, land)
    print 'mouth_value = ', mouth_value, ' eyebrow_value = ', eyebrow_value, ' nose_value = ', nose_value
    total_value = ((mouth_value + eyebrow_value + nose_value) / 3 + 100) / 2
    print 'total_value = ', total_value
    gender = attr[u'face'][0]['attribute']['gender']
    ismale = gender['value'] == u'Male'
    if (gender['confidence'] < 90):
        ismale = 1
    print ismale
    return [total_value, ismale]
