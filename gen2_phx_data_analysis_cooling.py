# -*- coding: utf-8 -*-
"""Gen2 PHX Data Analysis_Cooling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dpvXXofoaUeBYDQ1h_M0OWOFpU7wMcKE
"""

# Commented out IPython magic to ensure Python compatibility.
!pip install CoolProp
!pip install --upgrade gspread
from IPython.display import clear_output
clear_output()

# standard python packages:

# %matplotlib inline
import numpy as np
import math
import operator
from numpy import *
import scipy.linalg
from scipy.integrate import odeint
from scipy.optimize import fsolve
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import time
from IPython.display import HTML, display
import csv
from google.colab import files
from google.colab import drive
from google.colab import auth
auth.authenticate_user()

import warnings
from IPython.display import Image
from numpy import interp
import os
from scipy import signal
# %matplotlib inline
import pandas as pd
import gspread
from oauth2client.client import GoogleCredentials

import CoolProp.CoolProp as CP
from CoolProp.Plots import PropertyPlot
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI


drive.mount('/content/drive')

# # all python scripts and outputs will be saved in the following directory
directory = "/content/drive/My Drive/Treau Team/Engineering/Pythons/"

data_col_names1 = ['Time_stamp','Glycol_Pump_Speed','Log_intervals_s','Glycol_concentration','Air_DP_kPa','Avg_Air_Tin','Air_RHin','Avg_Air_Tout','Air_RHout','Liquid_DP_kPa','Liquid_LPM','Liquid_Tin_TC','Liquid_Tout_TC','T_resvr','LiquidQ_TC','AirQ','Air_Tout1','Air_Tout2','Air_Tout3','Air_Tout4','Air_Tout5','Air_Tout6','Air_Tout7','Air_Tout8','Air_Tout9','AirFlow_CFM','Air_TinRTD','Air_ToutRTD','Liquid_Tin_RTD','Liquid_Tout_RTD','DeltaT_TC','DeltaT_RTD','LiquidQ_RTD']

data1 = pd.read_table('/content/drive/My Drive/Gradient Team/Thermal Engineering/Polymer Heat Exchangers/Wind Tunnel Testing/Multilayer Material Gen2 PHX Testing 2022/Design P6-58 Pouches/07072022_4p75psi_Cooling/07072022_P6_coolingSS33p2CFM4p75psi.txt',sep = ',',names = data_col_names1)
data1 = pd.DataFrame(data1)#.dropna()
data2 = pd.read_table('/content/drive/My Drive/Gradient Team/Thermal Engineering/Polymer Heat Exchangers/Wind Tunnel Testing/Multilayer Material Gen2 PHX Testing 2022/Design P6-58 Pouches/07072022_4p75psi_Cooling/07072022_P6_coolingSS42p1CFM4p75psi.txt',sep = ',',names = data_col_names1)
data2 = pd.DataFrame(data2)#.dropna()
data3 = pd.read_table('/content/drive/My Drive/Gradient Team/Thermal Engineering/Polymer Heat Exchangers/Wind Tunnel Testing/Multilayer Material Gen2 PHX Testing 2022/Design P6-58 Pouches/07072022_4p75psi_Cooling/07072022_P6_coolingSS51p5CFM4p75psi.txt',sep = ',',names = data_col_names1)
data3 = pd.DataFrame(data3)#.dropna()
data4 = pd.read_table('/content/drive/My Drive/Gradient Team/Thermal Engineering/Polymer Heat Exchangers/Wind Tunnel Testing/Multilayer Material Gen2 PHX Testing 2022/Design P6-58 Pouches/07072022_4p75psi_Cooling/07072022_P6_coolingSS61p1CFM4p75psi.txt',sep = ',',names = data_col_names1)
data4 = pd.DataFrame(data4)#.dropna()
data5 = pd.read_table('/content/drive/My Drive/Gradient Team/Thermal Engineering/Polymer Heat Exchangers/Wind Tunnel Testing/Multilayer Material Gen2 PHX Testing 2022/Design P6-58 Pouches/07072022_4p75psi_Cooling/07072022_P6_coolingSS68p0CFM4p75psi.txt',sep = ',',names = data_col_names1)
data5 = pd.DataFrame(data5)#.dropna()

