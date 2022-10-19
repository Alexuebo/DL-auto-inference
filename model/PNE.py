from torch.utils.data import Dataset


class PNEDataset(Dataset):
    def __init__(self, imgs, transform=None, target_transform=None):
        self.imgs = imgs
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, index):
        img_x = self.imgs[index]
        # img_x = img_x.convert('RGB')
        if self.transform is not None:
            img_x = self.transform(img_x)
        return img_x

    def __len__(self):
        return len(self.imgs)

if __name__ == '__main__':
    import torch
    print(torch.__version__)
    print(torch.cuda.is_available())
