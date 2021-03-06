import cv2
import numpy as np
import random


def dilate_mask(src_label_np, radius):
    """
    This function implements the dilation for mask
    :param src_label_np:
    :param radius:
    :return:
    """
    dilation_diameter = int(2 * radius + 1)
    kernel = np.zeros((dilation_diameter, dilation_diameter), np.uint8)

    for row_idx in range(dilation_diameter):
        for column_idx in range(dilation_diameter):
            if np.linalg.norm(np.array([row_idx, column_idx]) - np.array(
                    [radius, radius])) <= radius:
                kernel[row_idx, column_idx] = 1

    dst_label_np = cv2.dilate(src_label_np, kernel, iterations=1)

    assert dst_label_np.shape == src_label_np.shape

    return dst_label_np


def erode_mask(src_label_np, radius):
    """
    This function implements the dilation for mask
    :param src_label_np:
    :param radius:
    :return:
    """
    erode_diameter = int(2 * radius + 1)
    kernel = np.zeros((erode_diameter, erode_diameter), np.uint8)

    for row_idx in range(erode_diameter):
        for column_idx in range(erode_diameter):
            if np.linalg.norm(np.array([row_idx, column_idx]) - np.array(
                    [radius, radius])) <= radius:
                kernel[row_idx, column_idx] = 1

    dst_label_np = cv2.erode(src_label_np, kernel, iterations=1)

    assert dst_label_np.shape == src_label_np.shape

    return dst_label_np


def foreground_move(src_label_np, max_distance):
    assert max_distance >= 0

    height, width = src_label_np.shape

    padded_label_np = np.pad(src_label_np, ((max_distance, max_distance), (max_distance, max_distance)), 'constant',
                             constant_values=0)

    r = np.random.randint(0, 2 * max_distance)
    c = np.random.randint(0, 2 * max_distance)

    dst_label_np = padded_label_np[r:r + height, c:c + width]

    assert src_label_np.shape == dst_label_np.shape

    return dst_label_np


def gaussian_noise(src_label_np, max_radius):
    assert max_radius >= 0

    height, width = src_label_np.shape
    edges = cv2.Canny(src_label_np, threshold1=64, threshold2=200)

    random_matrix = np.random.rand(height, width)
    random_matrix[random_matrix <= 0.5] = 0
    random_matrix[random_matrix > 0.5] = 1
    chosen_edges = edges * random_matrix
    choose_index = np.where(chosen_edges > 0)  # tuple with length 2 row and column

    dst_label_np = src_label_np
    for index in range(len(choose_index[0])):
        row = choose_index[0][index]
        column = choose_index[1][index]
        center_coordinates = (column, row)
        radius = np.random.randint(max_radius, size=1)
        coin = np.random.randint(2, size=1)
        if coin == 1:
            dst_label_np = cv2.circle(dst_label_np, center_coordinates, radius, thickness=-1, color=255)
        else:
            dst_label_np = cv2.circle(dst_label_np, center_coordinates, radius, thickness=-1, color=0)
    return dst_label_np


# debug only
# img=cv2.imread('/data1/minqing/data/JRST/noisy-data-alpha-0.1-beta1-10-beta2-15/all/training/clavicle/JPCLN001.png',0)
# dst=gaussian_noise(src_label_np=img, max_radius=2, move_ratio=0.25)
# cv2.imshow('image',dst)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


def add_noise(src_label_np, min_radius, max_radius):
    assert len(src_label_np.shape) == 2
    assert 0 <= max_radius <= max_radius

    random_num = random.random()
    radius = random.randint(min_radius, max_radius)

    if random_num < 0.33:
        dst_label_np = dilate_mask(src_label_np, radius)
        noise_type = 'dilate'
    elif random_num < 0.66:
        dst_label_np = erode_mask(src_label_np, radius)
        noise_type = 'erode'
    else:
        dst_label_np = gaussian_noise(src_label_np, max_radius)
        noise_type = 'gaussian noise'

    return dst_label_np, noise_type
