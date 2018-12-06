
import numpy as np


def generate_connections(N_tar, N_src, p, same=False):
    ''' 
    connect source to target with probability p
      - if populations SAME, avoid self-connection
      - if not SAME, connect any to any avoididing multiple
    return list of sources i and targets j
    '''
    nums = np.random.binomial(N_tar-1, p, N_src)
    i = np.repeat(np.arange(N_src), nums)
    j = []
    if same:
        for k,n in enumerate(nums):
            j+=list(np.random.choice([*range(k-1)]+[*range(k+1,N_tar)],
                                     size=n, replace=False))
    else:
        for k,n in enumerate(nums):
            j+=list(np.random.choice([*range(N_tar)],
                                     size=n, replace=False))

    return i, np.array(j)


def generate_N_connections(N_tar, N_src, N, same=False):
    ''' 
    connect source to target with N connections per target

    return list of sources i and targets j
    '''
    if same:
        return NotImplementedError

    i = np.array([])
    j = np.repeat(range(N_tar), N)

    for k in range(N_tar):
        srcs = np.random.choice(range(N_src), size=N, replace=False)
        i = np.concatenate((i,srcs))

    i,j = i.astype(int), j.astype(int)
    assert len(i)==len(j)

    return i,j



def generate_full_connectivity(N, same):
    if not same==True:
        raise NotImplementedError
    i = []
    j = []
    for k in range(N):
        i.extend([k]*(N-1))
        targets = list(range(N))
        del targets[k]
        j.extend(targets)

    assert len(i)==len(j)
    return np.array(i), np.array(j)



def extract_lifetimes(turnover_data, N_neuron,  with_starters):
    '''
    turnover data is assumed to be a numpy.array with 
    lines consisting of the four entries
    
      gen/prune, t, i, j     

    where 
      -- gen/prune :: 1 if synapse became active, 
                      0 if synapse became inactive
      -- t         :: simulation time point in seconds(!)
      -- i         :: pre-synaptic neuron index
      -- j         :: post-synaptic neuron index
      
    returns the collected
     -- lifetimes  :: duration from generation until pruning,
                      i.e. synapse generated but not yet 
                      pruned at simulation end are not included!
     -- deathtimes :: like lifetimes, but from death to generation,
                      i.e. time from begining of simulation until 
                      first generation is not included 
    '''

    # lexsort by pre- and post-synaptic indices
    # Example:
    #
    # array([[  1.,   0.,   2., 347.],
    #        [  1.,   0.,   3., 248.],
    #        [  1.,   0.,   4., 145.],
    #        [  1.,   0.,  14., 210.],
    #        [  1.,   0.,  20., 318.]])
    #
    # becomes
    #
    # array([[1.  , 7.19, 0.  , 1.  ],
    #        [1.  , 1.81, 0.  , 2.  ],
    #        [0.  , 1.86, 0.  , 2.  ],
    #        [1.  , 9.28, 0.  , 2.  ],
    #        [1.  , 1.89, 0.  , 3.  ]])


    ind = np.lexsort((turnover_data[:,3],turnover_data[:,2]))
    df_sorted = turnover_data[ind]

    # create result arrays and temporary storage
    lifetimes, deathtimes, current_synapse = [],[], []
    prev_s_id = 0.
    empty_array_count = 0

    for syn_rec in df_sorted:
        # concept:
        #   1. keep collect syn_records as long as pre-synaptic
        #   and post-synpatic neuron completely match (s_id)
        #
        #   2. if new synapse begins (prev_id != id), process the
        #   current collection by sorting it by time and computing
        #   array of differences.
        #
        #   3. odd entries are the lifetimes, even entries are the
        #   deathtimes
        
        s_id = syn_rec[2] * N_neuron + syn_rec[3]
        
        if not prev_s_id==s_id:

            if current_synapse==[]:
                # this can happen only when synapse 0,0 has no event
                empty_array_count += 1
                assert(empty_array_count < 2)

            else:
                c_array = np.array(current_synapse)
                ind = np.argsort(c_array[:,1])
                c_sort = c_array[ind]

                if len(c_sort) == 0:
                    pass
                elif len(c_sort) == 1:
                    # synapses started at beginning of simulation,
                    # died during the simulation and did not grow
                    # again
                    if with_starters and c_sort[0,0]==0:
                        lifetimes.extend([c_sort[0,1]])
                elif len(c_sort) > 1:
   
                    if c_sort[0,0] == 1:
                        # started with become active,
                        # can use previous method
                        life_death = np.diff(c_sort[:,1])

                        # finally add the data
                        lifetimes.extend(life_death[::2])
                        deathtimes.extend(life_death[1::2])

                    elif c_sort[0,0] == 0:
                        #print(c_sort)
                        life_death = np.diff(c_sort[:,1])
                        if with_starters:
                            #print(([c_sort[0,1]]),life_death)
                            life_death = np.concatenate(([c_sort[0,1]],
                                                        life_death))
                            lifetimes.extend(life_death[::2])
                            deathtimes.extend(life_death[1::2])
                        else:
                            lifetimes.extend(life_death[1::2])
                            deathtimes.extend(life_death[::2])
                            
                current_synapse = []
                
        current_synapse.append(list(syn_rec))
        prev_s_id = s_id

    return np.array(lifetimes), np.array(deathtimes)
