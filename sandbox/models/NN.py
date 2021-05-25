# -*- coding: utf-8 -*-

import casadi as cs
import matplotlib.pyplot as plt
import numpy as np


class RBFLPV():
    """
    
    """

    def __init__(self,dim_u,dim_x,dim_y,dim_theta,initial_params=None,
                 name='RBF_LPV'):
        
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_theta = dim_theta
        self.name = name
        
        self.Initialize(initial_params)

    def Initialize(self,initial_params=None):
            
            # For convenience of notation
            dim_u = self.dim_u
            dim_x = self.dim_x 
            dim_y = self.dim_y   
            dim_theta = self.dim_theta
            name = self.name
            
            # Define input, state and output vector
            u = cs.MX.sym('u',dim_u,1)
            x = cs.MX.sym('x',dim_x,1)
            y = cs.MX.sym('y',dim_y,1)
                        
            # Define Model Parameters
            A = cs.MX.sym('A',dim_x,dim_x,dim_theta)
            B = cs.MX.sym('B',dim_x,dim_u,dim_theta)
            C = cs.MX.sym('C',dim_y,dim_x,dim_theta)
            O = cs.MX.sym('O',dim_x,1,dim_theta)
            c_u = cs.MX.sym('c_u',dim_u,1,dim_theta)
            c_x = cs.MX.sym('c_x',dim_x,1,dim_theta)
            w_u = cs.MX.sym('w_u',dim_u,1,dim_theta)
            w_x = cs.MX.sym('w_x',dim_x,1,dim_theta)
                       
            # Define Model Equations, loop over all local models
            x_new = 0
            r_sum = 0
            
            for loc in range(0,len(A)):
                
                c = cs.vertcat(c_x[loc],c_u[loc])
                w = cs.vertcat(w_x[loc],w_u[loc])
                
                r = RBF(cs.vertcat(x,u),c,w)
                
                x_new = x_new + \
                r * (cs.mtimes(A[loc],x) + cs.mtimes(B[loc],u) + O[loc])
                
                r_sum = r_sum + r
            
            x_new = x_new / (r_sum + 1e-20)
            
            y_new = 0
            r_sum = 0
            
            for loc in range(0,len(A)):
                
                c = cs.vertcat(c_x[loc],c_u[loc])
                w = cs.vertcat(w_x[loc],w_u[loc])
                
                r = RBF(cs.vertcat(x,u),c,w)
                
                y_new = y_new + r * (cs.mtimes(C[loc],x_new))
                
                r_sum = r_sum + r
                
            y_new = y_new / (r_sum + 1e-20)
            
            # Define Casadi Function
           
            # Define input of Casadi Function and save all parameters in 
            # dictionary
                        
            input = [x,u]
            input_names = ['x','u']
            
            Parameters = {}
            
            # Add local model parameters
            for loc in range(0,len(A)):
                input.extend([A[loc],B[loc],C[loc],O[loc],c_u[loc],c_x[loc],w_u[loc],
                              w_x[loc]])    
                i=str(loc)
                input_names.extend(['A'+i,'B'+i,'C'+i,'O'+i,'c_u'+i,'c_x'+i,'w_u'+i,
                                    'w_x'+i])
                
                Parameters['A'+i] = np.random.rand(dim_x,dim_x)
                Parameters['B'+i] = np.random.rand(dim_x,dim_u)
                Parameters['C'+i] = np.random.rand(dim_y,dim_x)
                Parameters['O'+i] = np.random.rand(dim_x,1)
                Parameters['c_u'+i] = np.random.rand(dim_u,1)
                Parameters['c_x'+i] = np.random.rand(dim_x,1)
                Parameters['w_u'+i] = np.random.rand(dim_u,1)
                Parameters['w_x'+i] = np.random.rand(dim_x,1)
                
            self.Parameters=Parameters    
            
            # Initialize if inital parameters are given
            if initial_params is not None:
                for param in initial_params.keys():
                    self.Parameters[param] = initial_params[param]
            
            
            
            output = [x_new,y_new]
            output_names = ['x_new','y_new']  
            
            self.Function = cs.Function(name, input, output, input_names,output_names)

            # Calculate affine parameters
            # theta = XXX
            
            # self.AffineParameters = cs.Function('AffineParameters',input,
            #                                     [theta],input_names,['theta'])
            
            return None
    
    
    def AffineStateSpaceMatrices(self,theta):
        """
        A function that returns the state space matrices at a given value 
        for theta
        """
        # A_0 = self.Parameters['A_0']
        # B_0 = self.Parameters['B_0']
        # C_0 = self.Parameters['C_0']
    
        # A_lpv = self.Parameters['A_0']
        # B_lpv = self.Parameters['B_lpv']
        # C_lpv = self.Parameters['C_lpv']  
    
        # W_A = self.Parameters['W_A']
        # W_B = self.Parameters['W_B']
        # W_C = self.Parameters['W_C']      
    
        # theta_A = theta[0:self.dim_thetaA]
        # theta_B = theta[self.dim_thetaA:self.dim_thetaA+self.dim_thetaB]
        # theta_C = theta[self.dim_thetaA+self.dim_thetaB:self.dim_thetaA+
        #                 self.dim_thetaB+self.dim_thetaC]
        
        # A = A_0 + np.linalg.multi_dot([A_lpv,np.diag(theta_A),W_A])
        # B = B_0 + np.linalg.multi_dot([B_lpv,np.diag(theta_B),W_B])
        # C = C_0 + np.linalg.multi_dot([C_lpv,np.diag(theta_C),W_C]) 
        
        return None #A,B,C

    def AffineParameters(self,x0,u0):
        '''

        '''
        
        params = self.Parameters
        
        params_new = []
            
        for name in self.AffineParameters.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        theta = self.AffineParameters(x0,u0,*params_new) 

        return theta   
    
    
    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new)     
                              
        return x1,y1
   
    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''

        x = []
        y = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = self.OneStepPrediction(x[k],u[[k],:],params)
            x.append(x_new)
            y.append(y_new)
        
        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T
       
        return x,y


