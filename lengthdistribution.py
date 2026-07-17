#Importing the library

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import seaborn as sns

from config import PROCESSED_DATA_DIR, RAW_DATA_DIR
#Timeframe you want to analyze the system

D=10
C=100


t = str(800) 
M=[]
for i in range(1,17):
    k1 = str(i) 

    file_path = RAW_DATA_DIR / f"C0-{C},D-{D}" / f"SEED{i}" / "data_frame" / f"datas_frame_{t}.xyz"
    df = pd.read_fwf(file_path, names=["s", "x", "y", "z", "lf"])
    

    
#   sns.displot(df, x="lf", hue="s", kind="kde", fill=True)
    lf=df['lf'].to_numpy()
    
    x,y = sns.distplot(lf).get_lines()[0].get_data()
    H,X,_=plt.hist(lf,density=True,bins=20)
    
    n = len(H)
    X = np.linspace(0,3,n)
    np.savetxt(PROCESSED_DATA_DIR / f"KDE{k1}.txt", np.array([x,y]).T, delimiter = "   ", fmt = "%0.3e")
    np.savetxt(PROCESSED_DATA_DIR / f"Prob_dens{k1}.txt", np.array([X,H]).T, delimiter="   ", fmt="%0.3e")
    





























