import torch
import torch.nn.functional as F
import torch.optim as optim
import argparse
import torchquantum as tq
import random
import numpy as np

from torch.optim.lr_scheduler import CosineAnnealingLR
from torchpack.datasets.dataset import Dataset


# data is   cos(theta)|000> + e^(j * phi)sin(theta) |111>
# target is sin(2*theta) * cos(phi)
def gen_data(L, N):
    omega_0 = np.zeros([2 ** L], dtype='complex_')
    omega_0[0] = 1 + 0j
    omega_1 = np.zeros([2 ** L], dtype='complex_')
    omega_1[-1] = 1 + 0j
    states = np.zeros([N, 2 ** L], dtype='complex_')
    thetas = 2 * np.pi * np.random.rand(N)
    phis = 2 * np.pi * np.random.rand(N)

    for i in range(N):
        states[i] = np.cos(thetas[i]) * omega_0 + np.exp(1j * phis[i]) * np.sin(thetas[i]) * omega_1
    
    X = np.sin(2 * thetas) * np.cos(phis)

    return states, X


class RegressionDataset:
    def __init__(self, split, n_samples, n_wires):
        self.split = split
        self.n_samples = n_samples
        self.n_wires = n_wires
        self.states, self.Xlabel = gen_data(self.n_wires, self.n_samples)
    
    def __getitem__(self, index: int):
        instance = {'states': self.states[index],
                    'Xlabel': self.Xlabel[index]}
        return instance
    
    def __len__(self) -> int:
        return self.n_samples


class Regression(Dataset):
    def __init__(self, n_train, n_valid, n_wires):
        n_samples_dict = {
            'train': n_train,
            'valid': n_valid
        }
        super().__init__({
            split: RegressionDataset(
                split=split,
                n_samples = n_samples_dict[split],
                n_wires = n_wires
            )
            for split in ['train', 'valid']
        })


class QModel(tq.QuantumModule):
    def __init__(self, n_wires, n_blocks):
        super().__init__()
        self.n_wires = n_wires
        self.n_blocks = n_blocks
        self.u3_layers = tq.QuantumModuleList()
        self.cu3_layers = tq.QuantumModuleList()
        self.linear = torch.nn.Linear(self.n_wires, 1)
        for _ in range(n_blocks):
            self.u3_layers.append(tq.Op1QAllLayer(op=tq.U3,
                                                 n_wires=n_wires,
                                                 has_params=True,
                                                 trainable=True))
            self.cu3_layers.append(tq.Op2QAllLayer(op=tq.CU3,
                                                   n_wires=n_wires,
                                                   has_params=True,
                                                   trainable=True,
                                                   circular=True))
        self.measure = tq.MeasureAll(tq.PauliZ)
    
    def forward(self, q_device: tq.QuantumDevice, input_states: torch.tensor):
        '''this forward function is different than other forward function that it has a input_states parameter
           set_states(input_state) is like the encoder part of the quantum neural networks
        '''
        q_device.set_states(input_states)
        for k in range(self.n_blocks):
            self.u3_layers[k](q_device)
            self.cu3_layers[k](q_device)
        x = self.measure(q_device)
        # x = self.linear(x)
        return x


def train(dataflow, q_device, model, device, optimizer):
    for feed_dict in dataflow['train']:
        inputs = feed_dict['states'].to(device).to(torch.complex64)
        targets = feed_dict['Xlabel'].to(device).to(torch.float)
        # targets = feed_dict['Xlabel'].to(device).to(torch.float).unsqueeze(dim=-1)

        outputs = model(q_device, inputs)

        loss = F.mse_loss(outputs[:, 2], targets)
        # loss = F.mse_loss(outputs, targets)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(f'loss: {loss.item()}')


