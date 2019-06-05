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

# Data loader.
from DataUtils import isic2018

# Official packages.
import torch
import torch.nn as nn
import torch.optim as optim

# 下面开始进行主干内容

# GOT DATA
dataloader = isic2018.getdata()

# DEFINE MODEL
model = Resnet.Resnet152()

if args['continue']:
  model = globalconfig.loadmodel(model)

# DEFINE OPTIMIZER
# optimizer = optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9)
optimizer = optim.Adam(model.parameters(), lr=args['learning_rate'])

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