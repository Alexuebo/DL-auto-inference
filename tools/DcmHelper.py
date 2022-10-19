import os

import SimpleITK
import numpy as np

import pydicom
import tools.Utils as utils


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


def getps(dicom_path):
    first = os.listdir(dicom_path)[0]
    instance = pydicom.read_file(os.path.join(dicom_path, first))
    PixelSpacing = instance.PixelSpacing
    return PixelSpacing


def get_pixels_hu_by_simpleitk(dicom_dir):
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


def setDicomWinWidthWinCenter(img_data, window_type):
    img_temp = img_data.copy()
    rows = len(img_temp)
    cols = len(img_temp[0])
    center, width = utils.get_window_size(window_type)
    img_temp.flags.writeable = True
    min = (2 * center - width) / 2.0 + 0.5
    max = (2 * center + width) / 2.0 + 0.5
    dFactor = 255.0 / (max - min)
    for i in np.arange(rows):
        for j in np.arange(cols):
            img_temp[i, j] = int((img_temp[i, j] - min) * dFactor)

    min_index = img_temp < 0
    img_temp[min_index] = 0
    max_index = img_temp > 255
    img_temp[max_index] = 255

    return img_temp


# dcm数据处理
def dcmprocess(dicom_dir):
    imglist = []
    window_type = 'abdomen'
    ps = getps(dicom_dir)
    image = get_pixels_hu_by_simpleitk(dicom_dir)
    # print(image.shape[0])
    for i in range(image.shape[0]):
        s = setDicomWinWidthWinCenter(image[i], window_type)
        ndary = utils.Contrast_and_Brightness(1.1, 10, s)
        result = utils.CV2PIL(ndary)
        result = result.convert("RGB")
        imglist.append(result)
    return imglist, ps
