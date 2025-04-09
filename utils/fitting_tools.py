from scipy.special import erfc
import numpy as np
from scipy.integrate import quad
import lmfit
import pandas as pd

# class to store information about a model and results obtained with it
class fit_model:
    def __init__(self, name, parfunc, abbreviated_name, columns, description=""):
        self.name=name
        self.parfunc=parfunc
        self.abbreviated_name=abbreviated_name
        self.columns=columns
        self.description=description
        self.do=True
        self.data=pd.DataFrame()

#------------------------
#model functions, t is time, other arguments are parameters
#functions must be able to process numpy arrays functions from scipy and numpy generally wont cause issues
#------------------------

def linear_decay(t, a, b):
    return a * t + b

def exponential_decay(t, a3, b3):
    return a3 * np.exp(-t / b3)

def biexponential_decay(t, a1, b1, a2, b2):
    return a1 * np.exp(-t / b1) + a2 * np.exp(-t / b2)

def logistic_plus_exp(t, A, tau, L, k, x0):
    return A * np.exp(-t / tau) + L / (1 + np.exp(-k * (t - x0)))

def stretched_exponential(t, A, tau, beta):
    return A * np.exp(-(t / tau) ** beta)

def erfc_linear(t, PCE0, k, t0, b):
    return (0.5 * erfc((t - t0) / b)) * (PCE0 - k * t)

#----------------------
#parameter functions
#arguments: array of power values, array of time values
#returns: list of relevant parameters(e.g. t80), power values of the fitted function at the given time values
#----------------------

def stretched_exponential_params(power, times):
    stretched_exponential_model = lmfit.Model(stretched_exponential) #create Model object from the function
    initial_params = stretched_exponential_model.make_params(A=power[0], tau=times[-1], beta=1) #initial values for the parameters
    
    result = stretched_exponential_model.fit(power, initial_params, t=times) #perform fit, result is an instance of lmfit.ModelResult 
    
    #calculate additional parameters, such as t80 and lifetime energy production
    time_extrapolate, pce_extrapolate = extrapolate(times, result)
    T80 = find_T80(time_extrapolate, pce_extrapolate)
    T80_capped = min(T80, times[-1])
    lifetime_energy = calculate_ley(stretched_exponential, result.best_values.values(), Ts80_capped)
    
    #put all relevant parameters into a list, if errors were calculated return parameters as uncertainties.ufloats, otherwise as normal floats
    if result.errorbars:
        result_values=[result.uvars["A"], result.uvars["tau"], result.uvars["beta"], 
                       result.rsquared, T80_capped, lifetime_energy]
    else:
        result_values=[result.best_values["A"], result.best_values["tau"], result.best_values["beta"], 
                       result.rsquared, tS_capped, Ts80_capped, lifetime_energy]
    return result_values, result.best_fit

def linear_params(power, times):
    linear_model = lmfit.models.LinearModel()
    initial_params = linear_model.guess(power, x=times)
    result = linear_model.fit(power, initial_params, x=times)
    
    slope=result.best_values["slope"]
    intercept=result.best_values["intercept"]
    
    t80 = intercept * 0.2 / -slope
    t80_capped = min(t80, times[-1])
    lifetime_energy = 0.5*slope*t80_capped**2 + intercept*t80_capped
    
    if result.errorbars:
        result_values=[result.uvars["slope"], result.uvars["intercept"], result.rsquared, t80_capped, lifetime_energy]
    else:
        result_values=[result.best_values["slope"], result.best_values["intercept"], result.rsquared, t80_capped, lifetime_energy]
    return result_values, result.best_fit

def exponential_params(power, times):
    exponential_model=lmfit.models.ExponentialModel()
    initial_params = exponential_model.guess(power, x=times)
    result = exponential_model.fit(power, initial_params, x=times)
    
    amplitude = result.best_values["amplitude"]
    decay = result.best_values["decay"]
    
    t80 = -decay*np.log(0.8)
    t80_capped = min(t80, times[-1])
    lifetime_energy = amplitude*decay*(1-np.exp(-t80_capped/decay)) #explicit solution to integral
    
    if result.errorbars:
        result_values=[result.uvars["amplitude"], result.uvars["decay"], result.rsquared, t80_capped, lifetime_energy]
    else:
        result_values=[result.best_values["amplitude"], result.uvars["decay"], result.rsquared, t80_capped, lifetime_energy]
    return result_values, result.best_fit