class RehmerLPV_new():


    def __init__(self,dim_u,dim_x,dim_y,dim_thetaA=0,dim_thetaB=0,dim_thetaC=0,
                 NN_1_dim=[],NN_2_dim=[],NN_3_dim=[],NN1_act=[],NN2_act=[],
                 NN3_act=[], initial_params=None,name=None):
        '''
        Initializes the model structure by Rehmer et al. 2021.
        dim_u: int, dimension of the input vector
        dim_x: int, dimension of the state vector
        dim_y: int, dimension of the output vector
        dim_thetaA: int, dimension of the affine parameter associated with the 
        system matrix
        dim_thetaB: int, dimension of the affine parameter associated with the 
        input matrix
        dim_thetaC: int, dimension of the affine parameter associated with the 
        output matrix
        NN_1_dim: list, each entry is an integer specifying the number of neurons 
        in the hidden layers of the NN associated with the system matrix
        NN_2_dim: list, each entry is an integer specifying the number of neurons 
        in the hidden layers of the NN associated with the input matrix      
        NN_3_dim: list, each entry is an integer specifying the number of neurons 
        in the hidden layers of the NN associated with the system matrix     
        
        activation: list, each entry is an integer, that specifies the
        activation function used in the layers of the NNs
                    0 --> tanh()
                    1 --> logistic()
                    2 --> linear()
        initial_params: dict, dictionary specifying the inital parameter values
        name: str, specifies name of the model
        '''
        
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_thetaA = dim_thetaA
        self.dim_thetaB = dim_thetaB
        self.dim_thetaC = dim_thetaC
        self.NN_1_dim = NN_1_dim
        self.NN_2_dim = NN_2_dim
        self.NN_3_dim = NN_3_dim
        self.NN1_act = NN1_act
        self.NN2_act = NN2_act
        self.NN3_act = NN3_act
        self.name = name
        
        self.Initialize(initial_params)

    def Initialize(self,initial_params=None):
            
        # For convenience of notation
        dim_u = self.dim_u
        dim_x = self.dim_x 
        dim_y = self.dim_y   
        dim_thetaA = self.dim_thetaA
        dim_thetaB = self.dim_thetaB
        dim_thetaC = self.dim_thetaC
        NN_1_dim = self.NN_1_dim
        NN_2_dim = self.NN_2_dim
        NN_3_dim = self.NN_3_dim    
        NN1_act = self.NN1_act
        NN2_act = self.NN2_act
        NN3_act = self.NN3_act
       
        name = self.name
        
        # Define input, state and output vector
        u = cs.MX.sym('u',dim_u,1)
        x = cs.MX.sym('x',dim_x,1)
        y = cs.MX.sym('y',dim_y,1)
        
        # Define Model Parameters for the linear part
        A_0 = cs.MX.sym('A_0',dim_x,dim_x)
        B_0 = cs.MX.sym('B_0',dim_x,dim_u)
        C_0 = cs.MX.sym('C_0',dim_y,dim_x)
        
        # Define Model Parameters for the time varying part by Lachhab
        A_1 = cs.MX.sym('A_1',dim_x,dim_thetaA)
        E_1 = cs.MX.sym('E_1',dim_thetaA,dim_x)
  
        B_1 = cs.MX.sym('B_1',dim_x,dim_thetaB)
        E_2 = cs.MX.sym('E_2',dim_thetaB,dim_u)

        C_1 = cs.MX.sym('C_1',dim_y,dim_thetaC)
        E_3 = cs.MX.sym('E_3',dim_thetaC,dim_x)            
        
        # Define Parameters for the multiplicative Neural Networks by Rehmer
        NN1 = []
        NN2 = []
        NN3 = []
        
        # NN_1_dim.append(dim_thetaA)
        for NN, NN_name, NN_dim in zip([NN1,NN2,NN3],['NN1','NN2','NN3'],
                                       [NN_1_dim,NN_2_dim,NN_3_dim]):
            
            for l in range(0,len(NN_dim)):
            
                if l == 0:
                    params = [cs.MX.sym(NN_name+'_Wx'+str(l),NN_dim[l],dim_x),
                              cs.MX.sym(NN_name+'_Wu'+str(l),NN_dim[l],dim_u),
                              cs.MX.sym(NN_name+'_b'+str(l),NN_dim[l],1)]
                else:
                    params = [cs.MX.sym(NN_name+'_W'+str(l),NN_dim[l],NN_dim[l-1]),
                              cs.MX.sym(NN_name+'_b'+str(l),NN_dim[l],1)]
                
                NN.append(params)

        # Define Model Equations
       
        # Calculate the activations of the NNs by looping over each NN and
        # each layer
        NN_out = [[0],[0],[0]]
        
        for out,NN,NN_act in zip(NN_out,[NN1,NN2,NN3],[NN1_act,NN2_act,NN3_act]):

            for l in range(0,len(NN)):

                if l == 0:
                    out.append(NN_layer(cs.vertcat(x,u),cs.horzcat(NN[l][0],
                                       NN[l][1]),NN[l][2],NN_act[l]))
                else:
                    out.append(NN_layer(out[-1],NN[l][0],NN[l][1],NN_act[l]))


        # State and output equation
        x_new = cs.mtimes(A_0,x) + cs.mtimes(B_0,u) + cs.mtimes(A_1, 
                NN_out[0][-1]*cs.tanh(cs.mtimes(E_1,x))) + cs.mtimes(B_1, 
                NN_out[1][-1]*cs.tanh(cs.mtimes(E_2,u)))
        y_new = cs.mtimes(C_0,x_new) + cs.mtimes(C_1, 
                NN_out[2][-1]*cs.tanh(cs.mtimes(E_3,x_new)))
        
        
        # Define inputs and outputs for casadi function
        input = [x,u,A_0,A_1,E_1,B_0,B_1,E_2,C_0,C_1,E_3]
        input_names = ['x','u','A_0','A_1','E_1','B_0','B_1','E_2','C_0',
                       'C_1','E_3']
        
        self.Parameters = {'A_0':np.random.rand(dim_x,dim_x),
                           'A_1':np.random.rand(dim_x,dim_thetaA)*0.0001,
                           'E_1':np.random.rand(dim_thetaA,dim_x),
                           'B_0':np.random.rand(dim_x,dim_u),
                           'B_1':np.random.rand(dim_x,dim_thetaB),
                           'E_2':np.random.rand(dim_thetaB,dim_u),
                           'C_0':np.random.rand(dim_y,dim_x),
                           'C_1':np.random.rand(dim_y,dim_thetaC),
                           'E_3':np.random.rand(dim_thetaC,dim_x)}
        
        # Add remaining parameters in loop since they depend on depth of NNs
        
        for NN_name, NN in zip(['NN1','NN2','NN3'],[NN1,NN2,NN3]):
            
            for l in range(0,len(NN)):
            
                input.extend(NN[l])
                i=str(l)
                
                if l==0:
                    input_names.extend([NN_name+'_Wx'+i,
                                        NN_name+'_Wu'+i,
                                        NN_name+'_b'+i])
                    
                    self.Parameters[NN_name+'_Wx'+i] = np.random.rand(*NN[l][0].shape)
                    self.Parameters[NN_name+'_Wu'+i] = np.random.rand(*NN[l][1].shape)
                    self.Parameters[NN_name+'_b'+i] = np.random.rand(*NN[l][2].shape)
                    
                else:
                    input_names.extend([NN_name+'_W'+i,
                                        NN_name+'_b'+i])
                    
                    self.Parameters[NN_name+'_W'+i] = np.random.rand(*NN[l][0].shape)
                    self.Parameters[NN_name+'_b'+i] = np.random.rand(*NN[l][1].shape)            
        
        # Initialize if inital parameters are given
        if initial_params is not None:
            for param in initial_params.keys():
                self.Parameters[param] = initial_params[param]
                
        output = [x_new,y_new]
        output_names = ['x_new','y_new']
        
        self.Function = cs.Function(name, input, output, input_names,
                                    output_names)
        
        
        # Calculate affine parameters
        theta_A = NN_out[0][-1] * cs.tanh(cs.mtimes(E_1,x))/cs.mtimes(E_1,x)
        theta_B = NN_out[1][-1] * cs.tanh(cs.mtimes(E_2,u))/cs.mtimes(E_2,u)
        theta_C = NN_out[2][-1] * cs.tanh(cs.mtimes(E_3,x))/cs.mtimes(E_3,x)
        
        theta = cs.vertcat(theta_A,theta_B,theta_C)   
        
        self.AffineParameters = cs.Function('AffineParameters',input,
                                            [theta],input_names,['theta'])
        
        
        return None
        
    def AffineStateSpaceMatrices(self,theta):
        
        A_0 = self.Parameters['A_0']
        B_0 = self.Parameters['B_0']
        C_0 = self.Parameters['C_0']
    
        A_lpv = self.Parameters['A_0']
        B_lpv = self.Parameters['B_lpv']
        C_lpv = self.Parameters['C_lpv']  
    
        W_A = self.Parameters['W_A']
        W_B = self.Parameters['W_B']
        W_C = self.Parameters['W_C']      
    
        theta_A = theta[0:self.dim_thetaA]
        theta_B = theta[self.dim_thetaA:self.dim_thetaA+self.dim_thetaB]
        theta_C = theta[self.dim_thetaA+self.dim_thetaB:self.dim_thetaA+
                        self.dim_thetaB+self.dim_thetaC]
        
        A = A_0 + np.linalg.multi_dot([A_lpv,np.diag(theta_A),W_A])
        B = B_0 + np.linalg.multi_dot([B_lpv,np.diag(theta_B),W_B])
        C = C_0 + np.linalg.multi_dot([C_lpv,np.diag(theta_C),W_C]) 
        
        return A,B,C

    def AffineParameters(self,x0,u0):
        '''

        '''
        
        params = self.Parameters
        
        params_new = []
            
        for name in self.AffineParameters.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        theta = self.AffineParameters(x0,u0,*params_new)

        return theta

    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new) 

        return x1,y1    


    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        x = []
        y = []  
        theta = []

        # initial states
        x.append(x0)        
        
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = \
                self.OneStepPrediction(x[k],u[[k],:],params)
            
            # theta.append(t)
            x.append(x_new)
            y.append(y_new)
        
        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T   
        # theta = cs.hcat(theta).T
        
        return x,y


