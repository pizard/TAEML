import numpy as np 
import os 
import time 
import pdb
try: 
    import cPickle as pickle
except:
    import pickle

DATASET_SIZE = {'awa2': int(37322*0.8), 
        'mnist': 70000, 'cub200_2011': 11788,
        'omniglot': int(32460*0.8), 'caltech101': 9144, 
        'caltech256': int(30607*0.8), 'cifar100': int(60000*0.8), 
        'cifar10': 60000, 'voc2012': 11540, 
        'miniImagenet': int(60000*0.64), 'tiered_full': 448695,
        'tiered_sub0': 78269, 'tiered_sub1': 101752,
        'tiered_sub2': 163049, 'tiered_sub3': 105625,
        'multiple': int(37322*0.8) + int(60000*0.8) \
                + int(32460*0.8) + 11540 + 60000}

#TRAIN_DATASET = ['awa2', 'cifar100', 'omniglot', 'voc2012', 'caltech256']
#TEST_DATASET = ['mnist', 'cub200_2011', 'cifar10', 'caltech101', 'miniImagenet'] 
#VALIDATION_DATASET = ['awa2', 'cifar100', 'omniglot', 'caltech256']

class EpisodeGenerator(): 
    def __init__(self, data_dir, phase, config):
        if phase == 'train': 
            self.dataset_list = config['TRAIN_DATASET']
        elif phase == 'test':
            self.dataset_list = config['TEST_DATASET']
        elif phase == 'val': 
            self.dataset_list = config['VALIDATION_DATASET']
        else:
            raise ValueError('select one from train/test/val')

        self.data_root = data_dir
        self.dataset = {}
        self.data_all = []
        self.y_all = []
        self.dataset_size = DATASET_SIZE
        self.phase = phase
        for i, dname in enumerate(self.dataset_list): 
            load_dir = os.path.join(data_dir, phase,
                    dname+'.npy')
            self.dataset[dname] = np.load(load_dir)
        
    def get_episode(self, nway, kshot, qsize, 
            dataset_name=None, 
            onehot=True, 
            printname=False, 
            if_singleq=False,
            normalize=True):
        
        if (dataset_name is None) or (dataset_name=='multiple'):
            dataset_name = self.dataset_list[np.random.randint(len(self.dataset_list))] 
        if printname:
            print (dataset_name)
        dd = self.dataset[dataset_name]
        random_class = np.random.choice(len(dd), size=nway, replace=False)
        support_set_data = []; query_set_data = []
        support_set_label = []; query_set_label = []
        
        for n, rnd_c in enumerate(random_class):
            data = dd[rnd_c]
            rnd_ind = np.random.choice(len(data), size=kshot+qsize, replace=False)
            rnd_data = data[rnd_ind]

            label = np.array([n for _ in range(kshot+qsize)])
            support_set_data += [r for r in rnd_data[:kshot]]
            support_set_label += [l for l in label[:kshot]]

            query_set_data += [r for r in rnd_data[kshot:]] 
            query_set_label += [l for l in label[kshot:]]

        support_set_data = np.reshape(support_set_data, 
                [-1] + list(rnd_data.shape[1:]))
        query_set_data = np.reshape(query_set_data,
                [-1] + list(rnd_data.shape[1:]))

        if normalize:
            support_set_data = support_set_data.astype(float) / 255.
            query_set_data = query_set_data.astype(float) / 255.
        
        if onehot:
            s_1hot = np.zeros([nway*kshot, nway])
            s_1hot[np.arange(nway*kshot), support_set_label] = 1
            q_1hot = np.zeros([nway*qsize, nway]) 
            q_1hot[np.arange(nway*qsize), query_set_label] = 1
            support_set_label = s_1hot
            query_set_label = q_1hot
        
        if if_singleq: 
            single_ind = np.random.randint(len(query_set_data))
            query_set_data = query_set_data[np.newaxis,single_ind]
            query_set_label = query_set_label[np.newaxis,single_ind]

        return support_set_data, support_set_label, query_set_data, query_set_label


if __name__ == '__main__': 
    epgen = EpisodeGenerator('../../datasets', 'test')
    st = time.time()
    dset = 'cifar10'
    for i in range(10):
        epgen.get_random_batch(16, onehot=False)

    print ('time consumed for {} : {:.3f}'.format(dset, time.time()-st))