def biexponential_params(power, times):
    biexp_model = lmfit.models.ExponentialModel(prefix="exp1_") + lmfit.models.ExponentialModel(prefix="exp2_")
    #guess initial parameters, assume that decay consists of a dominant slow decay and a weaker fast decay
    initial_params = biexp_model.make_params(exp1_amplitude=power[0], 
                                             exp2_amplitude=power[0]/10, 
                                             exp1_decay=times[-1], 
                                             exp2_decay=times[-1]/10)
    result = biexp_model.fit(power, initial_params, x=times)
    
    tau_min = min(result.best_values["exp1_decay"], result.best_values["exp2_decay"])  # faster decay
    tau_max = max(result.best_values["exp1_decay"], result.best_values["exp2_decay"])  # slower decay
    tS = -tau_min * np.log(0.01)  # Use the fast decay for tS / burn-in-time
    Ts80 = -tau_max * np.log(0.8) # Use slow decay for Ts80
    tS_capped = min(tS, times[-1])
    Ts80_capped = min(Ts80, times[-1])
    lifetime_energy = (result.best_values["exp1_amplitude"]*result.best_values["exp1_decay"]*(1-np.exp(-Ts80_capped/result.best_values["exp1_decay"]))
                       +result.best_values["exp2_amplitude"]*result.best_values["exp2_decay"]*(1-np.exp(-Ts80_capped/result.best_values["exp2_decay"]))) #explicit solution for integral
    
    if result.errorbars:
        result_values=[result.uvars["exp1_amplitude"], result.uvars["exp1_decay"],
                       result.uvars["exp2_amplitude"], result.uvars["exp2_decay"],
                       result.rsquared, tS_capped, Ts80_capped, lifetime_energy]
    else:
        result_values=[result.best_values["exp1_amplitude"], result.best_values["exp1_decay"],
                       result.best_values["exp2_amplitude"], result.best_values["exp2_decay"],
                       result.rsquared, tS_capped, Ts80_capped, lifetime_energy]
    return result_values, result.best_fit

def logistic_params(power, times):
    log_exp_model = lmfit.Model(logistic_plus_exp)
    initial_params = log_exp_model.make_params(A=power[0]/2, 
                                               tau=times[-1], 
                                               L=power[0]/2, 
                                               k=times[-1]/5, 
                                               x0=times[-1]/2)
    result = log_exp_model.fit(power, initial_params, t=times)
    
    tS, time_extrapolate, pce_extrapolate = find_tS(times, result)
    PCE_tS = pce_extrapolate[np.where(time_extrapolate == tS)[0][0]]
    Ts80, _ = find_Ts80(pce_extrapolate, time_extrapolate, tS, PCE_tS)
    tS_capped = min(tS, times[-1])
    Ts80_capped = min(Ts80, times[-1])
    
    A = result.best_values["A"]
    tau = result.best_values["tau"]
    L = result.best_values["L"]
    k = result.best_values["k"]
    x0 = result.best_values["x0"]
    
    lifetime_energy = (A*tau*(1-np.exp(-Ts80_capped/tau)) #exponential part
                       +L/k*(np.log(1+np.exp(k*(Ts80_capped-x0))) - np.log(1+np.exp(-k*x0))) # logistic part
                      ) 
    
    #for some reason does not calculate errors
    if result.errorbars:
        result_values=[result.uvars["A"], result.uvars["tau"], 
                       result.uvars["L"], result.uvars["k"], 
                       result.uvars["x0"], result.rsquared, 
                       tS_capped, Ts80_capped, lifetime_energy]
    else:
        result_values=[A, tau, L, k, x0, result.rsquared, tS_capped, Ts80_capped, lifetime_energy]
    return result_values, result.best_fit