def NN_layer(input,weights,bias,nonlinearity):
    '''
    

    Parameters
    ----------
    input : TYPE
        DESCRIPTION.
    weights : TYPE
        DESCRIPTION.
    bias : TYPE
        DESCRIPTION.
    nonlinearity : TYPE
        DESCRIPTION.

    Returns
    -------
    y : TYPE
        DESCRIPTION.

    '''
    
    if nonlinearity == 0:
        nonlin = cs.tanh
    elif nonlinearity == 1:
        nonlin = logistic
    elif nonlinearity == 2:
        nonlin  = identity
            
    net = cs.mtimes(weights,input) + bias

    return nonlin(net)



class RehmerLPV():

    def __init__(self,dim_u,dim_x,dim_y,dim_thetaA=0,dim_thetaB=0,dim_thetaC=0,
                 fA_dim=0,fB_dim=0,fC_dim=0,activation=0,initial_params=None,name=None):
        '''
        Initializes the model structure by Rehmer et al. 2021.
        dim_u: int, dimension of the input vector
        dim_x: int, dimension of the state vector
        dim_y: int, dimension of the output vector
        dim_thetaA: int, dimension of the affine parameter associated with the 
        system matrix
        dim_thetaB: int, dimension of the affine parameter associated with the 
        input matrix
        dim_thetaC: int, dimension of the affine parameter associated with the 
        output matrix
        fA_dim: int, number of neurons in the hidden layer of the NN associated 
        with the system matrix
        fB_dim: int, number of neurons in the hidden layer of the NN associated 
        with the input matrix        
        fC_dim: int, number of neurons in the hidden layer of the NN associated 
        with the output matrix        
        
        activation: int, specifies activation function used in the NNs
                    0 --> tanh()
                    1 --> logistic()
                    2 --> linear()
        initial_params: dict, dictionary specifying the inital parameter values
        name: str, specifies name of the model
        '''
        
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_thetaA = dim_thetaA
        self.dim_thetaB = dim_thetaB
        self.dim_thetaC = dim_thetaC
        self.fA_dim = fA_dim
        self.fB_dim = fB_dim
        self.fC_dim = fC_dim
        self.activation = activation
        self.name = name
        
        self.Initialize(initial_params)

    def Initialize(self,initial_params=None):
            
            # For convenience of notation
            dim_u = self.dim_u
            dim_x = self.dim_x 
            dim_y = self.dim_y   
            dim_thetaA = self.dim_thetaA
            dim_thetaB = self.dim_thetaB
            dim_thetaC = self.dim_thetaC
            fA_dim = self.fA_dim
            fB_dim = self.fB_dim
            fC_dim = self.fC_dim    
           
            name = self.name
            
            # Define input, state and output vector
            u = cs.MX.sym('u',dim_u,1)
            x = cs.MX.sym('x',dim_x,1)
            y = cs.MX.sym('y',dim_y,1)
            
            # Define Model Parameters
            A_0 = cs.MX.sym('A_0',dim_x,dim_x)
            A_lpv = cs.MX.sym('A_lpv',dim_x,dim_thetaA)
            W_A = cs.MX.sym('W_A',dim_thetaA,dim_x)
            
            W_fA_x = cs.MX.sym('W_fA_x',fA_dim,dim_x)
            W_fA_u = cs.MX.sym('W_fA_u',fA_dim,dim_u)
            b_fA_h = cs.MX.sym('b_fA_h',fA_dim,1)
            W_fA = cs.MX.sym('W_fA',dim_thetaA,fA_dim)
            b_fA = cs.MX.sym('b_fA',dim_thetaA,1)
            
            B_0 = cs.MX.sym('B_0',dim_x,dim_u)
            B_lpv = cs.MX.sym('B_lpv',dim_x,dim_thetaB)
            W_B = cs.MX.sym('W_B',dim_thetaB,dim_u)
  
            W_fB_x = cs.MX.sym('W_fB_x',fB_dim,dim_x)
            W_fB_u = cs.MX.sym('W_fB_u',fB_dim,dim_u)
            b_fB_h = cs.MX.sym('b_fB_h',fB_dim,1)
            W_fB = cs.MX.sym('W_fB',dim_thetaB,fB_dim)
            b_fB = cs.MX.sym('b_fB',dim_thetaB,1)            
  
            C_0 = cs.MX.sym('C_0',dim_y,dim_x)
            C_lpv = cs.MX.sym('C_lpv',dim_y,dim_thetaC)
            W_C = cs.MX.sym('W_C',dim_thetaC,dim_x)
            
            W_fC_x = cs.MX.sym('W_fC_x',fC_dim,dim_x)
            W_fC_u = cs.MX.sym('W_fC_u',fC_dim,dim_u)
            b_fC_h = cs.MX.sym('b_fC_h',fC_dim,1)
            W_fC = cs.MX.sym('W_fC',dim_thetaC,fC_dim)
            b_fC = cs.MX.sym('b_fC',dim_thetaC,1)            
            
            
            
            # Put all Parameters in Dictionary with random initialization
            self.Parameters = {'A_0':np.random.rand(dim_x,dim_x),
                               'A_lpv':np.random.rand(dim_x,dim_thetaA)*0.0001,
                               'W_A':np.random.rand(dim_thetaA,dim_x),
                               'W_fA_x':np.random.rand(fA_dim,dim_x),
                               'W_fA_u':np.random.rand(fA_dim,dim_u),
                               'b_fA_h':np.random.rand(fA_dim,1),
                               'W_fA':np.random.rand(dim_thetaA,fA_dim),
                               'b_fA':np.random.rand(dim_thetaA,1)  ,                             
                               'B_0':np.random.rand(dim_x,dim_u),
                               'B_lpv':np.random.rand(dim_x,dim_thetaB),
                               'W_fB_x':np.random.rand(fB_dim,dim_x),
                               'W_fB_u':np.random.rand(fB_dim,dim_u),
                               'b_fB_h':np.random.rand(fB_dim,1),
                               'W_fB':np.random.rand(dim_thetaB,fB_dim),
                               'b_fB':np.random.rand(dim_thetaB,1),                               
                               'W_B':np.random.rand(dim_thetaB,dim_u),
                               'C_0':np.random.rand(dim_y,dim_x),
                               'C_lpv':np.random.rand(dim_y,dim_thetaC),
                               'W_C':np.random.rand(dim_thetaC,dim_x),
                               'W_fC_x':np.random.rand(fC_dim,dim_x),
                               'W_fC_u':np.random.rand(fC_dim,dim_u),
                               'b_fC_h':np.random.rand(fC_dim,1),
                               'W_fC':np.random.rand(dim_thetaC,fC_dim),
                               'b_fC':np.random.rand(dim_thetaC,1)}
        
            # Initialize if inital parameters are given
            if initial_params is not None:
                for param in initial_params.keys():
                    self.Parameters[param] = initial_params[param]
                    
            
            # Define Model Equations
            fA_h = cs.tanh(cs.mtimes(W_fA_x,x) + cs.mtimes(W_fA_u,u) + b_fA_h)
            fA = logistic(cs.mtimes(W_fA,fA_h)+b_fA)
            
            fB_h = cs.tanh(cs.mtimes(W_fB_x,x) + cs.mtimes(W_fB_u,u) + b_fB_h)
            fB = logistic(cs.mtimes(W_fB,fB_h)+b_fB)
            
            fC_h = cs.tanh(cs.mtimes(W_fC_x,x) + cs.mtimes(W_fC_u,u) + b_fC_h)
            fC = logistic(cs.mtimes(W_fC,fC_h)+b_fC)
            
            x_new = cs.mtimes(A_0,x) + cs.mtimes(B_0,u) + cs.mtimes(A_lpv, 
                    fA*cs.tanh(cs.mtimes(W_A,x))) + cs.mtimes(B_lpv, 
                    fB*cs.tanh(cs.mtimes(W_B,u)))
            y_new = cs.mtimes(C_0,x_new) + cs.mtimes(C_lpv, 
                    fC*cs.tanh(cs.mtimes(W_C,x_new)))
            
            input = [x,u,A_0,A_lpv,W_A,W_fA_x,W_fA_u,b_fA_h,W_fA,b_fA,
                     B_0,B_lpv,W_B,W_fB_x,W_fB_u,b_fB_h,W_fB,b_fB,
                     C_0,C_lpv,W_C,W_fC_x,W_fC_u,b_fC_h,W_fC,b_fC]
            
            input_names = ['x','u',
                           'A_0','A_lpv','W_A','W_fA_x','W_fA_u', 'b_fA_h',
                           'W_fA','b_fA',
                           'B_0','B_lpv','W_B','W_fB_x','W_fB_u','b_fB_h',
                           'W_fB','b_fB',
                           'C_0','C_lpv','W_C','W_fC_x','W_fC_u','b_fC_h',
                           'W_fC','b_fC']
            
            output = [x_new,y_new]
            output_names = ['x_new','y_new']
            
            self.Function = cs.Function(name, input, output, input_names,
                                        output_names)
            
            
            # Calculate affine parameters
            theta_A = fA * cs.tanh(cs.mtimes(W_A,x))/cs.mtimes(W_A,x)
            theta_B = fB * cs.tanh(cs.mtimes(W_B,u))/cs.mtimes(W_B,u)
            theta_C = fC * cs.tanh(cs.mtimes(W_C,x))/cs.mtimes(W_C,x)
            
            theta = cs.vertcat(theta_A,theta_B,theta_C)   
            
            self.AffineParameters = cs.Function('AffineParameters',input,
                                                [theta],input_names,['theta'])
            
            
            return None
        
    def AffineStateSpaceMatrices(self,theta):
        
        A_0 = self.Parameters['A_0']
        B_0 = self.Parameters['B_0']
        C_0 = self.Parameters['C_0']
    
        A_lpv = self.Parameters['A_0']
        B_lpv = self.Parameters['B_lpv']
        C_lpv = self.Parameters['C_lpv']  
    
        W_A = self.Parameters['W_A']
        W_B = self.Parameters['W_B']
        W_C = self.Parameters['W_C']      
    
        theta_A = theta[0:self.dim_thetaA]
        theta_B = theta[self.dim_thetaA:self.dim_thetaA+self.dim_thetaB]
        theta_C = theta[self.dim_thetaA+self.dim_thetaB:self.dim_thetaA+
                        self.dim_thetaB+self.dim_thetaC]
        
        A = A_0 + np.linalg.multi_dot([A_lpv,np.diag(theta_A),W_A])
        B = B_0 + np.linalg.multi_dot([B_lpv,np.diag(theta_B),W_B])
        C = C_0 + np.linalg.multi_dot([C_lpv,np.diag(theta_C),W_C]) 
        
        return A,B,C

    def EvalAffineParameters(self,x0,u0,params=None):
        '''

        '''
        if params==None:
            params = self.Parameters        
        
        params_new = []
            
        for name in self.AffineParameters.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        theta = self.AffineParameters(x0,u0,*params_new)

        return theta

    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new) 

        return x1,y1    


    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        x = []
        y = []  
        theta = []

        # initial states
        x.append(x0)        
        
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = \
                self.OneStepPrediction(x[k],u[[k],:],params)
            
            # theta.append(t)
            x.append(x_new)
            y.append(y_new)
        
        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T   
        # theta = cs.hcat(theta).T
        
        return x,y

