from flat_game import carmunk
import numpy as np
import random
import csv
from nn import neural_net, LossHistory
import os.path
import timeit

NUM_INPUT = 2
GAMMA = 0.9  
TUNING = False  

def train_net(model, params):

    filename = params_to_filename(params)

    observe = 1000  # Number of frames to observe before training.
    epsilon = 1
    train_frames = 100000  # Number of frames to play.
    batchSize = params['batchSize']
    buffer = params['buffer']

    
    max_car_distance = 0
    car_distance = 0
    t = 0
    data_collect = []
    replay = []  

    loss_log = []

    # Create a new game instance.
    game_state = carmunk.GameState()
    _, state = game_state.frame_step((2))

    
    start_time = timeit.default_timer()

    
    while t < train_frames:

        t += 1
        car_distance += 1

        # Choose an action.
        if random.random() < epsilon or t < observe:
            action = np.random.randint(0, 3)  
        else:
            
            qval = model.predict(state, batch_size=1)
            action = (np.argmax(qval))  # best
            reward, new_state = game_state.frame_step(action)

        
        replay.append((state, action, reward, new_state))

        
        if t > observe:
            if len(replay) > buffer:
                replay.pop(0)

            # Randomly sample our experience replay memory
            minibatch = random.sample(replay, batchSize)

            
            X_train, y_train = process_minibatch2(minibatch, model)

            
            history = LossHistory()
            model.fit(
                X_train, y_train, batch_size=batchSize,
                epochs=1, verbose=0, callbacks=[history]
            )
            loss_log.append(history.losses)

        
        state = new_state

        
        if epsilon > 0.1 and t > observe:
            epsilon -= (1.0/train_frames)

        
        if reward == -500:
            
            data_collect.append([t, car_distance])

            
            if car_distance > max_car_distance:
                max_car_distance = car_distance

            
            tot_time = timeit.default_timer() - start_time
            fps = car_distance / tot_time

            
            print("Max: %d at %d\tepsilon %f\t(%d)\t%f fps" %
                  (max_car_distance, t, epsilon, car_distance, fps))

            
            car_distance = 0
            start_time = timeit.default_timer()

        
        if t % 25000 == 0:
            model.save_weights('saved-models/' + filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model %s - %d" % (filename, t))

    
    log_results(filename, data_collect, loss_log)


def log_results(filename, data_collect, loss_log):
    with open('results/sonar-frames/learn_data-' + filename + '.csv', 'w') as data_dump:
        wr = csv.writer(data_dump)
        wr.writerows(data_collect)

    with open('results/sonar-frames/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
        for loss_item in loss_log:
            wr.writerow(loss_item)

def process_minibatch2(minibatch, model):
    # by Microos, improve this batch processing function 
    #   and gain 50~60x faster speed (tested on GTX 1080)
    #   significantly increase the training FPS
    
  

    mb_len = len(minibatch)

    old_states = np.zeros(shape=(mb_len, 2))
    actions = np.zeros(shape=(mb_len,))
    rewards = np.zeros(shape=(mb_len,))
    new_states = np.zeros(shape=(mb_len, 2))

    for i, m in enumerate(minibatch):
        old_state_m, action_m, reward_m, new_state_m = m
        old_states[i, :] = old_state_m[...]
        actions[i] = action_m
        rewards[i] = reward_m
        new_states[i, :] = new_state_m[...]

    old_qvals = model.predict(old_states, batch_size=mb_len)
    new_qvals = model.predict(new_states, batch_size=mb_len)

    maxQs = np.max(new_qvals, axis=1)
    y = old_qvals
    non_term_inds = np.where(rewards != -500)[0]
    term_inds = np.where(rewards == -500)[0]

    y[non_term_inds, actions[non_term_inds].astype(int)] = rewards[non_term_inds] + (GAMMA * maxQs[non_term_inds])
    y[term_inds, actions[term_inds].astype(int)] = rewards[term_inds]

    X_train = old_states
    y_train = y
    return X_train, y_train

def process_minibatch(minibatch, model):
    """This does the heavy lifting, aka, the training. It's super jacked."""
    X_train = []
    y_train = []
    
    for memory in minibatch:
        
        old_state_m, action_m, reward_m, new_state_m = memory
        
        old_qval = model.predict(old_state_m, batch_size=1)
        # Get prediction on new state.
        newQ = model.predict(new_state_m, batch_size=1)
        # Get our predicted best move.
        maxQ = np.max(newQ)
        y = np.zeros((1, 3))
        y[:] = old_qval[:]
        
        if reward_m != -500:  
            update = (reward_m + (GAMMA * maxQ))
        else:  # terminal state
            update = reward_m
        
        y[0][action_m] = update
        X_train.append(old_state_m.reshape(NUM_INPUT,))
        y_train.append(y.reshape(3,))

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train


def params_to_filename(params):
    return str(params['nn'][0]) + '-' + str(params['nn'][1]) + '-' + \
            str(params['batchSize']) + '-' + str(params['buffer'])


def launch_learn(params):
    filename = params_to_filename(params)
    print("Trying %s" % filename)
    
    if not os.path.isfile('results/sonar-frames/loss_data-' + filename + '.csv'):
        
        open('results/sonar-frames/loss_data-' + filename + '.csv', 'a').close()
        print("Starting test.")
        # Train.
        model = neural_net(NUM_INPUT, params['nn'])
        train_net(model, params)
    else:
        print("Already tested.")


if __name__ == "__main__":
    if TUNING:
        param_list = []
        nn_params = [[164, 150], [256, 256],
                     [512, 512], [1000, 1000]]
        batchSizes = [40, 100, 400]
        buffers = [10000, 50000]

        for nn_param in nn_params:
            for batchSize in batchSizes:
                for buffer in buffers:
                    params = {
                        "batchSize": batchSize,
                        "buffer": buffer,
                        "nn": nn_param
                    }
                    param_list.append(params)

        for param_set in param_list:
            launch_learn(param_set)

    else:
        nn_param = [128, 128]
        params = {
            "batchSize": 64,
            "buffer": 50000,
            "nn": nn_param
        }
        model = neural_net(NUM_INPUT, nn_param)
        train_net(model, params)