def erfc_params(power, times):
    erfc_model = lmfit.Model(erfc_linear)
    initial_params = erfc_model.make_params(PCE0=power[0], 
                                            k=times[-1]/10, 
                                            t0=times[-1]/2, 
                                            b=0)
    result = erfc_model.fit(power, initial_params, t=times)
    
    PCE0=result.best_values["PCE0"]
    k=result.best_values["k"]
    index_t80 = np.nonzero(np.diff(np.sign(result.best_fit-0.8*PCE0)))[0] #find the first index where the power falls below 80% of initial value
    if index_t80.size > 0:
        T80_composite = times[index_t80[0]]
    else:
        T80_composite = times[-1]
    T80_composite_capped = min(T80_composite, times[-1])
    # Calculate T80* from the linear part (PCE0 - k*t = 0.8*PCE0)
    T80_linear = (0.2 * PCE0) / k if k != 0 else None
    lifetime_energy = calculate_ley(erfc_linear, result.best_values.values(), T80_composite_capped)
    
    if result.errorbars:
        result_values=[result.uvars["PCE0"], result.uvars["k"], 
                       result.uvars["t0"], result.uvars["b"],
                       result.rsquared, T80_composite_capped, T80_linear, lifetime_energy]
    else:
        result_values=[result.best_values["PCE0"], result.best_values["k"], 
                       result.best_values["t0"], result.best_values["b"],
                       result.rsquared, T80_composite_capped, T80_linear, lifetime_energy]
    return result_values, result.best_fit

# ------------------------
# Utility Functions
# ------------------------

#lifetime energy from fitted function, output is in kWh/m^2 when input function uses the default W/cm^2 over hours
def calculate_ley(fit_function, params, t_end, t_start=0):
    integral, _ = quad(fit_function, t_start, t_end, args=tuple(params))
    ley = integral * 10
    return ley

#extrapolates the fitted curve by default 10 times the measurement time
def extrapolate(times, fit_results, time_limit=None):
    if time_limit:
        time_extrapolate = np.linspace(times[0], time_limit, 1000)#
    else: 
        time_extrapolate = np.linspace(times[0], 10*times[-1], 1000)
    pce_extrapolate = fit_results.eval(params=fit_results.params, t=time_extrapolate)
    return time_extrapolate, pce_extrapolate

#finds the first time where the power falls below the given fraction, by default the average of the 50 highest power values is taken as reference
def find_T80(times, power, reference_power=None, target_decay=0.8):
    if not reference_power:
        reference = np.mean(np.partition(power, -50)[-50:])
    else:
        reference = reference_power
    t80_index = numpy.argmax(power<=reference*target_decay) #argmax returns the first value for which the expression is true
    return times[t80_index]

# finds the global minimum, then finds the global maximum after that, fitted function is extrapolated to 10 times the measurement time
# exact motivation unknown
def find_tS(times, fit_results):
    time_extrapolate = np.linspace(times[0], 10 * times[-1], 1000)
    pce_extrapolate = fit_results.eval(params=fit_results.params ,t=time_extrapolate)

    min_idx = np.argmin(pce_extrapolate)
    tS_idx = min_idx + np.argmax(pce_extrapolate[min_idx:])
    tS = time_extrapolate[tS_idx]

    return tS, time_extrapolate, pce_extrapolate

def find_Ts80(pce_extrapolate, time_extrapolate, tS, PCE_tS):
    Ts80_value = 0.8 * PCE_tS
    tS_idx = np.where(time_extrapolate == tS)[0][0]
    Ts80_idx = np.where(pce_extrapolate[tS_idx:] <= Ts80_value)[0]

    if len(Ts80_idx) == 0:
        Ts80 = time_extrapolate[-1]
    else:
        Ts80_idx = tS_idx + Ts80_idx[0]
        Ts80 = time_extrapolate[Ts80_idx]

    return Ts80, time_extrapolate
