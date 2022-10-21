import os

import SimpleITK
import numpy as np
import pydicom

import utils.tools as utils


def is_dicom_file(filename):
    '''
       判断某文件是否是dicom格式的文件
    :param filename: dicom文件的路径
    :return:
    '''
    file_stream = open(filename, 'rb')
    file_stream.seek(128)
    data = file_stream.read(4)
    file_stream.close()
    if data == b'DICM':
        return True
    return False


def load_patient(src_dir):
    '''
        读取某文件夹内的所有dicom文件
        :param src_dir: dicom文件夹路径
        :return: dicom list
    '''
    files = os.listdir(src_dir)
    slices = []
    for s in files:
        file = src_dir + '/' + s
        if is_dicom_file(file):
            instance = pydicom.read_file(file)
            slices.append(instance)

    slices.sort(key=lambda x: int(x.InstanceNumber))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness
    return slices


def getdir_ps_thick(dicom_path):
    '''
    读取文件夹内dicom的 像素间距ps 层厚thick
    :param dicom_path:
    :return:
    '''
    first = os.listdir(dicom_path)[0]
    return getps_thick(os.path.join(dicom_path, first))


def getps_thick(dicom_file_path):
    '''
    读取单个dicom的ps
    :param dicom_file_path:
    :return:
    '''
    instance = pydicom.read_file(dicom_file_path)  # SimpleITK的GetPixel()有问题 所以用pydicom得到ps
    return instance.PixelSpacing, instance.SliceThickness


def read_dcm(dicom_file_path):
    '''
    读取单个dicom文件
    :param dicom_file_path:
    :return:
    '''
    image = SimpleITK.ReadImage(dicom_file_path)  # 还是用SimpleITK读
    image_array = np.squeeze(SimpleITK.GetArrayFromImage(image))
    image_array[image_array == -2000] = 0
    return image_array


def read_dcms_dir(dicom_dir):
    '''
    读取某文件夹内的所有dicom文件,并提取像素值(-4000 ~ 4000)
    :param src_dir: dicom文件夹路径
    :return: image array
    '''
    reader = SimpleITK.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    img_array = SimpleITK.GetArrayFromImage(image)
    img_array[img_array == -2000] = 0
    return img_array


def set_dcm_width_center(img_array, center, width):
    '''
    设置dcm array的窗口窗位
    :param img_array: 需要dcm array对象
    :param window_type:
    :return: array对象
    '''
    minWindow = float(center) - 0.5 * float(width)
    newimg = (img_array - minWindow) / float(width)
    newimg[newimg < 0] = 0
    newimg[newimg > 1] = 1
    newimg = (newimg * 255).astype('uint8')  # 归一化到0~255
    return newimg


#
# # 单个dcm数据处理, 用不上了
# def dcmprocess(dicom, window_type):
#     ps = getps(dicom)
#     image = read_dcm(dicom)
#     imglist = afterprocess(image, window_type)
#     return imglist, ps


# 一整个dcm文件夹处理
def dcmdirprocess(dicom_dir, window_type):
    pt = getdir_ps_thick(dicom_dir)
    image = read_dcms_dir(dicom_dir)
    imglist = afterprocess(image, window_type)
    return imglist, pt


# 统一调整窗宽窗位,各种后处理
def afterprocess(image, window_type):
    w, c = utils.get_CT_width_center(window_type)
    s = set_dcm_width_center(image, w, c)
    imglist = utils.Contrast_and_Brightness(1.1, 10, s)
    return imglist


# if __name__ == '__main__':
#     a = dcmdirprocess("F:\\MedData\\pneumothorax\\data\\111", "CT气胸")
#     # print(a)
#     print(a[1][0])
#     print(a[1][1])