def valid_test(dataflow, q_device, split, model, device):
    target_all = []
    output_all = []
    with torch.no_grad():
        for feed_dict in dataflow[split]:
            inputs = feed_dict['states'].to(device).to(torch.complex64)
            targets = feed_dict['Xlabel'].to(device).to(torch.float)
            # targets = feed_dict['Xlabel'].to(device).to(torch.float).unsqueeze(dim=-1)

            outputs = model(q_device, inputs)

            target_all.append(targets)
            output_all.append(outputs)
        target_all = torch.cat(target_all, dim=0)
        output_all = torch.cat(output_all, dim=0)
    
    loss = F.mse_loss(output_all[:, 2], target_all)
    # loss = F.mse_loss(output_all, target_all)
    global_loss.append(round(loss.item(), 8))
    print(f'{split} set loss: {loss}')


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--pdb', action='store_true', help='debug with pdb')
    parser.add_argument('--bsz', type=int, default=32, help='batch size for training and validation')
    parser.add_argument('--n_wires', type=int, default=3, help='number of qubits')
    parser.add_argument('--n_blocks', type=int, default=2, help='number of blocks, each contain one layer of U3 gates and one layer of CU3 with ring connections')
    parser.add_argument('--n_train', type=int, default=300, help='number of training samples')
    parser.add_argument('--n_valid', type=int, default=1000, help='number of validation samples')
    parser.add_argument('--epochs', type=int, default=100, help='number of training epochs')

    args = parser.parse_args()

    seed = 0
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    dataset = Regression(
        n_train=args.n_train,
        n_valid=args.n_valid,
        n_wires=args.n_wires,
    )

    dataflow = dict()

    for split in dataset:
        if split == 'train':
            sampler = torch.utils.data.RandomSampler(dataset[split])
        else:
            sampler = torch.utils.data.SequentialSampler(dataset[split])

        dataflow[split] = torch.utils.data.DataLoader(
                dataset[split],
                batch_size=args.bsz,
                sampler=sampler,
                num_workers=1,
                pin_memory=True
        )

    use_cuda = torch.cuda.is_available()
    device = torch.device('cuda' if use_cuda else 'cpu')

    model = QModel(n_wires=args.n_wires, n_blocks=args.n_blocks).to(device)

    n_epochs = args.epochs
    optimizer = optim.Adam(model.parameters(), lr=5e-3, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=n_epochs)

    q_device = tq.QuantumDevice(n_wires=args.n_wires)
    q_device.reset_states(bsz=args.bsz)

    for epoch in range(1, n_epochs + 1):
        # train
        print(f"Epoch {epoch}, RL : {optimizer.param_groups[0]['lr']}")
        train(dataflow, q_device, model, device, optimizer)
        # valid
        valid_test(dataflow, q_device, 'valid', model, device)
        scheduler.step()
    #  final valid
    valid_test(dataflow, q_device, 'valid', model, device)
    print(global_loss)

if __name__ == '__main__':
    global_loss = []
    main()

# adding nn.torch.Linear(3, 1) will improve the performance
# [0.29367763, 0.19590528, 0.12953235, 0.08074664, 0.04652008, 0.02385373, 0.01064033, 0.00392685, 0.00123427, 0.00033958, 8.484e-05, 2.061e-05, 5.32e-06, 1.9e-06, 1.05e-06, 7.7e-07, 6.6e-07, 6.1e-07, 5.9e-07, 5.8e-07, 5.8e-07, 5.7e-07, 5.7e-07, 5.7e-07, 5.7e-07, 5.7e-07]


# [0.20337933, 0.11402227, 0.07417366, 0.05454806, 0.04009848, 0.03030339, 0.02378082, 0.01879381, 0.01514006, 0.01230007, 0.01033051, 0.00878016, 0.00751242, 0.00658152, 0.00580128, 0.00515501, 0.00465647, 0.0042327, 0.00386561, 0.00356475, 0.00324513, 0.00299065, 0.00276434, 0.00257213, 0.00237561, 0.00221107, 0.00205864, 0.00192067, 0.00180645, 0.00169476, 0.00159107, 0.00149702, 0.00140795, 0.00133704, 0.00125953, 0.00119878, 0.00113679, 0.00107965, 0.00102632, 0.0009768, 0.0009343, 0.00089344, 0.00085666, 0.00082194, 0.00078797, 0.00075626, 0.00073176, 0.00070656, 0.00068144, 0.00065755, 0.00063743, 0.00061642, 0.00059939, 0.0005801, 0.00056457, 0.00054936, 0.00053592, 0.00052239, 0.00051, 0.00049885, 0.00048864, 0.00047823, 0.00046831, 0.00045987, 0.00045228, 0.0004435, 0.00043638, 0.00042951, 0.0004228, 0.00041758, 0.00041226, 0.00040683, 0.00040249, 0.00039815, 0.00039417, 0.00039075, 0.00038751, 0.0003843, 0.0003814, 0.00037907, 0.00037625, 0.00037426, 0.00037235, 0.0003708, 0.00036924, 0.0003681, 0.00036699, 0.00036601, 0.00036526, 0.00036448, 0.00036374, 0.00036319, 0.00036272, 0.00036241, 0.00036219, 0.00036202, 0.00036194, 0.00036188, 0.00036186, 0.00036185, 0.00036185]