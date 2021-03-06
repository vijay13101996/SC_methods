# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 12:52:02 2017

@author: Dell
"""

# Function file for the Interference pattern

from scipy import *
from scipy.fftpack import fft,ifft, fftshift, ifftshift
from scipy.integrate import odeint, ode
from multiprocessing import Pool,cpu_count
from matplotlib import pyplot as plt
from functools import partial
import numpy as np
import os
#import newfunc as cfunc

previous = 0.0
tPrintSpace = 0.01
tPrint = 0.0
m = 1.0

phasejump = 0
previous = 0j
current =0j


gammaxf = 0.5
gammayf = 0.5
gammaxi = 0.5
gammayi = 0.5
gammai = [[gammaxi,0],[0,gammayi]]
gammaf = [[gammaxf,0],[0,gammayf]]
S20 = ([2*gammaxi*1j,0],[0,2*gammayi*1j])     # Should be careful about this. 

cutoff = 10000

# Change dpxdpy, store sigma and j0

#----------------------------------
##from Parameter_file_double_slit_eckart_50_50_4_4 import *
##

##
##Nxr = 4
##Nxi = 2
##Nyr = 4
##Nyi = 2
##
##x0=-5.0
##y0=0.0
##px0=0.0
##py0=0.0
##
##xbar =  zeros(Nxr*Nxi*Nyr*Nyi) + 0j
##ybar = zeros_like(xbar) + 0j
##pxbar = zeros_like(xbar) + 0j
##pybar = zeros_like(ybar) + 0j
##
##xfinbar = zeros_like(xbar) + 0j
##yfinbar = zeros_like(ybar) + 0j
##pxfinbar = zeros_like(pxbar) + 0j
##pyfinbar = zeros_like(pybar) + 0j                
##Sfinbar = zeros_like(xbar) + 0j

#----------------------------------

def ketmanifold(xi,yi, pxi,pyi, xbar, pxbar, ybar, pybar, gammaxi, gammayi,Nxr,Nxi,Nyr,Nyi,widthxr,widthxi,widthyr,widthyi):
    if (Nxr==1 and Nxi==1 and Nyr==1 and Nyi==1):
##        xi = (-3.4+1.6j)
##        yi = (1.6-1.2j)
        xbar[0] = xi
        pxbar[0] = -1j*(2*gammaxi*xi + 1j*pxi - 2*gammaxi*xbar[0])
        ybar[0] = yi
        pybar[0] = -1j*(2*gammayi*yi + 1j*pyi - 2*gammayi*ybar[0])
    else:
        for i in range(Nxr):
            for j in range(Nxi):
                for k in range(Nyr):
                    for l in range(Nyi):
                        xbar[((i + Nxr*j)*Nyr + k)*Nyi + l] = xi - widthxr/2 + (i)*widthxr/Nxr + (0 - widthxi/2 + (j)*widthxi/Nxi)*1j                     
                        pxbar[((i + Nxr*j)*Nyr + k)*Nyi + l] = -1j*(2*gammaxi*xi + 1j*pxi - 2*gammaxi*xbar[((i + Nxr*j)*Nyr + k)*Nyi + l])
                        ybar[((i + Nxr*j)*Nyr + k)*Nyi + l] = yi - widthyr/2 + (k)*widthyr/Nyr + (0 - widthyi/2 + (l)*widthyi/Nyi)*1j
                        pybar[((i + Nxr*j)*Nyr + k)*Nyi + l] = -1j*(2*gammayi*yi + 1j*pyi - 2*gammayi*ybar[((i + Nxr*j)*Nyr + k)*Nyi + l])
                        
                        #print(i,j,k,l,((i + Nxr*j)*Nyr + k)*Nyi + l,xbar[((i + Nxr*j)*Nyr + k)*Nyi + l])
  

##ketmanifold(x0,y0, px0,py0, xbar, pxbar, ybar, pybar, gammaxi, gammayi,Nxr,Nxi,Nyr,Nyi,widthx,widthy)
##
##print(xbar,ybar)                     


# Ket manifold function is working alright

#------------

# def ketmanifold(xi,yi, pxi,pyi, xbar, pxbar, ybar, pybar, gammaxi, gammayi,Nxr,Nxi,Nyr,Nyi,widthxr,widthxi,widthyr,widthyi):
    # if (Nxr==1 and Nxi==1 and Nyr==1 and Nyi==1):
# ##        xi = (-3.4+1.6j)
# ##        yi = (1.6-1.2j)
        # xbar[0] = xi
        # pxbar[0] = -1j*(2*gammaxi*xi + 1j*pxi - 2*gammaxi*xbar[0])
        # ybar[0] = yi
        # pybar[0] = -1j*(2*gammayi*yi + 1j*pyi - 2*gammayi*ybar[0])
    # else:
        # for i in range(Nxr):
            # for j in range(Nxi):
                # for k in range(Nyr):
                    # for l in range(Nyi):
                        # xbar[((i + Nxr*j)*Nyr + k)*Nyi + l] = xi - widthxr/2 + (i)*widthxr/Nxr + (0 - widthxi/2 + (j)*widthxi/Nxi)*1j                     
                        # pxbar[((i + Nxr*j)*Nyr + k)*Nyi + l] = -1j*(2*gammaxi*xi + 1j*pxi - 2*gammaxi*xbar[((i + Nxr*j)*Nyr + k)*Nyi + l])
                        # ybar[((i + Nxr*j)*Nyr + k)*Nyi + l] = yi  + 0.5*(k)*widthyr/Nyr + (0 - widthyi/2 + 0.5*(l)*widthyi/Nyi)*1j
                        # pybar[((i + Nxr*j)*Nyr + k)*Nyi + l] = -1j*(2*gammayi*yi + 1j*pyi - 2*gammayi*ybar[((i + Nxr*j)*Nyr + k)*Nyi + l])

# #------------



def f(t,r,turningpoints,maxpx,maxpy,maxp,gammaf,S20, potential,dxpotential,dypotential,ddpotential1,ddpotential2,ddpotential3,ddpotential4,gammai,successarr):
    global current, tPrint, tPrintSpace
    r=r.view(dtype=complex)
    previous = turningpoints[1]
    #print("Hi")
    x,px,y,py,S, mpp1,mpp2,mpp3,mpp4,mpq1,mpq2,mpq3,mpq4,mqp1,mqp2,mqp3,mqp4,mqq1,mqq2,mqq3,mqq4=  r
    if(abs(px**2+py**2)>cutoff):  #Change at the other location too, when required
        successarr[0] = -1

    if(abs(px)>abs(maxpx[0])):
        maxpx[0] = px

    if(abs(py)>abs(maxpy[0])):
        maxpy[0] = py

    if(abs(px**2+py**2)>maxp[0]):
        maxp[0] = abs(px**2+py**2)
        
    
    ddV1 = ddpotential1(x,y)
    ddV2 = ddpotential2(x,y)
    ddV3 = ddpotential3(x,y)
    ddV4 = ddpotential4(x,y)
    drdt = array([px,-dxpotential(x,y), py, -dypotential(x,y),px**2/2 + py**2/2 - potential(x,y), 
                 -(ddV1*mqp1 + ddV2*mqp3),-(ddV1*mqp2 + ddV2*mqp4),
                 -(ddV3*mqp1 + ddV4*mqp3),-(ddV3*mqp2 + ddV4*mqp4),
                 -(ddV1*mqq1 + ddV2*mqq3),-(ddV1*mqq2 + ddV2*mqq4),
                 -(ddV3*mqq1 + ddV4*mqq3),-(ddV3*mqq2 + ddV4*mqq4),
                   mpp1,mpp2,mpp3,mpp4, mpq1,mpq2,mpq3,mpq4])

    # mpp = r[5:9].reshape((2,2))
    # mpq = r[9:13].reshape((2,2))
    # mqp = r[13:17].reshape((2,2))
    # mqq = r[17:21].reshape((2,2))
    
    # current  = np.linalg.det(2*np.matmul(gammaf,mqq) + 2*np.matmul(np.matmul(gammaf,mqp),S20)\
                       # -1j*mpq - 1j*np.matmul(mpp,S20))
    
    # if(t>tPrint+tPrintSpace):
        
        
        # if(real(current) < 0 and imag(previous)*imag(current) < 0):
           # phasejump+=1
           
    # previous = current
    # tPrint=t

    # #print('current,t',current,t)

    # #current = exp(-2*1j*Squantum)*4*((gammaf[0][0] + gammaxx)*(gammaf[1][1] + gammayy) - (gammaf[0][1] + gammaxy)*(gammaf[1][0] + gammayx))

    
    # if(real(current) < 0 and imag(previous)*imag(current) < 0):
           # turningpoints[0] += 1
    # turningpoints[1] = current
                 
    return drdt.view(dtype=float)

def solout(t,r):
    global phasejump,previous,current,gammaf,S20
    r=r.view(dtype=complex)
    #print('here')
    x,px,y,py,S, mpp1,mpp2,mpp3,mpp4,mpq1,mpq2,mpq3,mpq4,mqp1,mqp2,mqp3,mqp4,mqq1,mqq2,mqq3,mqq4=  r

    mpp = r[5:9].reshape((2,2))
    mpq = r[9:13].reshape((2,2))
    mqp = r[13:17].reshape((2,2))
    mqq = r[17:21].reshape((2,2))

    current  = np.linalg.det(2*np.matmul(gammaf,mqq) + 2*np.matmul(np.matmul(gammaf,mqp),S20)\
                       -1j*mpq - 1j*np.matmul(mpp,S20))

    #print('t',t,current)

    x1,y1 =real(current),imag(current)
    x2,y2 = real(previous),imag(previous)
    intercept=0.0
    if(y2!=y1):
        intercept = (x1*(y2-y1) - y1*(x2-x1))/(y2-y1)
    else:
        intercept = float("inf")
    #print('intercept',intercept)

    # if(real(current) < 0 and imag(previous)*imag(current) < 0):
       # phasejump+=1
       #print('phasejump')

    if(intercept<0.0 and ((x1<intercept<x2) or (x2<intercept<x1))):
        phasejump+=1
        #print('phasejump,here')

    previous = current

    if(abs(px**2+py**2)>cutoff):   # Change at the other location too, when required
        #print('diverging',px,py)
        return -1 
    
def traj_propagator(init_array,potential,dxpotential,dypotential,ddpotential1,ddpotential2,ddpotential3,ddpotential4,timear):
        global tPrint,phasejump,previous
        sol = ode(f)
        sol.set_integrator('dop853',nsteps=1000000)         #11/05/18 Check timesteps, it might be excessive.
        sol.set_solout(solout)
        init_array = array(init_array)
        # if all(init_array[:4].imag==0):         
                # print("REAL")

                    #print('i',i)
        x,px,y,py,S, mpp1,mpp2,mpp3,mpp4,mpq1,mpq2,mpq3,mpq4,mqp1,mqp2,mqp3,mqp4,mqq1,mqq2,mqq3,mqq4=init_array
        sol.set_initial_value(init_array.view(dtype=float),t=0.0)
        tempar = [0,2*np.linalg.det(np.add(gammaf,gammai))]
        successarr = [1]
        maxpx = [px]
        maxpy = [py]
        maxp = [abs(px**2 + py**2)]


        sol.set_f_params(tempar,maxpx,maxpy,maxp,gammaf,S20,potential,dxpotential,\
        dypotential,ddpotential1,ddpotential2,ddpotential3,ddpotential4,gammai,successarr)

        phasejump=0
        previous = 2*np.linalg.det(np.add(gammaf,gammai))
        current = 2*np.linalg.det(np.add(gammaf,gammai))
        trajdata = zeros((len(timear),len(init_array)+5),dtype=complex)
        #tPrint = -1e-3
        #print('tPrint',tPrint,'xbar',x,'ybar',y)
        for tc in range(len(timear)):
            
            if tc>0:
              sol.integrate(timear[tc])
            result=sol.y.view(dtype=complex)
            trajdata[tc,:-5] = result
            trajdata[tc,21] = phasejump
            trajdata[tc,22]=successarr[0]
            trajdata[tc,23]=maxpx[0]
            trajdata[tc,24]=maxpy[0]
            trajdata[tc,25]=maxp[0]
        
        #print(trajdata[len(timear)-1][0])
        #print('tPrint',tPrint,'xbar',x,'ybar',y)
        return trajdata
    
def finalconditions(xbar,pxbar,ybar, pybar, xi, pxi, yi, pyi, gammaxi,gammayi,\
                    gammaxf,gammayf,Nxr,Nxi,Nyr,Nyi,potential,dxpotential,dypotential,\
                    ddpotential1, ddpotential2, ddpotential3, ddpotential4, timear,gammaf,gammai,mpp,mpq,mqp,mqq,S20,successcheck,maxmomentum ):
    global tPrint,phasejump,previous
    sol = ode(f)
    sol.set_integrator('dop853',nsteps=1000000)         #11/05/18 Check timesteps, it might be excessive.
    sol.set_solout(solout)
    
    onearr = ones(len(xbar))
    zeroarr = zeros(len(xbar))
    xiarr = xi*onearr
    yiarr = yi*onearr
    pxiarr = pxi*onearr
    pyiarr = pyi*onearr
    Sarr = -1j*(0.25*log(2*gammaxi*onearr/pi)) -1j*gammaxi*(xbar**2 - (xiarr)**2)+ (xbar*pxbar - xiarr*pxiarr) +\
                               -1j*(0.25*log(2*gammayi*onearr/pi)) -1j*gammayi*(ybar**2 - yiarr**2)+ (ybar*pybar - yiarr*pyiarr)
    init_conditions_array=array([xbar,pxbar,ybar,pybar,Sarr,onearr,zeroarr,zeroarr,onearr,\
        zeroarr,zeroarr,zeroarr,zeroarr, zeroarr,zeroarr,zeroarr,zeroarr, onearr,zeroarr,zeroarr,onearr])
       

    #for tup in zip(*init_conditions_array):
     #   print('tup',tup)
            
    #print('init',init_conditions_array)
    #print(zip(*init_conditions_array))
    
    
    #if __name__ == '__main__':
    print('CPU',len(os.sched_getaffinity(0)))
    p = Pool(cpu_count()-1 or 1 )
    data=p.map(partial(traj_propagator,potential=potential,dxpotential=dxpotential,\
        dypotential=dypotential,ddpotential1=ddpotential1,ddpotential2=ddpotential2,ddpotential3=ddpotential3,ddpotential4=ddpotential4,timear=timear)\
        ,zip(*init_conditions_array))
        
    return array(data)
        
    
    
    # for i in range(Nxr*Nxi*Nyr*Nyi):
        # print('data',data[i][len(timear)-1][0])
    
    
    
    

    # for i in range(Nxr*Nxi*Nyr*Nyi):
                  
                    # y0 = array([xbar[i],pxbar[i],ybar[i],pybar[i],\
                               # -1j*(0.25*log(2*gammaxi/pi)) -1j*gammaxi*(xbar[i]**2 - xi**2)+ (xbar[i]*pxbar[i] - xi*pxi) +\
                               # -1j*(0.25*log(2*gammayi/pi)) -1j*gammayi*(ybar[i]**2 - yi**2)+ (ybar[i]*pybar[i] - yi*pyi), \
                            # 1.0,0.0,0.0,1.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 1.0,0.0,0.0,1.0])
                    

                    # if all(y0[:4].imag==0):
                        # print("REAL")

                    # #print('i',i)
                    
                    # sol.set_initial_value(y0.view(dtype=float),t=0.0)
                    # tempar = [0,2*np.linalg.det(np.add(gammaf,gammai))]
                    # successarr = [1]
                    # maxpx = [pxbar[i]]
                    # maxpy = [pybar[i]]
                    # maxp = [abs(pxbar[i]**2 + pybar[i]**2)]

                    
                    # sol.set_f_params(tempar,maxpx,maxpy,maxp,gammaf,S20,potential,dxpotential,dypotential,ddpotential1,ddpotential2,ddpotential3,ddpotential4,gammai,successarr)
                  
                    # phasejump=0
                    # previous = 2*np.linalg.det(np.add(gammaf,gammai))
                    # current = 2*np.linalg.det(np.add(gammaf,gammai))
                    # for tc in range(len(timear)):
                        
                        # if tc>0:
                          # sol.integrate(timear[tc])
                        # result=sol.y.view(dtype=complex)
                        # data[i,tc,:-1] = result

                        # mpp[i] = data[i,tc,5:9].reshape((2,2))
                        # mpq[i] = data[i,tc,9:13].reshape((2,2))
                        # mqp[i] = data[i,tc,13:17].reshape((2,2))
                        # mqq[i] = data[i,tc,17:21].reshape((2,2))
                        # #print(sol.successful())
                        # #print(i,'1',mpq[i])
    
                        # f(timear[tc],sol.y,tempar,maxpx,maxpy,maxp,gammaf,S20,potential,dxpotential,dypotential,ddpotential1,ddpotential2, ddpotential3,ddpotential4,gammai,successarr)
                        
                        # data[i,tc,21] = phasejump#tempar[0]                
                        # successcheck[i] = successarr[0]
                        # maxmomentum[i] = [maxpx[0],maxpy[0],maxp[0]]
                    # #print(data[i][len(timear)-1][0])
                    
                       


#  Final Conditions function is working perfect for x,px,y, py. It is verified to work fine for Sfinbar too, at time t=0.
        
def bramanifold(xfinbar, pxfinbar, yfinbar, pyfinbar, xfin, pxfin, yfin, pyfin, gammaxf, gammayf, Nxr,Nxi,Nyr,Nyi):

   for i in range(Nxr):
        for j in range(Nxi):
            for k in range(Nyr):
                for l in range(Nyi):
                
                    xfin[((i + Nxr*j)*Nyr + k)*Nyi + l] = real((2*gammaxf*xfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l] - 1j*pxfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l]))/(2*(gammaxf))
                    yfin[((i + Nxr*j)*Nyr + k)*Nyi + l] = real((2*gammayf*yfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l] - 1j*pyfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l]))/(2*(gammayf))
                    pxfin[((i + Nxr*j)*Nyr + k)*Nyi + l] = -imag((2*gammaxf*xfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l] - 1j*pxfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l])) 
                    pyfin[((i + Nxr*j)*Nyr + k)*Nyi + l] = -imag((2*gammayf*yfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l] - 1j*pyfinbar[((i + Nxr*j)*Nyr + k)*Nyi + l])) 

    #print(xfin)
    
# bramanifold is working perfectly    
     
def FINCO(xfin, yfin, pxfin, pyfin, xfinbar, pxfinbar, yfinbar, pyfinbar,\
          gammaf,gammaxf,gammayf, Sfinbar, turningpoints, gammaxi, gammayi,\
          mpp,mpq,mqp,mqq, Nxr,Nxi,Nyr,Nyi, widthxr,widthxi,widthyr,widthyi, x,y, wf,S20, magnitude, phaseangle,sigma,J0,successcheck):

    dpxdpy= (widthxi*widthyi)/(Nxi*Nyi)        # 22/05/18 : Watch out for gamma here, the differential changes....
    dxdy = (widthxr*widthyr)/(Nxr*Nyr)
    
    count=0
    for i in range(Nxr*Nxi*Nyr*Nyi):
        #if (successcheck[i] != -1):
            count+=1

            
            j0 = (0.25/(np.linalg.det(gammaf)))*np.linalg.det(2*np.dot(gammaf,mqq[i]) + 2*np.dot(np.dot(gammaf,mqp[i]),S20)\
                       -1j*mpq[i] - 1j*np.dot(mpp[i],S20))
            #print('j0',j0)
            J0[i] = j0
            J = -(0.25/np.linalg.det(gammaf))*abs(j0)**2 + 0j
##            temp0 = (2*np.dot(gammaf,mqq[i]) + 2*np.dot(np.dot(gammaf,mqp[i]),S20)\
##                       -1j*mpq[i] - 1j*np.dot(mpp[i],S20))

            #11/05/18 Check the reason for the definition of temp0, j01
            
            Integrand = -(-0.25)**2*(4/(pi**2*np.linalg.det(gammaf)))**0.75*J/(j0**0.5) # Change if required.
            
##            xgf =  (2*gammaxf/pi)**0.25*exp(-gammaxf*(x-xfin[i])**2 + 1j*pxfin[i]*(x-xfin[i]))
##            ygf =  (2*gammayf/pi)**0.25*exp(-gammayf*(y-yfin[i])**2 + 1j*pyfin[i]*(y-yfin[i]))

            ExponentS = 1j*Sfinbar[i]
            Exponentx = -gammaxf*xfinbar[i]**2 + gammaxf*xfin[i]**2 +\
                      1j*pxfinbar[i]*xfin[i] - 1j*pxfin[i]*xfinbar[i]
            Exponenty = -gammayf*yfinbar[i]**2 + gammayf*yfin[i]**2 +\
                      1j*pyfinbar[i]*yfin[i] - 1j*pyfin[i]*yfinbar[i]
            sigma[i] = Exponentx + Exponenty + ExponentS 
            
            if ( real(sigma[i]) < 0.0):
                 #wf += Integrand*exp(ExponentS+Exponentx+Exponenty)*xgf*ygf*dxdy*dpxdpy*exp(1j*pi*turningpoints[i])  
                 magnitude[i] = abs(Integrand*exp(Exponentx + Exponenty+ ExponentS))
                 phaseangle[i] = np.angle(Integrand*exp(Exponentx + Exponenty+ ExponentS))
            else:
                magnitude[i] = abs(Integrand*exp(Exponentx + Exponenty+ ExponentS))
                phaseangle[i] = np.angle(Integrand*exp(Exponentx + Exponenty+ ExponentS))
    #print('wf',wf)

           

# Note - i : xreal, j : ximag, k : yreal, l : yimag          
def xsubmanifold(arr,Nxr,Nxi,Nyr,Nyi,successcheck):
    submanifold = zeros((Nxr,Nxi)) + 0j
    #print('here')
    for i in range(Nxr):
            for j in range(Nxi):
                #if(successcheck[((i + Nxr*j)*Nyr + Nyr//2)*Nyi + Nyi//2] != -1):
                    submanifold[j][i] = arr[((i + Nxr*j)*Nyr + Nyr//2)*Nyi + Nyi//2]
         
    return (submanifold)
 
def ysubmanifold(arr,Nxr,Nxi,Nyr,Nyi,successcheck):
    submanifold  = zeros((Nyr,Nyi)) + 0j
    
    for k in range(Nyr):
        for l in range(Nyi):
            if(successcheck[((Nxr//2 + Nxr*Nxi//2)*Nyr + k)*Nyi + l] != -1):
                submanifold[l][k] = arr[((Nxr//2 + Nxr*Nxi//2)*Nyr + k)*Nyi + l]
         
    return submanifold

def xyrealsubmanifold(array,Nxr,Nxi,Nyr,Nyi,successcheck):
    submanifold  = zeros((Nxr,Nyr)) + 0j
    for i in range(Nxr):
        for k in range(Nyr):
            if(successcheck[((i + Nxr*Nxi/2)*Nyr + k)*Nyi + Nyi/2] != -1):
                submanifold[k][i] = array[((i + Nxr*Nxi/2)*Nyr + k)*Nyi + Nyi/2]
         
    return submanifold

def xyimagsubmanifold(array,Nxr,Nxi,Nyr,Nyi):
    submanifold  = zeros((Nxi,Nyi)) + 0j
    
    for j in range(Nxi):
           for l in range(Nyi):
                
                  submanifold[l][j] = array[((Nxr/2 + Nxr*j)*Nyr + Nyr/2)*Nyi + l]
         
    return submanifold

def xrealyimagsubmanifold(array,Nxr,Nxi,Nyr,Nyi):
    submanifold  = zeros((Nxr,Nyi)) + 0j
    for i in range(Nxr):
            for l in range(Nyi):
                
                  submanifold[l][i] = array[((i + Nxr*Nxi/2)*Nyr + Nyr/2)*Nyi + l]
         
    return submanifold

def ximagyrealsubmanifold(array,Nxr,Nxi,Nyr,Nyi):
    submanifold  = zeros((Nxi,Nyr)) + 0j
    
    for j in range(Nxi):
        for k in range(Nyr):
            
                submanifold[k][j] = array[((Nxr/2 + Nxr*j)*Nyr + k)*Nyi + Nyi/2]
         
    return submanifold






