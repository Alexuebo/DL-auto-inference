import cv2
import nibabel as nib
import numpy as np

import utils.tools as utils


def setNiiWidthAndCenter(img_data, window_type):
    center, width = utils.get_CT_width_center(window_type)
    minWindow = center - 0.5 * width
    newimg = (img_data - minWindow) / width
    newimg[newimg < 0] = 0
    newimg[newimg > 1] = 1
    newimg = (newimg * 255).astype('uint8')  # 归一化到0~255
    return newimg


def readnii(niifile):
    img_obj = nib.load(niifile)
    idata = img_obj.get_fdata()
    return idata


# nii.gz数据处理,一个即为一病人
def niiprocess(img_file, window_type):
    img_obj = nib.load(img_file)
    idata = img_obj.get_fdata()
    img = setNiiWidthAndCenter(idata, window_type)
    ndarry = utils.Contrast_and_Brightness(1.1, 10, img)
    pixdim = img_obj.header['pixdim']
    x, y, z = pixdim[2], pixdim[3], pixdim[1]
    # ps = xy z =thick
    ps = [[x, y], z]
    return ndarry, ps
    # niilist = []
    # for nii in img_file:
    #     ng = pydicom.read_file(nii)
    #     niilist.append(ng)
    # return niilist


def mask_to_onehot(masks, palette):
    """
    (N, H, W)->(K, N, H, W)
    mask:病人mask
    palette:[[0],[1],[2]] 几分类图
    """
    semantic_map = []
    m = np.expand_dims(masks, axis=0)  # (N,H,M) ->(1,N,H,M)
    for colour in palette:
        equality = np.equal(m, colour)
        class_map = np.all(equality, axis=0)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=0).astype(np.float32)
    return semantic_map


def onehot_to_mask(mask, palette):
    """
    Converts a mask (K, N, H, W) to (N, H, W)
    """
    x = np.argmax(mask, axis=-1)
    colour_codes = np.array(palette)
    x = np.uint8(colour_codes[x.astype(np.uint8)])
    return x


if __name__ == '__main__':
    array = np.reshape(list(np.random.random(240)), (20, 3, 4))

    for i in range(array.shape[0]):
        print(array[i, :, :])

    for j in range(array.shape[1]):
        print(array[:, j, :])

    for k in range(array.shape[2]):
        print(array[:, :, k])
