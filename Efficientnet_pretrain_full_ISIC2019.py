# Global environment setup.
import os
# Arg parser
from config import globalparser
args = vars(globalparser.getparser().parse_args())

from config import globalconfig
globalconfig.run()
globalconfig.update_filename(__file__)
globalconfig.update_parser_params(args)

# Essential network building blocks.
from Networks.Nets import Resnet
from torchvision import models
from efficientnet_pytorch import EfficientNet

# Data loader.
import torchvision.transforms as T
from DataUtils import isic2019 as data

# Official packages.
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

torch.set_num_threads(1)

# 下面开始进行主干内容

transform = {
  'train': T.Compose([
    T.Resize((500,500)), # 放大
    T.RandomResizedCrop((300,300)), # 随机裁剪后resize
    T.RandomHorizontalFlip(0.5), # 随机水平翻转
    T.RandomVerticalFlip(0.5), # 随机垂直翻转
    T.RandomApply([T.RandomRotation(90)], 0.5), # 随机旋转90/270度
    T.RandomApply([T.RandomRotation(180)], 0.25), # 随机旋转180度
    T.RandomApply([T.ColorJitter(brightness=np.random.random()/5+0.9)], 0.5), #随机调整图像亮度
    T.RandomApply([T.ColorJitter(contrast=np.random.random()/5+0.9)], 0.5), # 随机调整图像对比度
    T.RandomApply([T.ColorJitter(saturation=np.random.random()/5+0.9)], 0.5), # 随机调整图像饱和度
    T.ToTensor(),
    T.Normalize(mean=(0.6678, 0.5298, 0.5244), std=(0.2527, 0.1408, 0.1364))
  ]), 
  'val': T.Compose([
    T.Resize((300,300)), # 放大
    T.CenterCrop((300,300)),
    # T.RandomResizedCrop((224,224)), # 随机裁剪后resize
    # T.RandomHorizontalFlip(0.5), # 随机水平翻转
    # T.RandomVerticalFlip(0.5), # 随机垂直翻转
    # T.RandomApply([T.RandomRotation(90)], 0.5), # 随机旋转90/270度
    # T.RandomApply([T.RandomRotation(180)], 0.25), # 随机旋转180度
    # T.RandomApply([T.ColorJitter(brightness=np.random.random()/5+0.9)], 0.5), #随机调整图像亮度
    # T.RandomApply([T.ColorJitter(contrast=np.random.random()/5+0.9)], 0.5), # 随机调整图像对比度
    # T.RandomApply([T.ColorJitter(saturation=np.random.random()/5+0.9)], 0.5), # 随机调整图像饱和度
    T.ToTensor(),
    T.Normalize(mean=(0.6678, 0.5298, 0.5244), std=(0.2527, 0.1408, 0.1364))
  ])
}

# GOT DATA
torch.cuda.set_device(os.environ['device'])
dataloader = data.getdata(transform, {'num_workers': 4, 'pin_memory': True})

# DEFINE MODEL
model = EfficientNet.from_pretrained('efficientnet-b3')
# Modify.
num_fcin = model._fc.in_features
model._fc = nn.Linear(num_fcin, len(dataloader['train'].dataset.classes))

# print (model)

if args['continue']:
  model = globalconfig.loadmodel(model)

model = model.to(device=os.environ['device'])

print ('Params to learn:')
params_to_update = []
for name,param in model.named_parameters():
  if param.requires_grad == True:
    params_to_update.append(param)
    print ('\t', name)

# DEFINE OPTIMIZER
# optimizer = optim.SGD(params_to_update, lr=args['learning_rate'], momentum=0.9)
optimizer = optim.Adam(params_to_update, lr=args['learning_rate'])

criterion = nn.functional.cross_entropy

# Useful tools.
from tools import train_and_check as mtool

# RUN TRAINING PROCEDURE
mtool.train(
  model,
  dataloader,
  optimizer,
  criterion,
  args['epochs']
)