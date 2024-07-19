import numpy as np
# -*- coding: utf-8 -*-
"""the speed prediction model: estimate the predicted speed for target RS"""
#def getSpeed(RS, RS_Kjam, speed_result, vehicle, footprint, current_time, depart_time):
def getSpeed(RS, speed_result, current_time, depart_time, model, predicted_speeds):
    # __5___10----
    PastTime = 3
    Pred_limit = 6
    pred_num = int((depart_time - current_time)/300) + 1
    temp_pastspeed_list = speed_result[RS]
    pred_len = len(predicted_speeds[RS])

    #if len(temp_pastspeed_list) % 5 !=0:
    #    print("temp_pastspeed_list is changed")
    #    exit(0)
    #else:
    #   print("ok")
    #print("depart_time: ",depart_time)
    #print("current_time: ",current_time)
    #print("pred_num: ",pred_num)
    #print("Now speed: ",past_speed_list[-1:][0])
    #print("before predicted: ",past_speed_list[-1:])
    if pred_len >= pred_num: #Not need to predict again
        pred_inst = predicted_speeds[RS][pred_num-1]
        return pred_inst , predicted_speeds
    else: 
        error = pred_num - pred_len

        X = [[[13.89]*1 for i in range(PastTime)]]
        past_speed_list = temp_pastspeed_list + predicted_speeds[RS]
        if len(past_speed_list) < PastTime :
            new_idx = PastTime-len(past_speed_list)
            for idx,i in enumerate(past_speed_list):
                X[0][new_idx][0] = i
                new_idx +=1
        else:
            for idx,i in enumerate(past_speed_list[-PastTime:]):
                X[0][idx][0] = i
                
        if pred_num > Pred_limit:
            error = Pred_limit - pred_len
            if error == 0:
                pred_inst = predicted_speeds[RS][pred_len-1]
                return pred_inst , predicted_speeds
            elif error <0:
                print("negative")
                exit(0)

        for i in range(error):
            #print("enter prediction")
            X_nparry = np.array(X)
            pred_inst = model.predict(np.array(X_nparry))
            # predict next , so move data forward
            for j in range(PastTime-1):
              X[0][j][0] = X[0][j+1][0]
            
            X[0][PastTime-1][0] = pred_inst[0][0].tolist()
            #print("Predict Speed: ", pred_inst[0][0].tolist())
            predicted_speeds[RS].append(pred_inst[0][0].tolist())
            #print("after predicted: ",pred_inst[0][0])

    return pred_inst[0][0].tolist() ,predicted_speeds


"""the TL prediction model: estimate the queuing time before leaving the target RS"""
def getQueuingTime(arriving_time, RS, RS_Length, TL, phase_list):
    
    leaveTime_of_one_veh = 2.5 
        
    #TL_id = TL[0]
    index = int(TL[1])
    Tc = 0 # cycle
    Tp = 0 # green phase + yellow phase
    state_cycle = "" 
    Ts = 0 # timing plan StartTime (first green phase start time)
    """estimate Tc and Tp"""
    for phase in phase_list:
        
        Tc = Tc + int(phase[0])
        if phase[1][index] == "G" or phase[1][index] == "g" or phase[1][index] == "y":
            Tp = Tp + int(phase[0])
        state_cycle = state_cycle + phase[1][index]
    
    
    if state_cycle.find("r") == -1:
        return 0
        
    """estimate Ts"""
    
    first_green_phase_pos = min(state_cycle.find("G"),state_cycle.find("g"))
    
    if first_green_phase_pos == -1:
        first_green_phase_pos = max(state_cycle.find("G"),state_cycle.find("g"))
    if first_green_phase_pos == 0:
        Ts = 0
    else:        
        
        for i in range(first_green_phase_pos):
            Ts = Ts + int(phase_list[i][0])
            
    """estimate queuing_time"""
    remain_red_phase = 0
    accumulate_veh = 0
    
    if arriving_time < Ts:
        remain_red_phase = Ts - arriving_time
        elapsed_red_phase = (Tc - Tp) - remain_red_phase
        #if RS not in RS_acc:
            
        accumulate_veh = elapsed_red_phase * 0.15
            
        if accumulate_veh > RS_Length/7.5:
             accumulate_veh = RS_Length/7.5                
        #else:
        #    accumulate_veh = estimateAccumulateVeh(RS, elapsed_red_phase)
            
        RS_queuing_time = remain_red_phase + (accumulate_veh * leaveTime_of_one_veh)
               
    else:
       
        time_in_this_period = (arriving_time - Ts) % Tc
        #red phase
        if time_in_this_period > Tp:
            remain_red_phase = Tc - time_in_this_period
            elapsed_red_phase = (Tc - Tp) - remain_red_phase
            #if RS not in RS_acc:               
            accumulate_veh = elapsed_red_phase * 0.15
            if accumulate_veh > RS_Length/7.5:
                accumulate_veh = RS_Length/7.5                
            #else:
            #    accumulate_veh = estimateAccumulateVeh(RS, elapsed_red_phase)
                
            RS_queuing_time = remain_red_phase + (accumulate_veh * leaveTime_of_one_veh)
        #green phase
        else:
            RS_queuing_time = 0
            
    #print("remain_red_phase:",remain_red_phase)
    #print("accumulate_veh:",accumulate_veh)
    return RS_queuing_time

"""estimate the average number of vehicles accumulated in the queue """
def estimateAccumulateVeh(RS, elapsed_red_phase):
    
    time_interval = 5 
    idx = int(elapsed_red_phase/time_interval)
    x = elapsed_red_phase % time_interval
    
    
    if idx >= len(RS_acc[RS])-1:
        y1 = RS_acc[RS][-1]
        y2 = RS_acc[RS][-1]
    else:    
        y1 = RS_acc[RS][idx]
        y2 = RS_acc[RS][idx+1]
        
    y = (y2-y1)/time_interval*x + y1
    
   
    return y