class LachhabLPV():
    """
    
    """

    def __init__(self,dim_u,dim_x,dim_y,dim_thetaA,dim_thetaB,dim_thetaC,name):
        
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_thetaA = dim_thetaA
        self.dim_thetaB = dim_thetaB
        self.dim_thetaC = dim_thetaC
        self.name = name
        
        self.Initialize()

    def Initialize(self):
            
            # For convenience of notation
            dim_u = self.dim_u
            dim_x = self.dim_x 
            dim_y = self.dim_y   
            dim_thetaA = self.dim_thetaA
            dim_thetaB = self.dim_thetaB
            dim_thetaC = self.dim_thetaC
            name = self.name
            
            # Define input, state and output vector
            u = cs.MX.sym('u',dim_u,1)
            x = cs.MX.sym('x',dim_x,1)
            y = cs.MX.sym('y',dim_y,1)
            
            # Define Model Parameters
            A_0 = cs.MX.sym('A_0',dim_x,dim_x)
            A_lpv = cs.MX.sym('A_lpv',dim_x,dim_thetaA)
            W_A = cs.MX.sym('W_A',dim_thetaA,dim_x)
            
            B_0 = cs.MX.sym('B_0',dim_x,dim_u)
            B_lpv = cs.MX.sym('B_lpv',dim_x,dim_thetaB)
            W_B = cs.MX.sym('W_B',dim_thetaB,dim_u)
            
            C_0 = cs.MX.sym('C_0',dim_y,dim_x)
            C_lpv = cs.MX.sym('C_lpv',dim_y,dim_thetaC)
            W_C = cs.MX.sym('W_C',dim_thetaC,dim_x)
            
            # Put all Parameters in Dictionary with random initialization
            self.Parameters = {'A_0':np.random.rand(dim_x,dim_x),
                               'A_lpv':np.random.rand(dim_x,dim_thetaA),
                               'W_A':np.random.rand(dim_thetaA,dim_x),
                               'B_0':np.random.rand(dim_x,dim_u),
                               'B_lpv':np.random.rand(dim_x,dim_thetaB),
                               'W_B':np.random.rand(dim_thetaB,dim_u),
                               'C_0':np.random.rand(dim_y,dim_x),
                               'C_lpv':np.random.rand(dim_y,dim_thetaC),
                               'W_C':np.random.rand(dim_thetaC,dim_x)}
        
            
            # Initialize if inital parameters are given
            if initial_params is not None:
                for param in initial_params.keys():
                    self.Parameters[param] = initial_params[param]
            
            # Define Model Equations
            x_new = cs.mtimes(A_0,x) + cs.mtimes(B_0,u) + cs.mtimes(A_lpv, 
                    cs.tanh(cs.mtimes(W_A,x))) + cs.mtimes(B_lpv, 
                    cs.tanh(cs.mtimes(W_B,u)))
            y_new = cs.mtimes(C_0,x_new) + cs.mtimes(C_lpv, 
                    cs.tanh(cs.mtimes(W_C,x_new)))
            
            
            input = [x,u,A_0,A_lpv,W_A,B_0,B_lpv,W_B,C_0,C_lpv,W_C]
            input_names = ['x','u','A_0','A_lpv','W_A','B_0','B_lpv','W_B','C_0','C_lpv','W_C']
            
            output = [x_new,y_new]
            output_names = ['x_new','y_new']  
            
            self.Function = cs.Function(name, input, output, input_names,output_names)

            # Calculate affine parameters
            # theta_A = XXX
            # theta_B = XXX
            # theta_C = XXX
            
            # theta = cs.vertcat(theta_A,theta_B,theta_C)   
            
            # self.AffineParameters = cs.Function('AffineParameters',input,
            #                                     [theta],input_names,['theta'])


            
            return None

    def AffineParameters(self,x0,u0):
        '''
        Returns the affine Parameters of the LPV model
        '''
        
        params = self.Parameters
        
        params_new = []
            
        for name in self.AffineParameters.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        theta = self.AffineParameters(x0,u0,*params_new) 

        return theta    

    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new)     
                              
        return x1,y1
   
    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''

        x = []
        y = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = self.OneStepPrediction(x[k],u[[k],:],params)
            x.append(x_new)
            y.append(y_new)
        

        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T
       
        return y




