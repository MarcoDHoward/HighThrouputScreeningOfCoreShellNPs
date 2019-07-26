#!/usr/local/bin/python
######################################################################
#This is the script to calculate the activity of CO oxidation reaction
#The following parameters are needed 
# r->rate; K->eq const; p->pressure; cv->coverage(v,co,o);
# ins-> intersection; sl->slope;  k-> rate const (p,n);
# CO +* -> CO* (R1)  r1=K1*pco*cvv
# O2 +* -> O2* (R1)  r2=K2*po2*cvv
# O2* + * -> 2O* (R3)  r3=k3p*K2*po2*cvv*cvv-k3n*cvo*cvo = x3*cvv**2-y3*cvo**2
# O* + CO* -> CO2 + 2*(R4) r4 = k4p*K1*pco*cvo*cvv-k4n*pco2*cvv**2=x4*cvv*cv0-y4*cvv**2
# O2* +CO* -> CO2 +O*+* (R4) r5=k5p*K1*K2*po2*pco*cvv*cvv-k5n*pco2*cvv*cvo=x5*cvv**2-y5*cvo*cvv
# Ets3 = sl3* Ebo  +ins3; Ets4 = sl4*(Ebo+Ebco)+ins4; Ebo2=sl2*Ebo+ins2
######################################################################
s0 = []
entro_o2= 205.152/1.602177/6.02/10000.0
entro_co2= 213.79/1.602177/6.02/10000.0
entro_co= 197.66/1.602177/6.02/10000.0
h=1.0
kb=1.0/11604.5 
Eco2=-3.26
import numpy as np
#from data import cats

pco2=0.00 ; pco=0.67 ;po2=0.33
T=600.0 ; 
mu=kb*T/h;

sl3= 1.39; sl4=0.70 ; sl2=0.89 ;sl5=0.00
ins3= 1.56; ins4=0.02;ins2=0.17 ;ins5=-0.00 
cats = { 0 : {'ebo':0, 'ebco':0, 'symbol':'', 'type':'' }}

def rate(Ebo, Ebco):
    Ets3=sl3*Ebo+ins3
    Ets4=sl4*(Ebo+Ebco)+ins4
    Ets5=sl5*(Ebo+Ebco)+ins5
    Ebo2=sl2*Ebo+ins2
    dE1=Ebco; dS1=-entro_co
    dE2=Ebo2; dS2=-entro_o2
    Ea3p=Ets3-Ebo2; Ea3n=Ets3-2.0*Ebo
    Ea4p=Ets4-Ebco-Ebo; Ea4n=Ets4-Eco2; dS4n=-entro_co2 
    Ea5p=Ets5-Ebo2-Ebco; Ea5n=Ets5-Ebo-Eco2; dS5n=-entro_co2 
    K1=np.exp((-dE1+T*dS1)/kb/T)
    K2=np.exp((-dE2+T*dS2)/kb/T)
    k3p=mu*np.exp(-Ea3p/kb/T)
    k3n=mu*np.exp(-Ea3n/kb/T)
    k4p=mu*np.exp(-Ea4p/kb/T)
    k4n=mu*np.exp(-Ea4n/kb/T)*np.exp(dS4n/kb)
    k5p=mu*np.exp(-Ea5p/kb/T)
    k5n=mu*np.exp(-Ea5n/kb/T)*np.exp(dS5n/kb)
    x3=k3p*K2*po2; y3=k3n
    x4=k4p*K1*pco; y4=k4n*pco2
    x5=k5p*K1*K2*po2*pco ; y5=k5n*pco2   
    #print x3, y3, x4,y4,x5,y5
    tmp = 8.0*y3*(2*x3+y4+x5)/(x4+y5)/(x4+y5)
    #print tmp
    if (tmp < 0.0000000001):
        W = 0.5*tmp*(x4+y5)/4.0/y3
    else:
        W= (x4+y5)/4.0/y3*(-1.0+np.sqrt(1.0+tmp))
    #print W
    cvv=1.0/(1.0+K1*pco+K2*po2)
    cvo2=K2*po2*cvv
    cvco=K1*pco*cvv
    cvo=1.0
    r3s=k3p*cvo2*cvv
    #print cvo
    r4s=k4p*cvco*cvo
    r5s=k5p*cvo2*cvco
    #print r3s,r5s,r4s
    rs=min(2*r3s,r4s)
    region=-1
    As=kb*T*np.log(rs/mu)
    return As,region

#plot3D part########################
#print rate(0.0,-2.0)
pt_ebo = -1.25  ## Norskov Data From Liang Cats
pt_ebco = -1.20  ##

x0 = np.arange(-2.0, -0.9, 0.02)
x = x0 - pt_ebo
y0 = np.arange(-1.5, -0.4, 0.02)
y = y0 - pt_ebco
Z = np.zeros((len(y),len(x)))
R = np.zeros((len(y),len(x)))

X, Y = np.meshgrid(x, y)

#'''
for j in range(len(x0)):
    for i in range(len(y0)):
        Z[i][j], R[i][j] = rate(x0[j], y0[i]) 

