import os
import sys
import time

def run():
  """
  Run global configuration.
  
  Args:
    None.

  Return:
    None, but set environment parameters.
      where_am_i: 'pc' or 'lab', showing where this project is running.
      datapath: Data dir.
      device: Device configuration with auto recommendation, namely, 'cpu' or 'cuda:#id'
      logdir: Tensorboard log dir.
  """
  user = os.popen('whoami').readline()
  from config import deviceSelector as d

  if user.find('jianfei') == -1:
    os.environ['where_am_i'] = 'pc'
    os.environ['datapath'] = ''
    os.environ['device'] = 'cpu'
    os.environ['logdir'] = '/home/huihui/Log/tensorboard-log/'
  else:
    os.environ['where_am_i'] = 'lab'
    os.environ['datapath'] = ''
    os.environ['device'] = 'cuda:'+d.get_gpu_choice()
    os.environ['logdir'] = '/data0/jianfei/tensorboard-log/'
  os.environ['logdir'] += time.asctime().replace(' ', '-')

  print('Finish global configuration!')

def update_filename(file):
  """
  Update logdir to take filename.

  Args:
    file: String of __file__, which is the full path of file.

  Return:
    None, but set environment parameters.
      logdir: logdir + '-' + filename
      filename: String of entrance file name.(Without postfix '.py')
  """
  s = file.rfind('/')
  e = file.find('.')
  filename = file[s+1:e]
  os.environ['logdir'] += '-'
  os.environ['logdir'] += filename
  os.environ['filename'] = filename