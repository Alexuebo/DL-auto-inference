from torch.utils.data import Dataset
import numpy as np

class PNEDataset(Dataset):
    def __init__(self, imgs, transform=None, target_transform=None):
        self.imgs = imgs
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, index):
        img_x = self.imgs[index]
        # img_x = img_x.convert('RGB') # 转三通道
        image = np.expand_dims(img_x, axis=2)
        image = np.concatenate((image, image, image), axis=-1)
        if self.transform is not None:
            image = self.transform(image)
        return image

    def __len__(self):
        return len(self.imgs)
