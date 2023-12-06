import cv2
import pickle
import numpy as np
import matplotlib.pyplot as plt


# --------------------------------------------------------------------

# load mean eyes
with open('../data/eyes3d.pkl', 'rb') as f:
    eyes_info = pickle.load(f)
idxs481 = eyes_info['mask481']['idxs']
tri481 = eyes_info['mask481']['trilist']
iris_idx_481 = eyes_info['mask481']['idxs_iris']
eyel_template = eyes_info['left_points'][idxs481]
eyer_template = eyes_info['right_points'][idxs481]
eyel_template_homo = np.append(eyel_template, np.ones((eyel_template.shape[0],1)), axis=1)
eyer_template_homo = np.append(eyer_template, np.ones((eyer_template.shape[0],1)), axis=1)


# --------------------------------------------------------------------

idxs_ring0 = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
idxs_ring1 = [240, 112, 80, 48, 16, 304, 336, 368, 442, 480, 426, 352, 320, 288, 0, 32, 64, 96, 224]
idxs_ring2 = [248, 120, 88, 56, 24, 312, 344, 376, 433, 480, 421, 360, 328, 296, 8, 40, 72, 104, 232]
idxs_ring_iris = [224, 226, 228, 230, 232, 234, 236, 238, 240, 242, 244, 246, 248, 250, 252, 254]

def draw_eyes(image, lms68_3D, eyes, colour=[178, 255, 102]):
    '''
    Input args:
        image: cv2 image
        lms68_3D: face lms68
        eyes: dictionary including left and right eyes as np arrays
        colour: colour to use for drawing the eyes
    '''

    colour_iris = colour
    colour_eyeball = colour
    colour_rings = colour

    # face diag
    lms5 = lms68_3D[[36, 45, 30, 48, 54]]
    lms5[0] = lms68_3D[36:42].mean(axis=0)
    lms5[1] = lms68_3D[42:48].mean(axis=0)
    diag1 = np.linalg.norm(lms5[0] - lms5[4])
    diag2 = np.linalg.norm(lms5[1] - lms5[3])
    diag = np.max([diag1, diag2])
    thickness_iris = max(int(diag / 50), 1)
    thickness_eyeball = max(int(diag / 50), 1)
    thickness_rings = max(int(diag / 80), 1)
    
    # draw eyeballs
    for side, eye in eyes.items():
        eye = eye[:, [1, 0]]
        ring1 = eye[idxs_ring1][:, :2]
        ring2 = eye[idxs_ring2][:, :2]
        range1 = ring1[:, 1].max() - ring1[:, 1].min()
        range2 = ring2[:, 0].max() - ring2[:, 0].min()
        radius = int(range1/4 + range2/4)
        cnt = eye[:32].mean(axis=0)
        image = cv2.circle(
            image, tuple(cnt[:2].astype(np.int32).tolist()), radius, colour_eyeball, thickness_eyeball)
    # draw rings
    for side, eye in eyes.items():
        eye = eye[:, [1, 0]]
        iris8 = eye[idxs_ring1][:, :2]
        for i_idx in range(iris8.shape[0]-1):
            pt1 = tuple(iris8[i_idx].astype(np.int32).tolist())
            pt2 = tuple(iris8[i_idx + 1].astype(np.int32).tolist())
            image = cv2.line(image, pt1, pt2, colour_rings, thickness_rings)
    for side, eye in eyes.items():
        eye = eye[:, [1, 0]]
        iris8 = eye[idxs_ring2][:, :2]
        for i_idx in range(iris8.shape[0]-1):
            pt1 = tuple(iris8[i_idx].astype(np.int32).tolist())
            pt2 = tuple(iris8[i_idx + 1].astype(np.int32).tolist())
            image = cv2.line(image, pt1, pt2, colour_rings, thickness_rings)
    # draw irises
    for side, eye in eyes.items():
        eye = eye[:, [1, 0]]
        iris8 = eye[idxs_ring_iris][:, :2]
        for i_idx in range(iris8.shape[0]):
            pt1 = tuple(iris8[i_idx].astype(np.int32).tolist())
            pt2 = tuple(iris8[(i_idx + 1) % 16].astype(np.int32).tolist())
            image = cv2.line(image, pt1, pt2, colour_iris, thickness_iris) 
    return image


def draw_gaze_from_vector(image, lms68_3D, vector, colour=[255, 0, 0]):
    '''
    Input args:
        image: cv2 image
        lms68_3D: face lms68
        vector: gaze vector
        colour: colour of the gaze vector
    '''
    # face diag
    lms5 = lms68_3D[[36, 45, 30, 48, 54]][:, [0, 1]]
    lms5[0] = lms68_3D[36:42].mean(axis=0)[[0, 1]]
    lms5[1] = lms68_3D[42:48].mean(axis=0)[[0, 1]]
    diag1 = np.linalg.norm(lms5[0] - lms5[4])
    diag2 = np.linalg.norm(lms5[1] - lms5[3])
    diag = np.max([diag1, diag2])
    # norm weights
    vector_norm = 1.3 * diag
    thickness = int(diag / 10)
    
    # gaze vector eye in image space
    cnt = lms68_3D[30, [1, 0]].astype(np.int32)
    vector_norm = int(np.array(image.shape[1])/4.)
    g_vector = vector[[1, 0]] * np.array([-1., -1.]) * vector_norm
    start_point = cnt[[1, 0]]
    g_point = start_point + g_vector
    # draw gaze vectors
    pt1 = start_point.astype(np.int32)[[1, 0]]
    pt2 = g_point.astype(np.int32)[[1, 0]]
    image = cv2.arrowedLine(image, pt1, pt2, colour, thickness, tipLength=0.2)
    return image