import os
import pandas as pd
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torch.utils.data import sampler
import torch

# import torchvision.datasets as dset
import torchvision.transforms as T

# 图像大小：600*450
# 个数：10015
# 种类：7(0~6)

DATAPATH = os.environ['datapath']
NUM_VAL = 1000
NUM_TRAIN = 10015 - NUM_VAL

# CSV处理器
def getlabels(mode):
  if mode=='Train':
    df = pd.read_csv(DATAPATH + 'trainlabel.csv')
  else:
    df = pd.read_csv(DATAPATH + 'testlabel.csv')
  images = np.array(df['image'].values.tolist())
  labels = np.array(list(range(0, len(images))))
  label_dic = df.columns.values.tolist()[1:]
  val_ind = np.array([])
  weights = np.zeros(len(label_dic))

  for i in range(len(label_dic)):
    ind = df.index[df[df.columns[i+1]] == 1].tolist()
    weights[i] = len(ind)
    lab = label_dic[i]
    labels[ind] = i
    if i != len(label_dic)-1:
      val_ind = np.append(np.random.choice(ind, int(NUM_VAL*float(len(ind)/len(labels))), replace=False), val_ind)
    else:
      val_ind = np.append(np.random.choice(ind, NUM_VAL-len(val_ind), replace=False), val_ind)
  return label_dic, images, labels, val_ind, weights

# 自定义torchvisoin.dataset类
class ISIC18(Dataset):
  def __init__(self, root, train=True, transform=None):
    super(ISIC18, self).__init__()
    self.transform = transform
    self.train = train
    
    if self.train:
      self.data_folder = DATAPATH + 'Train/'
      self.classes, self.img_paths, self.labels, self.val_ind, self.weights = getlabels('Train')
    else:
      self.data_folder = DATAPATH + 'Test/'
      self.classes, self.img_paths, self.labels, self.val_ind, self.weights = getlabels('Test')

  def __getitem__(self, index):
    img_path = self.img_paths[int(index)]
    label = self.labels[int(index)]
    img = Image.open(self.data_folder + img_path + '.jpg')

    if self.transform is not None:
      img = self.transform(img)

    return img, label

  def __len__(self):
    return len(self.labels)

# 数据获取器
def getdata():

  print ("Collecting data ...")

  transform = T.Compose([
    T.Resize((224,224)),
    T.ToTensor(),
    T.Normalize(mean=(0.7635, 0.5461, 0.5705), std=(0.6332, 0.3557, 0.3974))
  ])

  isic18_train = ISIC18(DATAPATH, train=True, transform=transform)
  sample = isic18_train.__getitem__(0)[0][None, :, :, :]
  
  # 归一化的各类权重
  weights = 1/isic18_train.weights
  sumweights = np.sum(weights)
  weights /= sumweights
  weights = torch.from_numpy(weights).type(torch.float)
  
  #Train dataloader
  train_dataloader = DataLoader(isic18_train, batch_size=int(os.environ['batchsize']), sampler=sampler.SubsetRandomSampler(list(set(range(NUM_TRAIN+NUM_VAL)).difference(set(isic18_train.val_ind)))))
  
  isic18_val = ISIC18(DATAPATH, train=True, transform=transform)
  val_dataloader = DataLoader(isic18_val, batch_size=int(os.environ['batchsize']), sampler=sampler.SubsetRandomSampler(isic18_val.val_ind))

  isic18_test = ISIC18(DATAPATH, train=False, transform=transform)
  test_dataloader = DataLoader(isic18_test, batch_size=512)
  # test_dataloader = None

  print ("Collect data complete!\n")

  return (train_dataloader, val_dataloader, test_dataloader, sample, weights)

# 计算均值方差的功能函数，训练开始时跑一遍
def compute_pixels():
  transform = T.Compose([
    # T.Resize((224,224)),
    T.ToTensor(),
  ])
  isic18_train = ISIC18(DATAPATH, train=True, transform=transform)
  totalpixels = 0
  for i in range(isic18_train.__len__()):
    img = isic18_train.__getitem__(i)[0][None, :, :, :]
    print (img.size()[2:])
    shape = img.size()[2:]
    totalpixels += shape[0] * shape[1]
  print (totalpixels)

def compute_mean():
  transform = T.Compose([
    # T.Resize((224,224)),
    T.ToTensor(),
  ])
  isic18_train = ISIC18(DATAPATH, train=True, transform=transform)
  img0 = isic18_train.__getitem__(0)[0][None, :, :, :]
  mean = torch.sum(img0, dim=(2,3))/(17800019220)
  for i in range(1, isic18_train.__len__()):
    img = isic18_train.__getitem__(i)[0][None, :, :, :]
    mean += torch.sum(img, dim=(2,3))/(17800019220)
    print(i, ':', mean)
  print (mean.size(), mean)

def compute_var():
  mean = torch.tensor([0.7635, 0.5461, 0.5705])
  transform = T.Compose([
    # T.Resize((224,224)),
    T.ToTensor(),
  ])
  isic18_train = ISIC18(DATAPATH, train=True, transform=transform)
  img0 = isic18_train.__getitem__(0)[0][None, :, :, :]
  img = img0 - mean[None, :, None, None]
  img = img * img
  totalvar = torch.sum(img * img, dim=(2,3))/(450*600*isic18_train.__len__())
  # totalvar = torch.sum(img * img, dim=(2,3))/(17800019220)
  for i in range(1, isic18_train.__len__()):
    img = isic18_train.__getitem__(i)[0][None, :, :, :]
    img = img * img
    totalvar += torch.sum(img * img, dim=(2,3))/(450*600*isic18_train.__len__())
    # totalvar += torch.sum(img * img, dim=(2,3))/(17800019220)
    print (i, ':', totalvar)
  print (totalvar.size(), totalvar)

# 不进行resize，直接计算的norm参数
# mean = [0.7635, 0.5461, 0.5705]
# var = [0.4009, 0.1265, 0.1579]
# std = [0.6332, 0.3557, 0.3974]

# compute_var()

# 19
# mean = [0.6678, 0.5298, 0.5244]
# var = [0.2527, 0.1408, 0.1364]

# 19 2
# mean = [0.6238, 0.5201, 0.5039]
# var = [0.2527, 0.1408, 0.1364]