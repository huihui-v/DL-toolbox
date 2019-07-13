import torch
import torch.nn as nn
import os

# class DOCLoss(nn.Module):
#   def __init__(self):
#     super(DOCLoss, self).__init__()
#     # self.weight = weight

#   def forward(self, input, target, weight=None):
#     sigmoid = 1 / (1 + torch.exp(-input))
#     bias = torch.ones_like(input)
#     bias[range(0, bias.shape[0]), target] = 0
#     log_sigmoid = torch.log(bias - sigmoid)
#     loss = -torch.sum(log_sigmoid)
#     return loss

#   def prediction(input, t=0.5, weight=None):
#     sigmoid = 1 / (1 + torch.exp(-input))
#     values, indices = sigmoid.max(1)
#     predict = torch.where(values > t, indices, torch.tensor([-1]))
#     return predict

def loss(input, target, unknown_ind, weight=None):
  sigmoid = 1 - 1 / (1 + torch.exp(-input))
  sigmoid[range(0, sigmoid.shape[0]), target] = 1 - sigmoid[range(0, sigmoid.shape[0]), target]
  sigmoid = torch.log(sigmoid)
  sigmoid = torch.cat([sigmoid[:, :unknown_ind], sigmoid[:, unknown_ind+1:]], dim=1)
  weight = torch.cat([weight[:unknown_ind], weight[unknown_ind+1:]])/(1-weight[unknown_ind])
  if weight is not None:
    loss = -torch.sum(sigmoid * weight)
  else:
    loss = -torch.sum(sigmoid)
  return loss

def prediction(input, unknown_ind, t=0.5, weight=None):
  sigmoid = 1 / (1 + torch.exp(-input))
  # sigmoid = torch.cat([sigmoid[:, :unknown_ind], sigmoid[:, unknown_ind+1:]], dim=1)
  values, indices = sigmoid.max(1)
  if int(os.environ['gpus']) == 0:
    device = 'cpu'
  elif int(os.environ['gpus']) == 1:
    device = os.environ['device']
  else:
    device = os.environ['device'][:6]
  predict = torch.where(values > t, indices, torch.tensor([unknown_ind]).to(device=device))
  return predict