datafiles = [data1,data2,data3,data4,data5]
for datafile in datafiles:
  ## User Defined quantities
  Pouch_count = 58
  Pouch_active_length = np.mean([0.362,0.357])
  #Pouch_active_length = np.mean([0.286,0.283])
  Pouch_active_width = 0.03259
  #Pouch_active_width = 0.064
  Pouch_active_area = 2*(Pouch_active_length*Pouch_active_width)
  PHX_active_area = Pouch_active_area*Pouch_count
  Face_Area = Pouch_active_length*np.mean([0.077,0.078])

  atm_P = 101375
  glycol = 'INCOMP::MPG-38%'

  ## Quantities from txt files
  Avg_Airflow_CFM = np.mean(np.array(datafile.AirFlow_CFM[1::]).astype(np.float))
  STD_Airflow_CFM = np.std(np.array(datafile.AirFlow_CFM[1::]).astype(np.float))
  Avg_Airflow_SI = 0.00047194745*Avg_Airflow_CFM
  STD_Airflow_SI = 0.00047194745*STD_Airflow_CFM
  Avg_glycol_conc  = np.mean(np.array(datafile.Glycol_concentration[1::]).astype(np.float))
  STD_glycol_conc = np.std(np.array(datafile.Glycol_concentration[1::]).astype(np.float))


  Avg_Air_Tin =  np.mean(np.array(datafile.Avg_Air_Tin[1::]).astype(np.float))
  STD_Air_Tin = np.std(np.array(datafile.Avg_Air_Tin[1::]).astype(np.float))
  Avg_Air_RHin = np.mean(np.array(datafile.Air_RHin[1::]).astype(np.float))
  STD_Air_RHin = np.std(np.array(datafile.Air_RHin[1::]).astype(np.float))
  omega_in = HAPropsSI('W','T',Avg_Air_Tin+273.15,'P',atm_P,'R',Avg_Air_RHin/100)
  p_w_in = HAPropsSI('P_w','T',Avg_Air_Tin+273.15,'P',atm_P,'R',Avg_Air_RHin/100)
  h_a_in = PropsSI('H','T',Avg_Air_Tin+273.15,'P',atm_P,'Air')
  h_w_a_in = PropsSI('H','T',Avg_Air_Tin+273.15,'P',p_w_in,'Water')


  Avg_Air_Tout =  np.mean(np.array(datafile.Avg_Air_Tout[1::]).astype(np.float))
  STD_Air_Tout = np.std(np.array(datafile.Avg_Air_Tout[1::]).astype(np.float))
  Avg_Air_RHout = np.mean(np.array(datafile.Air_RHout[1::]).astype(np.float))
  STD_Air_RHout = np.std(np.array(datafile.Air_RHout[1::]).astype(np.float))
  omega_out = HAPropsSI('W','T',Avg_Air_Tout+273.15,'P',atm_P,'R',Avg_Air_RHout/100)
  p_w_out = HAPropsSI('P_w','T',Avg_Air_Tout+273.15,'P',atm_P,'R',Avg_Air_RHout/100)
  h_a_out = PropsSI('H','T',Avg_Air_Tout+273.15,'P',atm_P,'Air')
  h_w_a_out = PropsSI('H','T',Avg_Air_Tout+273.15,'P',p_w_out,'Water')

  Avg_Liquid_LPM =  np.mean(np.array(datafile.Liquid_LPM[1::]).astype(np.float))
  STD_Liquid_LPM = np.std(np.array(datafile.Liquid_LPM[1::]).astype(np.float))
  Avg_LiquidFLW_SI = Avg_Liquid_LPM*0.0000166667
  STD_LiquidFLW_SI = STD_Liquid_LPM*0.0000166667
  Avg_AirFaceV_SI = Avg_Airflow_SI/Face_Area
  STD_AirFaceV_SI = STD_Airflow_SI/Face_Area

  ## TC Liquid Temp values:
  Avg_Liquid_Tin_TC =  np.mean(np.array(datafile.Liquid_Tin_TC[1::]).astype(np.float))
  STD_Liquid_Tin_TC = np.std(np.array(datafile.Liquid_Tin_TC[1::]).astype(np.float))
  Avg_Liquid_Tout_TC =  np.mean(np.array(datafile.Liquid_Tout_TC[1::]).astype(np.float))
  STD_Liquid_Tout_TC = np.std(np.array(datafile.Liquid_Tout_TC[1::]).astype(np.float))
  Avg_LiquidT_TC = np.mean([Avg_Liquid_Tin_TC,Avg_Liquid_Tout_TC])

  h_w_lTC = PropsSI('H','T',Avg_LiquidT_TC+273.15,'Q',0,'Water') # Liquid water condensed on HX - assume it condenses at the average glycol temperature
  h_l_inTC = PropsSI('H','T',Avg_LiquidT_TC+273.15,'P',atm_P,glycol)
  h_l_outTC = PropsSI('H','T',Avg_LiquidT_TC+273.15,'P',atm_P,glycol)

  ## RTD Liquid Temp values:
  Avg_Liquid_Tin_RTD =  np.mean(np.array(datafile.Liquid_Tin_RTD[1::]).astype(np.float))
  STD_Liquid_Tin_RTD = np.std(np.array(datafile.Liquid_Tin_RTD[1::]).astype(np.float))
  Avg_Liquid_Tout_RTD =  np.mean(np.array(datafile.Liquid_Tout_RTD[1::]).astype(np.float))
  STD_Liquid_Tout_RTD = np.std(np.array(datafile.Liquid_Tout_RTD[1::]).astype(np.float))
  Avg_LiquidT_RTD = np.mean([Avg_Liquid_Tin_RTD,Avg_Liquid_Tout_RTD])
  
  h_w_lRTD = PropsSI('H','T',Avg_LiquidT_RTD+273.15,'Q',0,'Water') # Liquid water condensed on HX - assume it condenses at the average glycol temperature
  h_l_inRTD = PropsSI('H','T',Avg_LiquidT_RTD+273.15,'P',atm_P,glycol)
  h_l_outRTD = PropsSI('H','T',Avg_LiquidT_RTD+273.15,'P',atm_P,glycol)


  atm_P = 101375

  ## AIR PROPERTIES TC
  Avg_Air_T = (Avg_Air_Tin+Avg_Air_Tout)/2
  deltaTAir = Avg_Air_Tout-Avg_Air_Tin
  CpAir = (PropsSI('C','T',Avg_Air_T+273.15,'P',atm_P,'Air'))/1000
  rhoAir = PropsSI('D','T',Avg_Air_T+273.15,'P',atm_P,'Air')
  P_Air = ((rhoAir*Avg_Airflow_SI*(h_a_out - h_a_in) + rhoAir*Avg_Airflow_SI*(omega_out*h_w_a_out - omega_in*h_w_a_in) + rhoAir*Avg_Airflow_SI*(omega_in - omega_out)*h_w_lRTD)/1000)#rhoAir*CpAir*Avg_Airflow_SI*deltaTAir


  ## AIR PROPERTIES RTD

  ## LIQUID PROPERTIES TC
  Avg_Liquid_TTC = (Avg_Liquid_Tin_TC+Avg_Liquid_Tout_TC)/2
  deltaTLiquidTC = Avg_Liquid_Tin_TC-Avg_Liquid_Tout_TC
  CpLiquidTC = PropsSI('C','T',Avg_Liquid_TTC+273.15,'P',atm_P,glycol)/1000
  rhoLiquidTC = PropsSI('D','T',Avg_Liquid_TTC+273.15,'P',atm_P,glycol)
  P_LiquidTC = rhoLiquidTC*CpLiquidTC*Avg_LiquidFLW_SI*deltaTLiquidTC
  Av_PowerTC = (P_LiquidTC+P_Air)/2




  ## LIQUID PROPERTIES RTD
  Avg_Liquid_TRTD = (Avg_Liquid_Tin_RTD+Avg_Liquid_Tout_RTD)/2
  deltaTLiquidRTD = Avg_Liquid_Tin_RTD-Avg_Liquid_Tout_RTD
  CpLiquidRTD = PropsSI('C','T',Avg_Liquid_TRTD+273.15,'P',atm_P,glycol)/1000
  rhoLiquidRTD = PropsSI('D','T',Avg_Liquid_TRTD+273.15,'P',atm_P,glycol)
  P_LiquidRTD = rhoLiquidRTD*CpLiquidRTD*Avg_LiquidFLW_SI*deltaTLiquidRTD
  Av_PowerRTD = (P_LiquidRTD+P_Air)/2


  ## Power Differences for TCs vs RTDs
  PercDiff_PowerTC = np.abs(((P_LiquidTC-P_Air)/((P_LiquidTC+P_Air)/2))*100)
  PercDiff_PowerRTD = np.abs(((P_LiquidRTD-P_Air)/((P_LiquidRTD+P_Air)/2))*100)

  print('Perc diff TC: ',PercDiff_PowerTC)
  print('Perc diff RTD',PercDiff_PowerRTD)

  ## TC LMTD Calculations:
  DeltaTs_TC = (Avg_Liquid_Tin_TC-Avg_Air_Tout)-(Avg_Liquid_Tout_TC-Avg_Air_Tin)
  LnT1_TC = np.log(abs(Avg_Liquid_Tin_TC-Avg_Air_Tout))
  LnT2_TC = np.log(abs(Avg_Liquid_Tout_TC-Avg_Air_Tin))
  LMTD_Counter_TC = DeltaTs_TC/(LnT1_TC-LnT2_TC)
  UA1_TC = (P_LiquidTC*1000)/LMTD_Counter_TC
  U1_TC = UA1_TC/PHX_active_area
  UA2_TC = (P_Air*1000)/LMTD_Counter_TC
  U2_TC = UA2_TC/PHX_active_area
  print('UA Liquid TC: ',UA1_TC)
  print('U Liquid TC: ',U1_TC)
  print('UA Air TC: ',UA2_TC)
  print('U Air TC: ',U2_TC)

  ## RTD LMTD Calculations:
  DeltaTs_RTD = (Avg_Liquid_Tin_RTD-Avg_Air_Tout)-(Avg_Liquid_Tout_RTD-Avg_Air_Tin)
  LnT1_RTD = np.log(abs(Avg_Liquid_Tin_RTD-Avg_Air_Tout))
  LnT2_RTD = np.log(abs(Avg_Liquid_Tout_RTD-Avg_Air_Tin))
  LMTD_Counter_RTD = DeltaTs_RTD/(LnT1_RTD-LnT2_RTD)
  UA1_RTD = (P_LiquidRTD*1000)/LMTD_Counter_RTD
  U1_RTD = UA1_RTD/PHX_active_area
  UA2_RTD = (P_Air*1000)/LMTD_Counter_RTD
  U2_RTD = UA2_RTD/PHX_active_area
  print('UA Liquid RTD: ',UA1_RTD)
  print('U Liquid RTD: ',U1_RTD)
  print('UA Air RTD: ',UA2_RTD)
  print('U Air RTD: ',U2_RTD)
  print('Air Face Velocity: ',Avg_AirFaceV_SI)