import pickle
pklfile = open('coox_rate.pkl', 'wb')
xyZ = [X, Y, Z]
pickle.dump(xyZ, pklfile)
#'''
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot, mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from pylab import *
from matplotlib import rc, rcParams
import json



#rc('text',usetex=True)
#rc('font',**{'family':'serif','serif':['Computer Modern']})

pklfile = open('coox_rate.pkl', 'rb')
import pickle
xyE = pickle.load(pklfile)
Xt = xyE[0]
Yt = xyE[1]
E  = xyE[2]


#fig=plt.figure(figsize=(8,8))
fig=plt.figure()
ax=fig.gca()
#plt.title(r'$\rm CO Oxidation Activity Contour$'+"\n"+r'$T= 600K$'+"\t"+r'$P_{\rm CO}= 0.67$'+"\t"+r'$P_{\rm {O_2}}=0.33$',fontsize=14)
matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
CS0= plt.contour(Xt, Yt, E, 20,
                colors = 'k')
CS4 = plt.contourf(Xt, Yt, E, 20,
                origin = 'lower', 
                norm=plt.normalize(vmin=-3.0,vmax=-0.6)
                )
ax.set_xlim(-0.7,0.3)
ax.set_ylim(-0.3,0.7)
plt.tick_params(axis='both', which='major', labelsize=15)
#ax.set_xlabel(r'$Eb_{\rm O}-Eb{^{\rm Pt}}{_{\rm O}}$',fontsize=18,weight='bold')
#ax.set_ylabel(r'$Eb_{\rm CO}-Eb{^{\rm Pt}}{_{\rm CO}}$',fontsize=18,weight='bold')
x0=[];x1=[];y0=[];y1=[];x2=[];y2=[];x3=[];y3=[];x3e=[];y3e=[]






jsonData = json.load(open ( 'allresults.json', 'r' ))
newKey = ''
cats = { 0 : {'ebo':0.0, 'ebco':0.0, 'symbol':'', 'type':'' }}
numEntries = 0
for key in (jsonData):
  if key.split('/')[-1] == "Binding Energy":
    
    newKey =  '/'.join(key.split('/')[0:4]) + "/CO Binding Energy"
    if newKey in list(jsonData.keys()):
      partsList = key.split('/')[0 :len(key) -1]
      cats[numEntries] = numEntries 
      ebo = float(jsonData[key]['result'])
      ebco = float(jsonData[newKey]['result'])
      symbol =  "%s%s@%s%s" %(partsList[0], partsList[1], partsList[2], partsList[3])
      cats[numEntries] = {'ebo':ebo, 'ebco':ebco, 'symbol':symbol, 'type':'ps'}
      numEntries +=1




for i in range( len(cats)):
    x=cats[i]['ebo']-pt_ebo
    y=cats[i]['ebco']-pt_ebco
    s=cats[i]['symbol']
    t=cats[i]['type']
    if (t=='ps' and  (x > -0.5 and x < 0.2 ) and (y < 0.7 and y >= -.3)):                       
        x0.append(x)
        y0.append(y)
        s0.append(s)
        #plt.text(x-0.00,y+0.03,s,weight='medium',fontsize=12,va='center',ha='center', color='k')
    elif (t=='spt'):
        x1.append(x)
        y1.append(y)
#        plt.text(x-0.00,y+0.03,s,weight='medium',fontsize=12,va='center',ha='center', color='b')
    elif (t=='npp1'):
        x2.append(x)
        y2.append(y)
#        plt.text(x-0.03,y+0.03,s,weight='medium',fontsize=12,va='center',ha='center', color='g')    
    elif (t=='acnp'):
        x3.append(x)
        y3.append(y)
        x3e.append(cats[i]['xerr'])
        y3e.append(cats[i]['yerr'])
        #plt.text(x-0.00,y-0.06,s,fontsize=6,va='center',ha='left', color='c')
       
plt.colorbar()
#print x3, y3, x3e, y3e
plt.plot(x0, y0, 'ko', label='Pure slab',markersize=10)
plt.xlabel("NP_ebo - Pt_ebo")
plt.ylabel("NP_ebco - Pt_ebco")

pt_ebo = -1.25  ## Norskov Data From Liang Cats
pt_ebco = -1.20  ##

print(x0, y0, s0)

for i, txt in enumerate(s0):
  plt.annotate(txt, (x0[i], y0[i]), xycoords='data')
plt.plot(x1, y1, 'ko', label='Slab with Pt on top',markersize=10,mec='k',mfc='none')
plt.plot(x2, y2, 'b^',label='Pt shell NP140 (111)',markersize=10,mec='b')
#ax.errorbar(x3,y3, xerr=x3e, yerr=y3e,fmt='b^', mec='b',mfc='none', label='Au$_{x}$Pd$_{1-x}$@Pt',capsize=2, markersize=10)
#ax, _ = mpl.colorbar.make_axes(plt.gca(), shrink=1.0)
#cbar = mpl.colorbar.ColorbarBase(ax, cmap=mpl.cm.jet,
                               #norm=mpl.colors.Normalize(vmin=-7.0, vmax=0.0))

plt.savefig('coox_rate.png')
plt.savefig('coox_rate.eps')
#'''

print cats
