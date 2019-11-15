# coding: utf8


from collections import namedtuple
import cv2
import numpy as np
import os

from common.logger import log_new, logg

ImageSet = namedtuple('ImageSet', ['correct', 'current', 'baseline', 'diff'])
"""
Container with visual comparison results

:param correct: correct/expected screenshot name obtained from scenario json parsing
:type correct: str
:param current: path to image in current set, None if image is missing
:type current: str | None
:param baseline: path to image in baseline set, None if image is missing
:type baseline: str | None
:param diff: path to corresponding diff b/w current and baseline, None if current image equal baseline image.
:type diff: str | None
"""


def _compare_pair(l_image_path, r_image_path, diff_dir, rgb_threshold, size_threshold, whitening_ratio):
    """
    Comparison of 2 images resulting diff image with non-diff areas whitening and diff areas markup
    4-channel image processing (rgba) to make code reusable in tiles
    
    :param l_image_path: path to first image for comparison
    :type l_image_path: str
    :param r_image_path: path to second image for comparison
    :type r_image_path: str
    :param diff_dir: path to output directory
    :type diff_dir: str
    :param rgb_threshold: value of color threshold in rgba units
    :type rgb_threshold: int
    :param size_threshold: value of size threshold in pixels
    :type size_threshold: int
    :param whitening_ratio: ratio of added white color in output diff (0..1)
    :type whitening_ratio: float
    :return diff_path: output diff image path
    :rtype diff_path: str | None
    """
    
    log_new('_compare_pair')
    logg('image1', l_image_path)
    logg('image2', r_image_path)
    
    #checking input parameters: filters threshold values
    rgb_threshold = np.clip(rgb_threshold, 0, 255)
    logg('rgb threshold', rgb_threshold)
    size_threshold = np.clip(size_threshold, 0, 50)
    logg('size threshold', size_threshold)

    def read_image(image_path):
        image = cv2.imread(image_path)
        channels_n = len(cv2.split(image))
        #conversion of 3-channel format to 4-channel format (cv2.COLOR_RGB2RGBA)
        if channels_n == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        return image
    
    #checking unexisting image case (path is None)
    if l_image_path is None or r_image_path is None:
        return None
    
    #reading png files from disk
    image1 = read_image(l_image_path)
    image2 = read_image(r_image_path)

    height1, width1 = image1.shape[:2]
    height2, width2 = image2.shape[:2]

    if (height1 != height2) or (width1 != width2):
        raise Exception(
            'Different dimensions of img1 ({}, {}) and img2 ({}, {})!!!'.format(height1, width1, height2, width2)
        )
        
    blue1, green1, red1, alpha1 = cv2.split(image1)

    blue2, green2, red2, alpha2 = cv2.split(image2)

    def channel_abs_rgb_th_diff(im1, im2):
        channel_diff = cv2.absdiff(im1, im2)
        ret, thresh = cv2.threshold(channel_diff, rgb_threshold, 255, cv2.THRESH_BINARY)
        return thresh

    def channel_inverse(im):
        ret, thresh = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV)
        return thresh

    def channel_noise_removal(img):
        if size_threshold > 1:
            kernel = np.ones((size_threshold, size_threshold), np.uint8)
            result = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel, iterations=1)
        else:
            result = img
        return result

    # obtaining abs difference image with color threshold filter to each channel
    diff_blue0 = channel_abs_rgb_th_diff(blue1, blue2)
    diff_green0 = channel_abs_rgb_th_diff(green1, green2)
    diff_red0 = channel_abs_rgb_th_diff(red1, red2)
    diff_alpha0 = channel_abs_rgb_th_diff(alpha1, alpha2)

    #application of size filter (noise removal) to each channel
    diff_blue = channel_noise_removal(diff_blue0)
    diff_green = channel_noise_removal(diff_green0)
    diff_red = channel_noise_removal(diff_red0)
    diff_alpha = channel_noise_removal(diff_alpha0)

    #calculation of diff count value (sum of rgba differences of all pixels)
    diff_bg = cv2.bitwise_or(diff_blue, diff_green)
    diff_gray = cv2.bitwise_or(diff_bg, diff_red)
    diff_gray_alpha = cv2.bitwise_or(diff_gray, diff_alpha)
    diff_count = cv2.countNonZero(diff_gray_alpha)
   
    def build_diff_image(diff_gray_alpha_image, base_image, white_ratio):
        # application of 0.3 white blending to non-diff areas
        # creating red markup of diff areas
        height, width = diff_gray_alpha_image.shape[:2]
        dtype = diff_gray_alpha_image.dtype
        mask1 = np.zeros((height, width, 1), np.uint8)
        mask1[:] = (0)
        diff_marker = cv2.merge((mask1, mask1, diff_gray_alpha_image, diff_gray_alpha_image))
        white = np.ones(diff_gray_alpha_image.shape, dtype=dtype) * 255
        whity = cv2.merge((white, white, white, white))
        base_image_with_white = cv2.addWeighted(base_image, 1 - white_ratio, whity, white_ratio, 0)
        diff_channel_inv = channel_inverse(diff_gray_alpha_image)
        anti_marker = cv2.merge((diff_channel_inv, diff_channel_inv, diff_channel_inv, diff_channel_inv))
        patterned_img_wh = cv2.bitwise_and(base_image_with_white, anti_marker)
        return cv2.bitwise_or(patterned_img_wh, diff_marker)

    def save_diff_image(l_path, r_path, count):
        # saving resulting diff png on disk
        if count == 0:
            return None
          
        image1_name = os.path.basename(l_path)
        image2_name = os.path.basename(r_path)
        assert image1_name == image2_name
        diff_name = image1_name.replace('.png', '_{}.png'.format(str(count)))
        diff_path = os.path.join(diff_dir, diff_name)
        diff_image = build_diff_image(diff_gray_alpha, image1, whitening_ratio)
        cv2.imwrite(diff_path, diff_image)
        
        logg('diff', diff_path)
        return diff_path

    return save_diff_image(l_image_path, r_image_path, diff_count)


def compare_images(process_list, diff_dir, rgb_threshold, size_threshold, config):
    """
    Image comparison: cycle through list of image pairs creating corresponding diffs
    
    :param process_list: list of image pairs (paths)
    :type process_list: [(list[str], list[str])]
    :param diff_dir: target diff directory
    :type diff_dir: str
    :param rgb_threshold: color filter threshold value in rgba units
    :type rgb_threshold: int
    :param size_threshold: size filter threshold value in pixels
    :type size_threshold: int
    :param config: configuration
    :type config: Config
    :return: namedtuple containing paths of initial images and created diff (l_image_path, r_image_path, diff_path)
    :rtype: list[ImageSet]
    """

    log_new('compare_images')
   
    assert isinstance(process_list, list)
    assert isinstance(diff_dir, str)

    return [
        ImageSet(
            correct_name,
            l_image_path,
            r_image_path,
            _compare_pair(l_image_path, r_image_path, diff_dir, rgb_threshold, size_threshold, config.WHITENING_RATIO)
        ) for correct_name, l_image_path, r_image_path in process_list
    ]




