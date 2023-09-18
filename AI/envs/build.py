import os
os.chdir("./AI/envs/env_2048/cython_2048")
os.system("python setup.py build_ext --inplace")