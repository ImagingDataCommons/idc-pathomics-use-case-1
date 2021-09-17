#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
sys.path.append('/usr/local/lib/python3.7/dist-packages')
#%load_ext autoreload
#%autoreload 2


# # Preprocessing

# In[2]:


#!sudo apt-get update
#!sudo apt-get install --no-install-recommends -y python3-openslide
#!sudo pip3 install -r ../requirements.txt


# In[3]:


input_dir = '/home/jupyter/idc_input/'
slides_dir = os.path.join(input_dir, 'cptac_slides')
tiles_dir = os.path.join(input_dir, 'cptac_tiles')


# In[ ]:


from data.tile_generation_cptac_tumbnail import generate_tiles

generate_tiles(slides_dir, os.path.join(input_dir, 'slides_metadata.csv'), tiles_dir, 'idc-pathomics-000')


# In[ ]:




