
import sys, os, shutil, pickle, powerlaw

from . import standard_params as prm
from . import models as mod
from .utils import generate_connections, generate_full_connectivity, \
                   extract_lifetimes, generate_N_connections

import numpy as np

from brian2.units import ms,mV,second,Hz
from pypet.brian2.parameter import Brian2Parameter, Brian2MonitorResult

from brian2 import NeuronGroup, StateMonitor, SpikeMonitor, run, \
                   PoissonGroup, Synapses, set_device, device, Clock, \
                   defaultclock, prefs, network_operation, Network, \
                   PoissonGroup, PopulationRateMonitor

from .cpp_methods import syn_scale, record_turnover, record_spk

def add_params(tr):

    tr.v_standard_parameter=Brian2Parameter
    tr.v_fast_access=True

    tr.f_add_parameter('netw.N_e', prm.N_e)
    tr.f_add_parameter('netw.N_i', prm.N_i)
    
    tr.f_add_parameter('netw.tau',   prm.tau)
    tr.f_add_parameter('netw.tau_e', prm.tau_e)
    tr.f_add_parameter('netw.tau_i', prm.tau_i)
    tr.f_add_parameter('netw.El',    prm.El)
    tr.f_add_parameter('netw.Ee',    prm.Ee)
    tr.f_add_parameter('netw.Ei',    prm.Ei)
    tr.f_add_parameter('netw.sigma_e', prm.sigma_e)
    tr.f_add_parameter('netw.sigma_i', prm.sigma_i)
    
    tr.f_add_parameter('netw.Vr_e',  prm.Vr_e)
    tr.f_add_parameter('netw.Vr_i',  prm.Vr_i)
    tr.f_add_parameter('netw.Vt_e',  prm.Vt_e)
    tr.f_add_parameter('netw.Vt_i',  prm.Vt_i)

    tr.f_add_parameter('netw.ascale', prm.ascale)
    tr.f_add_parameter('netw.a_ee',  prm.a_ee)
    tr.f_add_parameter('netw.a_ie',  prm.a_ie)
    tr.f_add_parameter('netw.a_ei',  prm.a_ei)
    tr.f_add_parameter('netw.a_ii',  prm.a_ii)

    tr.f_add_parameter('netw.p_ee',  prm.p_ee)
    tr.f_add_parameter('netw.p_ie',  prm.p_ie)
    tr.f_add_parameter('netw.p_ei',  prm.p_ei)
    tr.f_add_parameter('netw.p_ii',  prm.p_ii)

    # Poisson Input
    tr.f_add_parameter('netw.PInp_mode',  prm.PInp_mode)
    tr.f_add_parameter('netw.NPInp',  prm.NPInp)
    tr.f_add_parameter('netw.NPInp_1n',  prm.NPInp_1n)
    tr.f_add_parameter('netw.NPInp_inh',  prm.NPInp_inh)
    tr.f_add_parameter('netw.NPInp_inh_1n',  prm.NPInp_inh_1n)    
    tr.f_add_parameter('netw.a_EPoi',  prm.a_EPoi)
    tr.f_add_parameter('netw.a_IPoi',  prm.a_IPoi)
    tr.f_add_parameter('netw.PInp_rate',  prm.PInp_rate)
    tr.f_add_parameter('netw.PInp_inh_rate',  prm.PInp_inh_rate)
    tr.f_add_parameter('netw.p_EPoi',  prm.p_EPoi)
    tr.f_add_parameter('netw.p_IPoi',  prm.p_IPoi)
    tr.f_add_parameter('netw.poisson_mod',  mod.poisson_mod)

    # STDP
    tr.f_add_parameter('netw.config.stdp_active', prm.stdp_active)
    tr.f_add_parameter('netw.taupre',    prm.taupre)
    tr.f_add_parameter('netw.taupost',   prm.taupost)
    tr.f_add_parameter('netw.Aplus',     prm.Aplus)
    tr.f_add_parameter('netw.Aminus',    prm.Aminus)
    tr.f_add_parameter('netw.amax',      prm.amax)
    tr.f_add_parameter('netw.synEE_rec',      prm.synEE_rec)
    

    # scaling
    tr.f_add_parameter('netw.config.scl_active', prm.scl_active)
    tr.f_add_parameter('netw.ATotalMax',        prm.ATotalMax)
    tr.f_add_parameter('netw.dt_synEE_scaling', prm.dt_synEE_scaling)
    tr.f_add_parameter('netw.eta_scaling', prm.eta_scaling)

    # intrinsic plasticity
    tr.f_add_parameter('netw.config.it_active', prm.it_active)
    tr.f_add_parameter('netw.eta_ip', prm.eta_ip)
    tr.f_add_parameter('netw.it_dt',  prm.it_dt)
    tr.f_add_parameter('netw.h_ip',   prm.h_ip)

    # structural plasticity
    tr.f_add_parameter('netw.prn_thrshld', prm.prn_thrshld)
    tr.f_add_parameter('netw.insert_P',    prm.insert_P)
    tr.f_add_parameter('netw.a_insert',    prm.a_insert)
    tr.f_add_parameter('netw.strct_dt',    prm.strct_dt)
    tr.f_add_parameter('netw.p_inactivate',    prm.p_inactivate)
    
    
    tr.f_add_parameter('netw.mod.condlif_sig',   mod.condlif_sig)
    tr.f_add_parameter('netw.mod.nrnEE_thrshld', mod.nrnEE_thrshld)
    tr.f_add_parameter('netw.mod.nrnEE_reset',   mod.nrnEE_reset)
    tr.f_add_parameter('netw.mod.synEE_mod',     mod.synEE_mod)
    # tr.f_add_parameter('netw.mod.synEE_pre',     mod.synEE_pre)
    # tr.f_add_parameter('netw.mod.synEE_post',    mod.synEE_post)
    tr.f_add_parameter('netw.mod.synEE_p_activate', mod.synEE_p_activate)
    tr.f_add_parameter('netw.mod.synEE_scaling', mod.synEE_scaling)
    tr.f_add_parameter('netw.mod.intrinsic_mod', mod.intrinsic_mod)
    tr.f_add_parameter('netw.mod.strct_mod',     mod.strct_mod)
    tr.f_add_parameter('netw.mod.turnover_rec_mod',     mod.turnover_rec_mod)
    tr.f_add_parameter('netw.mod.strct_mod_thrs',     mod.strct_mod_thrs)
    
    # tr.f_add_parameter('netw.mod.neuron_method', prm.neuron_method)
    # tr.f_add_parameter('netw.mod.synEE_method',  prm.synEE_method)

    #tr.f_add_parameter('netw.sim.preT',  prm.T)
    tr.f_add_parameter('netw.sim.T1',  prm.T1)
    tr.f_add_parameter('netw.sim.T2',  prm.T2)
    tr.f_add_parameter('netw.sim.T3',  prm.T3)
    tr.f_add_parameter('netw.sim.dt', prm.netw_dt)

    tr.f_add_parameter('netw.config.strct_active', prm.strct_active)
    tr.f_add_parameter('netw.config.strct_mode', prm.strct_mode)
    tr.f_add_parameter('netw.rec.turnover_rec', prm.turnover_rec)

    # recording
    tr.f_add_parameter('netw.rec.memtraces_rec', prm.memtraces_rec)
    tr.f_add_parameter('netw.rec.vttraces_rec', prm.vttraces_rec)
    tr.f_add_parameter('netw.rec.getraces_rec', prm.getraces_rec)
    tr.f_add_parameter('netw.rec.gitraces_rec', prm.gitraces_rec)
    tr.f_add_parameter('netw.rec.GExc_stat_dt', prm.GExc_stat_dt)
    tr.f_add_parameter('netw.rec.GInh_stat_dt', prm.GInh_stat_dt)

    tr.f_add_parameter('netw.rec.synee_atraces_rec', prm.synee_atraces_rec)
    tr.f_add_parameter('netw.rec.synee_Apretraces_rec', prm.synee_Apretraces_rec)
    tr.f_add_parameter('netw.rec.synee_Aposttraces_rec', prm.synee_Aposttraces_rec)
    tr.f_add_parameter('netw.rec.n_synee_traces_rec', prm.n_synee_traces_rec)
    tr.f_add_parameter('netw.rec.synEE_stat_dt', prm.synEE_stat_dt)
    tr.f_add_parameter('netw.rec.spks_rec', prm.spks_rec)
    tr.f_add_parameter('netw.synee_a_nrecpoints', prm.synee_a_nrecpoints)
    

    