class LinearSSM():
    """
    
    """

    def __init__(self,dim_u,dim_x,dim_y,name):
        
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.name = name
        
        self.Initialize(initial_params)

    def Initialize(self,initial_params=None):
            
            # For convenience of notation
            dim_u = self.dim_u
            dim_x = self.dim_x 
            dim_y = self.dim_y             
            name = self.name
            
            # Define input, state and output vector
            u = cs.MX.sym('u',dim_u,1)
            x = cs.MX.sym('x',dim_x,1)
            y = cs.MX.sym('y',dim_y,1)
            
            # Define Model Parameters
            A = cs.MX.sym('A',dim_x,dim_x)
            B = cs.MX.sym('B',dim_x,dim_u)
            C = cs.MX.sym('C',dim_y,dim_x)

            
            # Put all Parameters in Dictionary with random initialization
            self.Parameters = {'A':np.random.rand(dim_x,dim_x),
                               'B':np.random.rand(dim_x,dim_u),
                               'C':np.random.rand(dim_y,dim_x)}
        
            # self.Input = {'u':np.random.rand(u.shape)}
            
            # Define Model Equations
            x_new = cs.mtimes(A,x) + cs.mtimes(B,u)
            y_new = cs.mtimes(C,x_new) 
            
            
            input = [x,u,A,B,C]
            input_names = ['x','u','A','B','C']
            
            output = [x_new,y_new]
            output_names = ['x_new','y_new']  
            
            self.Function = cs.Function(name, input, output, input_names,output_names)
            
            return None
   
    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new)     
                              
        return x1,y1
   
    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''

        x = []
        y = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = self.OneStepPrediction(x[k],u[[k],:],params)
            x.append(x_new)
            y.append(y_new)
        

        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T
       
        return y


class MLP():
    """
    
    """

    def __init__(self,dim_u,dim_x,dim_hidden,name):
        
        self.dim_u = dim_u
        self.dim_hidden = dim_hidden
        self.dim_x = dim_x
        self.name = name
        
        self.Initialize()

    def Initialize(self):
                
            dim_u = self.dim_u
            dim_hidden = self.dim_hidden
            dim_x = self.dim_x 
            name = self.name
        
            u = cs.MX.sym('u',dim_u,1)
            x = cs.MX.sym('x',dim_x,1)
            
            # Parameters
            W_h = cs.MX.sym('W_h',dim_hidden,dim_u+dim_x)
            b_h = cs.MX.sym('b_h',dim_hidden,1)
            
            W_o = cs.MX.sym('W_out',dim_x,dim_hidden)
            b_o = cs.MX.sym('b_out',dim_x,1)
            
            # Put all Parameters in Dictionary with random initialization
            self.Parameters = {'W_h':np.random.rand(W_h.shape[0],W_h.shape[1]),
                               'b_h':np.random.rand(b_h.shape[0],b_h.shape[1]),
                               'W_o':np.random.rand(W_o.shape[0],W_o.shape[1]),
                               'b_o':np.random.rand(b_o.shape[0],b_o.shape[1])}
        
            # self.Input = {'u':np.random.rand(u.shape)}
            
            # Equations
            h =  cs.tanh(cs.mtimes(W_h,cs.vertcat(u,x))+b_h)
            x_new = cs.mtimes(W_o,h)+b_o
            
            
            input = [x,u,W_h,b_h,W_o,b_o]
            input_names = ['x','u','W_h','b_h','W_o','b_o']
            
            output = [x_new]
            output_names = ['x_new']  
            
            self.Function = cs.Function(name, input, output, input_names,output_names)
            
            return None
   
    def OneStepPrediction(self,x0,u0,params=None):
        # Casadi Function needs list of parameters as input
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1 = self.Function(x0,u0,*params_new)     
                              
        return x1
   
    def Simulation(self,x0,u,params=None):
        # Casadi Function needs list of parameters as input
        
        x = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x.append(self.OneStepPrediction(x[k],u[[k],:],params))
        
        # Concatenate list to casadiMX
        x = cs.vcat(x) 
       
        return x

