import torch
import torch.nn as nn

class LSTMModel(nn.Module):

    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            dropout=dropout,
            batch_first=True
        )
        
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        self.fc =  nn.Linear(hidden_size, output_size)

        print('## Modelo Iniciado ##')
        print(f'input_size = {input_size}, hidden_size = {hidden_size}, num_layers = {num_layers}, output_size = {output_size}')

    def forward(self, x):
        batch_size = x.size(0)

        # Inicialização dos tensores zerados
        h0_1 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0_1 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)

        out, _ = self.lstm(x, (h0_1, c0_1))
        out = out[:, -1, :]
        out = self.dropout(out)
        out = self.relu(out)

        out = self.fc(out)

        return out