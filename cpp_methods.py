
from brian2.units import ms,mV,second
from brian2 import implementation, check_units



# Implementation of synaptic scaling
#
#
@implementation('cpp', code=r'''
   
    double syn_scale(double a, double vATotalMax, double Asum_post, double veta_scaling) {
      
      double a_out;

      if (Asum_post==0.){
          a_out = 0.;
      }
      else{
          a_out = a*(1 + veta_scaling*(vATotalMax/Asum_post-1));
      }

      return a_out;
    } ''')
@check_units(a=1, vATotalMax=1, Asum_post=1, eta_scaling=1, result=1)
def syn_scale(a, vATotalMax, Asum_post, eta_scaling):
    return -1.


# recording of turnover
#
#
@implementation('cpp', code=r'''
    #include <fstream>
    
    double record_turnover(double t, int was_active_before, int should_become_active, int should_stay_active, int syn_active, int i, int j) {

      if (int(was_active_before==0)*should_become_active==1){
          std::ofstream outfile;          
          outfile.open("turnover", std::ios_base::app);
          outfile << 1 << "," << t << "," << i << "," << j << "\n";
      }
      else if (was_active_before*int(should_stay_active==0)){
           std::ofstream outfile;     
           outfile.open("turnover", std::ios_base::app);
           outfile << 0 << "," << t << "," << i << "," << j << "\n";
      }

      return 0.0; // we need to return a dummy value
    } ''')

@check_units(t=second, was_active_before=1, should_become_active=1,
             should_stay_active=1, syn_active=1, i=1, j=1, result=1)
def record_turnover(t, was_active_before, should_become_active,
                    should_stay_active, syn_active, i, j):
    return 0.0


# record spk
#
#
@implementation('cpp', code=r'''
    #include <fstream>
    
    double record_spk(double t, int i, int j, double a, double Apre, double Apost, int syn_active, int preorpost) {

       if (syn_active > 0){
          std::ofstream outfile;          
          outfile.open("spk_register", std::ios_base::app);
          outfile << t << "," << i << "," << j << "," << a << "," << Apre << "," << Apost << "," << preorpost << "\n";
       }

      return 0.0; // we need to return a dummy value
    } ''')

@check_units(t=second, i=1, j=1, a=1, Apre=1, Apost=1, syn_active=1,
             preorpost=1, result=1)
def record_spk(t, i, j, a, Apre, Apost, syn_active, preorpost):
    return 0.0
