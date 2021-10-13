# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 09:18:25 2021

@author: LocalAdmin
"""

import pickle as pkl
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

path = 'Results/MSD/'
file = 'MSD_LPVNN_3stateslam0.01.pkl'


res=pkl.load(open(path+file,'rb'))

# for i in range(len(res)):
#     res.iloc[i,1] = res.iloc[i,1][0]
#     res.iloc[i,0] = res.iloc[i,0][0]


# res['structure'] = None

# res.iloc[0:90]['structure'] = 'A0'
# res.iloc[90:180]['structure'] = 'A1'
# res.iloc[180:270]['structure'] = 'A2'
# res.iloc[270:360]['structure'] = 'A3'
# res.iloc[360:450]['structure'] = 'A4'
# res.iloc[450:540]['structure'] = 'A5'
# res.iloc[540:630]['structure'] = 'A6'
# res.iloc[630:720]['structure'] = 'A7'
# res.iloc[720:810]['structure'] = 'A8'

# pkl.dump(res,open(path+file,'wb'))


# Delete NaNs ?

# for i in range(len(res)):
#     try:
#         if np.isnan(res.iloc[i]['BFR_test']) or np.isinf(res.iloc[i]['BFR_test']):
#             # res.drop(res.index[i],inplace = True)
#             continue
#         elif res.iloc[i]['BFR_test']==0.0:
#             res.drop(res.index[i],inplace = True)
#     except:
#         break
        
palette = sns.color_palette()[1::]

fig, axs = plt.subplots() #plt.subplots(2,gridspec_kw={'height_ratios': [1, 1.5]})

fig.set_size_inches((9/2.54,4/2.54))
fig.set_size_inches((9,4))

sns.boxplot(x='dim_phi', y='BFR_test', hue='structure', data=res, ax=axs,
            color=".8")

sns.stripplot(x='dim_phi', y='BFR_test', hue='structure',data=res, 
                  palette=palette, ax=axs, linewidth=0.1,
                   dodge=True,zorder=1,size=10)

# sns.boxplot(x='theta', y='BFR', hue='model',data=BFR_on_val_data, 
#                   palette="Set1",fliersize=2,ax=axs[1], linewidth=1)

axs.legend_.remove()
axs.set_xlabel(r'$\dim(\phi_k)$')
axs.set_ylabel(None)
axs.set_ylim(60,105)
fig.tight_layout()


# fig.savefig('Bioreactor_StateSched_Boxplot.png', bbox_inches='tight',dpi=600)