def run_net(tr):

    # prefs.codegen.target = 'numpy'
    # prefs.codegen.target = 'cython'
    set_device('cpp_standalone', directory='./builds/%.4d'%(tr.v_idx),
               build_on_run=False)

    print("Started process with id ", str(tr.v_idx))

    T = tr.T1 + tr.T2 + tr.T3

    namespace = tr.netw.f_to_dict(short_names=True, fast_access=True)
    namespace['idx'] = tr.v_idx

    defaultclock.dt = tr.netw.sim.dt

    GExc = NeuronGroup(N=tr.N_e, model=tr.condlif_sig,
                       threshold=tr.nrnEE_thrshld,
                       reset=tr.nrnEE_reset, #method=tr.neuron_method,
                       namespace=namespace)
    GInh = NeuronGroup(N=tr.N_i, model=tr.condlif_sig,
                       threshold ='V > Vt',
                       reset='V=Vr_i', #method=tr.neuron_method,
                       namespace=namespace)

    # set initial thresholds fixed, init. potentials uniformly distrib.
    GExc.sigma, GInh.sigma = tr.sigma_e, tr.sigma_i
    GExc.Vt, GInh.Vt = tr.Vt_e, tr.Vt_i
    GExc.V , GInh.V  = np.random.uniform(tr.Vr_e/mV, tr.Vt_e/mV,
                                         size=tr.N_e)*mV, \
                       np.random.uniform(tr.Vr_i/mV, tr.Vt_i/mV,
                                         size=tr.N_i)*mV

    print("need to fix?")
    synEE_pre_mod = mod.synEE_pre
    synEE_post_mod = mod.synEE_post




    if tr.PInp_mode == 'pool':
        PInp = PoissonGroup(tr.NPInp, rates=tr.PInp_rate,
                            namespace=namespace)
        sPN = Synapses(target=GExc, source=PInp, model=tr.poisson_mod,
                       on_pre='ge_post += a_EPoi',
                       namespace=namespace)
        
        sPN_src, sPN_tar = generate_N_connections(N_tar=tr.N_e,
                                                  N_src=tr.NPInp,
                                                  N=tr.NPInp_1n)

    elif tr.PInp_mode == 'indep':
        PInp = PoissonGroup(tr.N_e, rates=tr.PInp_rate,
                        namespace=namespace)
        sPN = Synapses(target=GExc, source=PInp, model=tr.poisson_mod,
                       on_pre='ge_post += a_EPoi',
                       namespace=namespace)
        sPN_src, sPN_tar = range(tr.N_e), range(tr.N_e)


    sPN.connect(i=sPN_src, j=sPN_tar)
    

    
    if tr.PInp_mode == 'pool':
        PInp_inh = PoissonGroup(tr.NPInp_inh, rates=tr.PInp_inh_rate,
                                namespace=namespace)
        sPNInh = Synapses(target=GInh, source=PInp_inh, model=tr.poisson_mod,
                           on_pre='ge_post += a_EPoi',
                           namespace=namespace)
        sPNInh_src, sPNInh_tar = generate_N_connections(N_tar=tr.N_i,
                                                        N_src=tr.NPInp_inh,
                                                        N=tr.NPInp_inh_1n)


    elif tr.PInp_mode == 'indep':

        PInp_inh = PoissonGroup(tr.N_i, rates=tr.PInp_inh_rate,
                            namespace=namespace)
        sPNInh = Synapses(target=GInh, source=PInp_inh, model=tr.poisson_mod,
                          on_pre='ge_post += a_EPoi',
                          namespace=namespace)
        sPNInh_src, sPNInh_tar = range(tr.N_i), range(tr.N_i)

        
    sPNInh.connect(i=sPNInh_src, j=sPNInh_tar)
    
    

    if tr.stdp_active:
        synEE_pre_mod  = '''%s 
                            %s''' %(synEE_pre_mod, mod.synEE_pre_STDP)
        synEE_post_mod = '''%s 
                            %s''' %(synEE_post_mod, mod.synEE_post_STDP)

    
    if tr.synEE_rec:
        synEE_pre_mod  = '''%s 
                            %s''' %(synEE_pre_mod, mod.synEE_pre_rec)
        synEE_post_mod = '''%s 
                            %s''' %(synEE_post_mod, mod.synEE_post_rec)

        
    # E<-E advanced synapse model, rest simple
    SynEE = Synapses(target=GExc, source=GExc, model=tr.synEE_mod,
                     on_pre=synEE_pre_mod, on_post=synEE_post_mod,
                     #method=tr.synEE_method,
                     namespace=namespace)
    SynIE = Synapses(target=GInh, source=GExc, on_pre='ge_post += a_ie',
                     namespace=namespace)
    SynEI = Synapses(target=GExc, source=GInh, on_pre='gi_post += a_ei',
                     namespace=namespace)
    SynII = Synapses(target=GInh, source=GInh, on_pre='gi_post += a_ii',
                     namespace=namespace)

    

    if tr.strct_active:
        sEE_src, sEE_tar = generate_full_connectivity(tr.N_e, same=True)
        SynEE.connect(i=sEE_src, j=sEE_tar)
        SynEE.syn_active = 0

    else:
        srcs_full, tars_full = generate_full_connectivity(tr.N_e, same=True)
        SynEE.connect(i=srcs_full, j=tars_full)
        SynEE.syn_active = 0


    sIE_src, sIE_tar = generate_connections(tr.N_i, tr.N_e, tr.p_ie)
    sEI_src, sEI_tar = generate_connections(tr.N_e, tr.N_i, tr.p_ei)
    sII_src, sII_tar = generate_connections(tr.N_i, tr.N_i, tr.p_ii,
                                            same=True)

    SynIE.connect(i=sIE_src, j=sIE_tar)
    SynEI.connect(i=sEI_src, j=sEI_tar)
    SynII.connect(i=sII_src, j=sII_tar)
        
    tr.f_add_result('sIE_src', sIE_src)
    tr.f_add_result('sIE_tar', sIE_tar)
    tr.f_add_result('sEI_src', sEI_src)
    tr.f_add_result('sEI_tar', sEI_tar)
    tr.f_add_result('sII_src', sII_src)
    tr.f_add_result('sII_tar', sII_tar)


    SynEE.a = tr.a_ee
        
    SynEE.insert_P = tr.insert_P
    SynEE.p_inactivate = tr.p_inactivate


    # make synapse active at beginning
    SynEE.run_regularly(tr.synEE_p_activate, dt=T, when='start',
                            order=-100)
            
        
    # synaptic scaling
    if tr.netw.config.scl_active:
        SynEE.summed_updaters['Asum_post']._clock = Clock(
            dt=tr.dt_synEE_scaling)
        SynEE.run_regularly(tr.synEE_scaling, dt = tr.dt_synEE_scaling,
                            when='end')

    # intrinsic plasticity
    if tr.netw.config.it_active:
        GExc.h_ip = tr.h_ip
        GExc.run_regularly(tr.intrinsic_mod, dt = tr.it_dt, when='end')

    # structural plasticity
    if tr.netw.config.strct_active:
        if tr.strct_mode == 'zero':    
            if tr.turnover_rec:
                strct_mod  = '''%s 
                                %s''' %(tr.strct_mod, tr.turnover_rec_mod)
            else:
                strct_mod = tr.strct_mod
                
            SynEE.run_regularly(strct_mod, dt = tr.strct_dt, when='end')
           
        elif tr.strct_mode == 'thrs':
            if tr.turnover_rec:
                strct_mod_thrs  = '''%s 
                                %s''' %(tr.strct_mod_thrs, tr.turnover_rec_mod)
            else:
                strct_mod_thrs = tr.strct_mod_thrs
                
            SynEE.run_regularly(strct_mod_thrs, dt = tr.strct_dt, when='end')


            
    # -------------- recording ------------------        

    #run(tr.sim.preT)

    GExc_recvars = []
    if tr.memtraces_rec:
        GExc_recvars.append('V')
    if tr.vttraces_rec:
        GExc_recvars.append('Vt')
    if tr.getraces_rec:
        GExc_recvars.append('ge')
    if tr.gitraces_rec:
        GExc_recvars.append('gi')

    GInh_recvars = GExc_recvars
    
    GExc_stat = StateMonitor(GExc, GExc_recvars, record=[0,1,2],
                             dt=tr.GExc_stat_dt)
    GInh_stat = StateMonitor(GInh, GInh_recvars, record=[0,1,2],
                             dt=tr.GInh_stat_dt)
    

    SynEE_recvars = []
    if tr.synee_atraces_rec:
        SynEE_recvars.append('a')
    if tr.synee_Apretraces_rec:
        SynEE_recvars.append('Apre')
    if tr.synee_Aposttraces_rec:
        SynEE_recvars.append('Apost')

    SynEE_stat = StateMonitor(SynEE, SynEE_recvars,
                              record=range(tr.n_synee_traces_rec),
                              when='end', dt=tr.synEE_stat_dt)

    
    GExc_spks = SpikeMonitor(GExc)    
    GInh_spks = SpikeMonitor(GInh)
    PInp_spks = SpikeMonitor(PInp)

    GExc_rate = PopulationRateMonitor(GExc)
    GInh_rate = PopulationRateMonitor(GInh)
    PInp_rate = PopulationRateMonitor(PInp)

    
    SynEE_a = StateMonitor(SynEE, ['a','syn_active'],
                           record=range(tr.N_e*(tr.N_e-1)),
                           dt=(tr.sim.T2/tr.synee_a_nrecpoints),
                           when='end', order=100)


    net = Network(GExc, GInh, PInp, sPN, sPNInh, SynEE, SynEI, SynIE, SynII,
                  GExc_stat, GInh_stat, SynEE_stat, SynEE_a,
                  GExc_spks, GInh_spks, PInp_spks, GExc_rate, GInh_rate,
                  PInp_rate, PInp_inh)


       
    net.run(tr.sim.T1, report='text')

    recorders      = [GExc_spks, GInh_spks, PInp_spks, SynEE_stat,
                      GExc_stat, GInh_stat]
    rate_recorders = [GExc_rate, GInh_rate, PInp_rate]
    
    for rcc in recorders:
        rcc.active=False
    for rcc in rate_recorders:
        rcc.active=False


    # print('''Hack solution: Simulate single timestep 
    #          to avoid missing simulation chunks''')
    # net.run(tr.dt)
        
    for time_step in range(int(tr.sim.T2/(100*second))):
        net.run(100*second, report='text')
        
    recorders = [SynEE_stat, GExc_stat, GInh_stat, GExc_rate, GInh_rate,
                 PInp_rate]
    for rcc in recorders:
        rcc.active=True
    for rcc in rate_recorders:
        rcc.active=True

    if tr.spks_rec:
        GExc_spks.active=True
        GInh_spks.active=True
        # PInp_spks.active=True

    net.run(tr.sim.T3, report='text')
    SynEE_a.record_single_timestep()

    device.build(directory='builds/%.4d'%(tr.v_idx), clean=True)


    # save monitors as raws in build directory
    raw_dir = 'builds/%.4d/raw/'%(tr.v_idx)
    
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    with open(raw_dir+'namespace.p','wb') as pfile:
        pickle.dump(namespace,pfile)   

    with open(raw_dir+'gexc_stat.p','wb') as pfile:
        pickle.dump(GExc_stat.get_states(),pfile)   
    with open(raw_dir+'ginh_stat.p','wb') as pfile:
        pickle.dump(GInh_stat.get_states(),pfile)   
        
    with open(raw_dir+'synee_stat.p','wb') as pfile:
        pickle.dump(SynEE_stat.get_states(),pfile)   
    with open(raw_dir+'synee_a.p','wb') as pfile:
        pickle.dump(SynEE_a.get_states(),pfile)   

    with open(raw_dir+'gexc_spks.p','wb') as pfile:
        pickle.dump(GExc_spks.get_states(),pfile)   
    with open(raw_dir+'ginh_spks.p','wb') as pfile:
        pickle.dump(GInh_spks.get_states(),pfile)
    with open(raw_dir+'pinp_spks.p','wb') as pfile:
        pickle.dump(PInp_spks.get_states(),pfile)

    with open(raw_dir+'gexc_rate.p','wb') as pfile:
        pickle.dump(GExc_rate.get_states(),pfile)
        pickle.dump(GExc_rate.smooth_rate(width=25*ms),pfile)   
    with open(raw_dir+'ginh_rate.p','wb') as pfile:
        pickle.dump(GInh_rate.get_states(),pfile)
        pickle.dump(GInh_rate.smooth_rate(width=25*ms),pfile)   
    with open(raw_dir+'pinp_rate.p','wb') as pfile:
        pickle.dump(PInp_rate.get_states(),pfile)
        pickle.dump(PInp_rate.smooth_rate(width=25*ms),pfile)   


    # ----------------- add raw data ------------------------
    fpath = 'builds/%.4d/'%(tr.v_idx)

    from pathlib import Path

    Path(fpath+'turnover').touch()
    turnover_data = np.genfromtxt(fpath+'turnover',delimiter=',')    
    os.remove(fpath+'turnover')

    with open(raw_dir+'turnover.p','wb') as pfile:
        pickle.dump(turnover_data,pfile)   
    
    Path(fpath+'spk_register').touch()
    spk_register_data = np.genfromtxt(fpath+'spk_register',delimiter=',')
    os.remove(fpath+'spk_register')
    
    with open(raw_dir+'spk_register.p','wb') as pfile:
        pickle.dump(spk_register_data,pfile)


    # ---------------- create the powerlaw fit ---------------

    # if len(turnover_data) > 10:
    
    #     _lt, _dt = extract_lifetimes(turnover_data, tr.N_e,
    #                                  with_starters=True)
    #     life_t, death_t = _lt*second, _dt*second

    #     if len(life_t)>25:                                         
    #         fit_wstart = powerlaw.Fit(life_t/ms, discrete=True)

            
    #     _lt, _dt = extract_lifetimes(turnover_data, tr.N_e,
    #                                  with_starters=False)
    #     life_t, death_t = _lt*second, _dt*second

        
    #     if len(life_t)>25:                                         
    #         fit_nostart = powerlaw.Fit(life_t/ms, discrete=True)
            
    #         with open(raw_dir+'powerlaw_fit.p', 'wb') as pfile:
    #             pickle.dump({'fit_wstart': fit_wstart,
    #                          'fit_nostart': fit_nostart}, pfile)
                        


    # ---------------- plot results --------------------------

    #os.chdir('./analysis/file_based/')

    from analysis.overview_fb import overview_figure
    overview_figure('builds/%.4d'%(tr.v_idx), namespace)

    from analysis.synw_fb import synw_figure
    synw_figure('builds/%.4d'%(tr.v_idx), namespace)

    from analysis.synw_log_fb import synw_log_figure
    synw_log_figure('builds/%.4d'%(tr.v_idx), namespace)

    from analysis.turnover_fb import turnover_figure
    turnover_figure('builds/%.4d'%(tr.v_idx), namespace, fit=False)

    from analysis.turnover_fb import turnover_figure
    turnover_figure('builds/%.4d'%(tr.v_idx), namespace, fit=True)



    # -----------------  clean up  ---------------------------
    shutil.rmtree('builds/%.4d/results/'%(tr.v_idx))
                        
            
