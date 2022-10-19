import tools.Utils as utils


def test():
    print(10.54)


def setNiiWidthAndCenter(img_data, window_type):
    img_temp = img_data.copy()
    center, width = utils.get_window_size(window_type)
    val_min = center - (width / 2)
    val_max = center + (width / 2)
    img_temp[img_data < val_min] = val_min
    img_temp[img_data > val_max] = val_max
    return img_temp


# nii.gz数据处理
def niiprocess(img_file):
    # 一个即为一病人
    window_type = 'abdomen'
    import nibabel as nib
    img_obj = nib.load(img_file)
    img = img_obj.get_fdata()
    patient = []
    for i in img:
        s = setNiiWidthAndCenter(i, window_type)
        ndary = utils.Contrast_and_Brightness(1.1, 10, s)
        result = utils.CV2PIL(ndary)
        result = result.convert("RGB")
        patient.append(result)

    pixdim = img_obj.header['pixdim']
    x, y, z = pixdim[2], pixdim[3], pixdim[1]
    ps = [x, y, z]
    return patient, ps
    # niilist = []
    # for nii in img_file:
    #     ng = pydicom.read_file(nii)
    #     niilist.append(ng)
    # return niilist
