import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import math
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import seaborn as sns
import statistics as sts


D = 10

C = 100

SEEDS = 4

t = str(800)


for w in range(1,SEEDS+1):
    
    k1 = str(w)
    
    df=pd.read_fwf(('/D_'+str(D)+'/C_'+str(C)+'/SEED'+str(w)+'/data_frame/datas_frame_'+t+'.xyz'),names=["s","x", "y","z","ux","uy","uz","lf"])     
    
    df = df.dropna()
#    C1 = df[(df['s']=='C')]
#    box = 200
    ux = df['ux'].to_numpy()
    uy = df['uy'].to_numpy()
    r =  df[["x","y"]].to_numpy()
#   r = r - np.rint(r/box)*box 
    
    x = r[:,0]
    y = r[:,1]
    a_j=[]
    
    df3 = pd.DataFrame({'x': r[:,0], 'y': r[:,1] , 'ux': ux ,'uy': uy})
    
    
    # Neighbour Information
    
    for j in range(len(ux)):
        A_j=[]
        u=(x[j],y[j])
        v=(ux[j],uy[j])



        for i in range(len(x)):
            if ((x[i]-x[j])*(x[i]-x[j])+(y[i]-y[j])*(y[i]-y[j])<=100 and i!=j):
                A_j.append(i)

        a_j.append(A_j)


    S_mean=[]
    for j in range(len(ux)):
        v=(ux[j],uy[j])
        a_j[j]
        S=[]
        for i in range(len(a_j[j])):
            neighbour=df3.loc[[a_j[j][i]]]

            ux_neighbour = neighbour['ux'].to_numpy()
            uy_neighbour = neighbour['uy'].to_numpy()

            u_neighbour=[ux_neighbour[0],uy_neighbour[0]]

            cost=(np.dot(v, u_neighbour))
            s = ((1.5*cost*cost) - 0.5)
            S.append(s)  
        S_mean.append(np.mean(S))
    S_mean = np.array(S_mean)
    S_mean = S_mean[np.logical_not(np.isnan(S_mean))]
    
    #S_mean = abs(S_mean)
    
    Mean = np.mean(S_mean)
    h = 0
    X = []
    H = []
    x,y = sns.distplot(S_mean).get_lines()[0].get_data()
    H,X,_=plt.hist(S_mean,density=True,bins=20)
    #plt.show()
    n = len(H)
    X = np.linspace(-1,1,n)
    np.savetxt(f"KDE"+k1+".txt", np.array([x,y]).T, delimiter = "   ", fmt = "%0.3e")
    np.savetxt(f"Prob_dens"+k1+".txt", np.array([X,H]).T, delimiter = "   ", fmt = "%0.3e")
    
    
    
    
    
    
    
    
    