def RBF(x,c,w):
    d = x-c    
    e = - cs.mtimes(cs.mtimes(d.T,cs.diag(w)**2),d)
    y = cs.exp(e)
    
    return y

def logistic(x):
    
    y = 0.5 + 0.5 * cs.tanh(0.5*x)

    return y


def identity(x):
    return x


class GRU():
    """
    Modell des Bauteils, welches die einwirkenden Prozessgrößen auf die 
    resultierenden Bauteilqualität abbildet.    
    """

    def __init__(self,dim_u,dim_c,dim_hidden,dim_out,name):
        
        self.dim_u = dim_u
        self.dim_c = dim_c
        self.dim_hidden = dim_hidden
        self.dim_out = dim_out
        self.name = name
        
        self.Initialize()  
 

    def Initialize(self):
        
        dim_u = self.dim_u
        dim_c = self.dim_c
        dim_hidden = self.dim_hidden
        dim_out = self.dim_out
        name = self.name      
        
        u = cs.MX.sym('u',dim_u,1)
        c = cs.MX.sym('c',dim_c,1)
        
        # Parameters
        # RNN part
        W_r = cs.MX.sym('W_r',dim_c,dim_u+dim_c)
        b_r = cs.MX.sym('b_r',dim_c,1)
    
        W_z = cs.MX.sym('W_z',dim_c,dim_u+dim_c)
        b_z = cs.MX.sym('b_z',dim_c,1)    
        
        W_c = cs.MX.sym('W_c',dim_c,dim_u+dim_c)
        b_c = cs.MX.sym('b_c',dim_c,1)    
    
        # MLP part
        W_h = cs.MX.sym('W_z',dim_hidden,dim_c)
        b_h = cs.MX.sym('b_z',dim_hidden,1)    
        
        W_o = cs.MX.sym('W_c',dim_out,dim_hidden)
        b_o = cs.MX.sym('b_c',dim_out,1)  
        
        # Put all Parameters in Dictionary with random initialization
        self.Parameters = {'W_r':np.random.rand(W_r.shape[0],W_r.shape[1]),
                           'b_r':np.random.rand(b_r.shape[0],b_r.shape[1]),
                           'W_z':np.random.rand(W_z.shape[0],W_z.shape[1]),
                           'b_z':np.random.rand(b_z.shape[0],b_z.shape[1]),
                           'W_c':np.random.rand(W_c.shape[0],W_c.shape[1]),
                           'b_c':np.random.rand(b_c.shape[0],b_c.shape[1]),                          
                           'W_h':np.random.rand(W_h.shape[0],W_h.shape[1]),
                           'b_h':np.random.rand(b_h.shape[0],b_h.shape[1]),                           
                           'W_o':np.random.rand(W_o.shape[0],W_o.shape[1]),
                           'b_o':np.random.rand(b_o.shape[0],b_o.shape[1])}
        
        # Equations
        f_r = logistic(cs.mtimes(W_r,cs.vertcat(u,c))+b_r)
        f_z = logistic(cs.mtimes(W_z,cs.vertcat(u,c))+b_z)
        
        c_r = f_r*c
        
        f_c = cs.tanh(cs.mtimes(W_c,cs.vertcat(u,c_r))+b_c)
        
        
        c_new = f_z*c+(1-f_z)*f_c
        
        h =  cs.tanh(cs.mtimes(W_h,c_new)+b_h)
        x_new = cs.mtimes(W_o,h)+b_o    
    
        
        # Casadi Function
        input = [c,u,W_r,b_r,W_z,b_z,W_c,b_c,W_h,b_h,W_o,b_o]
        input_names = ['c','u','W_r','b_r','W_z','b_z','W_c','b_c','W_h','b_h',
                        'W_o','b_o']
        
        output = [c_new,x_new]
        output_names = ['c_new','x_new']
    
        self.Function = cs.Function(name, input, output, input_names,output_names)

        return None
    
    def OneStepPrediction(self,c0,u0,params=None):
        # Casadi Function needs list of parameters as input
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        c1,x1 = self.Function(c0,u0,*params_new)     
                              
        return c1,x1
   
    def Simulation(self,c0,u,params=None):
        # Casadi Function needs list of parameters as input
        
        # print('GRU Simulation ignores given initial state, initial state is set to zero!')
        c0 = np.zeros((self.dim_c,1))
        
        c = []
        x = []
        
        # initial cell state
        c.append(c0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            c_new,x_new = self.OneStepPrediction(c[k],u[k,:],params)
            c.append(c_new)
            x.append(x_new)
        
        # Concatenate list to casadiMX
        c = cs.hcat(c).T    
        x = cs.hcat(x).T
        
        return x[-1]
    
    
class SilverBoxPhysikal():
    """
    
    """

    def __init__(self,name):
        
        self.name = name
        
        self.Initialize()

    def Initialize(self):
            
            # For convenience of notation
            name = self.name
            
            # Define input, state and output vector
            u = cs.MX.sym('u',1,1)
            x = cs.MX.sym('x',2,1)
            y = cs.MX.sym('y',1,1)
            
            # Define Model Parameters
            dt = 1/610.352    #1/610.35  cs.MX.sym('dt',1,1)  #Sampling rate fixed from literature
            d = cs.MX.sym('d',1,1)
            a = cs.MX.sym('a',1,1)
            b = cs.MX.sym('b',1,1)
            m = cs.MX.sym('m',1,1)
            
            
            m_init = 1.e-05*abs(np.random.rand(1,1))#1.09992821e-05
            d_init = 2*m_init*21.25
            a_init = d_init**2/(4*m_init)+437.091**2*m_init
            # dt_init = np.array([[ 1/610.35]])
            
            # Put all Parameters in Dictionary with random initialization
            self.Parameters = {'d':d_init,#0.01+0.001*np.random.rand(1,1),
                               'a':a_init,#2+0.001*np.random.rand(1,1),
                               'b':0.01*abs(np.random.rand(1,1)),
                               'm':m_init}#0.0001+0.001*np.random.rand(1,1)}
            
           
        
            # continuous dynamics
            x_new = cs.vertcat(x[1],(-(a + b*x[0]**2)*x[0] - d*x[1] + u)/m)
            
            input = [x,u,d,a,b,m]
            input_names = ['x','u','d','a','b','m']
            
            output = [x_new]
            output_names = ['x_new']  
            
            
            f_cont = cs.Function(name,input,output,
                                 input_names,output_names)  
            
            x1 = RK4(f_cont,input,dt)
            y1 = x1[0]
            
            self.Function = cs.Function(name, input, [x1,y1],
                                        input_names,['x1','y1'])
            
            return None
   
    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new)     
                              
        return x1,y1
   
    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''

        x = []
        y = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = self.OneStepPrediction(x[k],u[[k],:],params)
            x.append(x_new)
            y.append(y_new)
        

        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T
        
        # y = y[0::10]
       
        return y
    





