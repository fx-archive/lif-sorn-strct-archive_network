
from brian2.units import *

N_e = 400
N_i = int(0.2*N_e)

tau = 20*ms                 # membrane time constant
tau_e = 3*ms                # EPSP time constant
tau_i = 5*ms                # IPSP time constant
El = -60*mV                 # resting value
Ee = 0*mV                   # reversal potential Excitation 
Ei = -80*mV                 # reversal potential Inhibition
sigma_e = 4.0**0.5 *mV        # noise amplitude
sigma_i = 4.0**0.5 *mV

Vr_e = -60*mV
Vr_i = -60*mV
Vt_e = -57.5*mV
Vt_i = -58*mV

ascale = 1.0
a_ee = 1.5 
a_ie = 1.5 
a_ei = -1.5 
a_ii = -1.5 

p_ee = 0.1 
p_ie = 0.1
p_ei = 0.1
p_ii = 0.5

taupre = 15*ms
taupost = 30*ms
Aplus = 15*0.001
Aminus = -7.5*0.001
amax = 40*0.001

# Poisson
PInp_mode = 'indep' #pool
NPInp = 400
NPInp_1n = 10
NPInp_inh = 80
NPInp_inh_1n = 10
PInp_rate = 10*Hz
PInp_inh_rate = 10*Hz
a_EPoi = 0.005
a_IPoi = 0.
p_EPoi = 0.2
p_IPoi = 0.1

#STDP
stdp_active = 1

synEE_rec = 1

ATotalMax = 40.*0.001

# scaling
scl_active = 0
dt_synEE_scaling = 10*ms
eta_scaling = 0.2

# intrinsic plasticity
it_active = 0
eta_ip = 0.2*mV*ms
it_dt = 10*ms
h_ip = 3*Hz

# structural plasticity
strct_active = 0
strct_mode = 'zero'
prn_thrshld = 0.001 * ATotalMax
insert_P = 0.001
strct_dt = 10*ms
a_insert = 0.01 * ATotalMax
p_inactivate = 0.25


#preT  = 100*second
T1 = 5*second
T2 = 5*second
T3 = 5*second
netw_dt = 0.1*ms


# neuron_method = 'euler'
# synEE_method = 'euler'


# recording
memtraces_rec = 1
vttraces_rec = 1
getraces_rec = 1
gitraces_rec = 1
GExc_stat_dt = 0.1*ms
GInh_stat_dt = 0.1*ms

synee_atraces_rec = 1
synee_Apretraces_rec = 1
synee_Aposttraces_rec = 1
n_synee_traces_rec = 20
synEE_stat_dt = 0.1*ms

turnover_rec = 0
spks_rec = 0
synee_a_nrecpoints = 10