class LinearSSM():
    """
    
    """

    def __init__(self,dim_u,dim_x,dim_y,name):
        
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.name = name
        
        self.Initialize()

    def Initialize(self):
            
            # For convenience of notation
            dim_u = self.dim_u
            dim_x = self.dim_x 
            dim_y = self.dim_y             
            name = self.name
            
            # Define input, state and output vector
            u = cs.MX.sym('u',dim_u,1)
            x = cs.MX.sym('x',dim_x,1)
            y = cs.MX.sym('y',dim_y,1)
            
            # Define Model Parameters
            A = cs.MX.sym('A',dim_x,dim_x)
            B = cs.MX.sym('B',dim_x,dim_u)
            C = cs.MX.sym('C',dim_y,dim_x)

            
            # Put all Parameters in Dictionary with random initialization
            self.Parameters = {'A':np.random.rand(dim_x,dim_x),
                               'B':np.random.rand(dim_x,dim_u),
                               'C':np.random.rand(dim_y,dim_x)}
        
            # self.Input = {'u':np.random.rand(u.shape)}
            
            # Define Model Equations
            x_new = cs.mtimes(A,x) + cs.mtimes(B,u)
            y_new = cs.mtimes(C,x_new) 
            
            
            input = [x,u,A,B,C]
            input_names = ['x','u','A','B','C']
            
            output = [x_new,y_new]
            output_names = ['x_new','y_new']  
            
            self.Function = cs.Function(name, input, output, input_names,output_names)
            
            return None
   
    def OneStepPrediction(self,x0,u0,params=None):
        '''
        Estimates the next state and output from current state and input
        x0: Casadi MX, current state
        u0: Casadi MX, current input
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''
        
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1,y1 = self.Function(x0,u0,*params_new)     
                              
        return x1,y1
   
    def Simulation(self,x0,u,params=None):
        '''
        A iterative application of the OneStepPrediction in order to perform a
        simulation for a whole input trajectory
        x0: Casadi MX, inital state a begin of simulation
        u: Casadi MX,  input trajectory
        params: A dictionary of opti variables, if the parameters of the model
                should be optimized, if None, then the current parameters of
                the model are used
        '''

        x = []
        y = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x_new,y_new = self.OneStepPrediction(x[k],u[[k],:],params)
            x.append(x_new)
            y.append(y_new)
        

        # Concatenate list to casadiMX
        y = cs.hcat(y).T    
        x = cs.hcat(x).T
       
        return y


class MLP():
    """
    Implementation of a single-layered Feedforward Neural Network.
    """

    def __init__(self,dim_u,dim_x,dim_hidden,name):
        """
        Initialization procedure of the Feedforward Neural Network Architecture
        
        
        Parameters
        ----------
        dim_u : int
            Dimension of the input, e.g. dim_u = 2 if input is a 2x1 vector
        dim_x : int
            Dimension of the state, e.g. dim_x = 3 if state is a 3x1 vector.
        dim_hidden : int
            Number of nonlinear neurons in the hidden layer, e.g. dim_hidden=10,
            if NN is supposed to have 10 neurons in hidden layer.
        name : str
            Name of the model, e.g. name = 'InjectionPhaseModel'.

        Returns
        -------
        None.

        """
        self.dim_u = dim_u
        self.dim_hidden = dim_hidden
        self.dim_x = dim_x
        self.name = name
        
        self.Initialize()

    def Initialize(self):
        """
        Defines the parameters of the model as symbolic casadi variables and 
        the model equation as casadi function. Model parameters are initialized
        randomly.

        Returns
        -------
        None.

        """   
        dim_u = self.dim_u
        dim_hidden = self.dim_hidden
        dim_x = self.dim_x 
        name = self.name
    
        u = cs.MX.sym('u',dim_u,1)
        x = cs.MX.sym('x',dim_x,1)
        
        # Model Parameters
        W_h = cs.MX.sym('W_h',dim_hidden,dim_u+dim_x)
        b_h = cs.MX.sym('b_h',dim_hidden,1)
        
        W_o = cs.MX.sym('W_out',dim_x,dim_hidden)
        b_o = cs.MX.sym('b_out',dim_x,1)
        
        # Put all Parameters in Dictionary with random initialization
        self.Parameters = {'W_h':np.random.rand(W_h.shape[0],W_h.shape[1]),
                           'b_h':np.random.rand(b_h.shape[0],b_h.shape[1]),
                           'W_o':np.random.rand(W_o.shape[0],W_o.shape[1]),
                           'b_o':np.random.rand(b_o.shape[0],b_o.shape[1])}
    
       
        # Model Equations
        h =  cs.tanh(cs.mtimes(W_h,cs.vertcat(u,x))+b_h)
        x_new = cs.mtimes(W_o,h)+b_o
        
        
        input = [x,u,W_h,b_h,W_o,b_o]
        input_names = ['x','u','W_h','b_h','W_o','b_o']
        
        output = [x_new]
        output_names = ['x_new']  
        
        self.Function = cs.Function(name, input, output, input_names,output_names)
        
        return None
   
    def OneStepPrediction(self,x0,u0,params=None):
        """
        OneStepPrediction() evaluates the model equation defined in 
        self.Function()
        
        self.Function() takes initial state x0, input u0 and all model 
        parameters as input. The model parameters can either be optimization
        variables themselves (as in system identification) or the take specific 
        values (when the estimated model is used for control)

        Parameters
        ----------
        x0 : array-like with dimension [self.dim_x, 1]
            initial state resp. state from last time-step
        u0 : array-like with dimension [self.dim_u, 1]
            input
        params : dictionary, optional
            params is None: This is the case during model based control,
            self.Function() is evaluated with the numerical
            values of the model parameters saved in self.Parameters
            params is dictionary of opti.variables: During system identification
            the model parameters are optimization variables themselves, so a 
            dictionary of opti.variables is passed to self.Function()

        Returns
        -------
        x1 : array-like with dimension [self.dim_x, 1]
            output of the Feedforward Neural Network

        """
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        x1 = self.Function(x0,u0,*params_new)     
                              
        return x1
   
    def Simulation(self,x0,u,params=None):
        """
        Repeated call of self.OneStepPrediction() for a given input trajectory
        

        Parameters
        ----------
        x0 : array-like with dimension [self.dim_x, 1]
            initial state resp
        u : array-like with dimension [N,self.dim_u]
            trajectory of input signal with length N
        params : dictionary, optional
            see self.OneStepPrediction()

        Returns
        -------
        x : array-like with dimension [N+1,self.dim_x]
            trajectory of output signal with length N+1 
            
        """
        
        x = []

        # initial states
        x.append(x0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            x.append(self.OneStepPrediction(x[k],u[[k],:],params))
        
        # Concatenate list to casadiMX
        x = cs.hcat(x).T 
       
        return x


    
def logistic(x):
    
    y = 0.5 + 0.5 * cs.tanh(0.5*x)

    return y

class GRU():
    """
    Implementation of a Gated Recurrent Unit with a Feedforward Neural Network
    as output
    """

    def __init__(self,dim_u,dim_c,dim_hidden,dim_out,name):
        """
        Initialization procedure of the GRU Architecture
        
        Parameters
        ----------
        dim_u : int
            Dimension of the input, e.g. dim_u = 2 if input is a 2x1 vector
        dim_c : int
            Dimension of the cell-state, i.e. the internal state of the GRU,
            e.g. dim_c = 2 if cell-state is a 2x1 vector
        dim_hidden : int
            Number of nonlinear neurons in the hidden layer, e.g. dim_hidden=10,
            if output network is supposed to have 10 neurons in hidden layer.           
        dim_out : int
            Dimension of the output, e.g. dim_out = 3 if output is a 3x1 vector.
        name : str
            Name of the model, e.g. name = 'QualityModel'.

        Returns
        -------
        None.

        """        
        self.dim_u = dim_u
        self.dim_c = dim_c
        self.dim_hidden = dim_hidden
        self.dim_out = dim_out
        self.name = name
        
        self.Initialize()  
 

    def Initialize(self):
        """
        Defines the parameters of the model as symbolic casadi variables and 
        the model equation as casadi function. Model parameters are initialized
        randomly.

        Returns
        -------
        None.

        """          
        dim_u = self.dim_u
        dim_c = self.dim_c
        dim_hidden = self.dim_hidden
        dim_out = self.dim_out
        name = self.name      
        
        u = cs.MX.sym('u',dim_u,1)
        c = cs.MX.sym('c',dim_c,1)
        
        # Parameters
        # RNN part
        W_r = cs.MX.sym('W_r',dim_c,dim_u+dim_c)
        b_r = cs.MX.sym('b_r',dim_c,1)
    
        W_z = cs.MX.sym('W_z',dim_c,dim_u+dim_c)
        b_z = cs.MX.sym('b_z',dim_c,1)    
        
        W_c = cs.MX.sym('W_c',dim_c,dim_u+dim_c)
        b_c = cs.MX.sym('b_c',dim_c,1)    
    
        # MLP part
        W_h = cs.MX.sym('W_z',dim_hidden,dim_c)
        b_h = cs.MX.sym('b_z',dim_hidden,1)    
        
        W_o = cs.MX.sym('W_c',dim_out,dim_hidden)
        b_o = cs.MX.sym('b_c',dim_out,1)  
        
        # Put all Parameters in Dictionary with random initialization
        self.Parameters = {'W_r':np.random.rand(W_r.shape[0],W_r.shape[1]),
                           'b_r':np.random.rand(b_r.shape[0],b_r.shape[1]),
                           'W_z':np.random.rand(W_z.shape[0],W_z.shape[1]),
                           'b_z':np.random.rand(b_z.shape[0],b_z.shape[1]),
                           'W_c':np.random.rand(W_c.shape[0],W_c.shape[1]),
                           'b_c':np.random.rand(b_c.shape[0],b_c.shape[1]),                          
                           'W_h':np.random.rand(W_h.shape[0],W_h.shape[1]),
                           'b_h':np.random.rand(b_h.shape[0],b_h.shape[1]),                           
                           'W_o':np.random.rand(W_o.shape[0],W_o.shape[1]),
                           'b_o':np.random.rand(b_o.shape[0],b_o.shape[1])}
        
        # Equations
        f_r = logistic(cs.mtimes(W_r,cs.vertcat(u,c))+b_r)
        f_z = logistic(cs.mtimes(W_z,cs.vertcat(u,c))+b_z)
        
        c_r = f_r*c
        
        f_c = cs.tanh(cs.mtimes(W_c,cs.vertcat(u,c_r))+b_c)
        
        
        c_new = f_z*c+(1-f_z)*f_c
        
        h =  cs.tanh(cs.mtimes(W_h,c_new)+b_h)
        x_new = cs.mtimes(W_o,h)+b_o    
    
        
        # Casadi Function
        input = [c,u,W_r,b_r,W_z,b_z,W_c,b_c,W_h,b_h,W_o,b_o]
        input_names = ['c','u','W_r','b_r','W_z','b_z','W_c','b_c','W_h','b_h',
                        'W_o','b_o']
        
        output = [c_new,x_new]
        output_names = ['c_new','x_new']
    
        self.Function = cs.Function(name, input, output, input_names,output_names)

        return None
    
    def OneStepPrediction(self,c0,u0,params=None):
        """
        OneStepPrediction() evaluates the model equation defined in 
        self.Function()
        
        self.Function() takes initial cell-state c0, input u0 and all model 
        parameters as input. The model parameters can either be optimization
        variables themselves (as in system identification) or the take specific 
        values (when the estimated model is used for control)

        Parameters
        ----------
        c0 : array-like with dimension [self.dim_c, 1]
            initial cell-state resp. state from last time-step
        u0 : array-like with dimension [self.dim_u, 1]
            input
        params : dictionary, optional
            params is None: This is the case during model based control,
            self.Function() is evaluated with the numerical
            values of the model parameters saved in self.Parameters
            params is dictionary of opti.variables: During system identification
            the model parameters are optimization variables themselves, so a 
            dictionary of opti.variables is passed to self.Function()

        Returns
        -------
        c1 : array-like with dimension [self.dim_c, 1]
            new cell-state
        x1 : array-like with dimension [self.dim_x, 1]
            output of the Feedforward Neural Network
        """
        if params==None:
            params = self.Parameters
        
        params_new = []
            
        for name in  self.Function.name_in():
            try:
                params_new.append(params[name])                      # Parameters are already in the right order as expected by Casadi Function
            except:
                continue
        
        c1,x1 = self.Function(c0,u0,*params_new)     
                              
        return c1,x1
   
    def Simulation(self,c0,u,params=None):
        """
        Repeated call of self.OneStepPrediction() for a given input trajectory
        

        Parameters
        ----------
        c0 : array-like with dimension [self.dim_c, 1]
            initial cell-state
        u : array-like with dimension [N,self.dim_u]
            trajectory of input signal with length N
        params : dictionary, optional
            see self.OneStepPrediction()

        Returns
        -------
        x : array-like with dimension [N+1,self.dim_x]
            trajectory of output signal with length N+1 
            
        """
        
        # Is that necessary?
        print('GRU Simulation ignores given initial state, initial state is set to zero!')
        
        
        c0 = np.zeros((self.dim_c,1))
        
        c = []
        x = []
        
        # initial cell state
        c.append(c0)
                      
        # Simulate Model
        for k in range(u.shape[0]):
            c_new,x_new = self.OneStepPrediction(c[k],u[k,:],params)
            c.append(c_new)
            x.append(x_new)
        
        # Concatenate list to casadiMX
        c = cs.hcat(c).T    
        x = cs.hcat(x).T
        
        return x[-1]
