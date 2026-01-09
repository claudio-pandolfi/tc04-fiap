
import yfinance as yf
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import mlflow
import mlflow.pytorch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from app.models.trained_model import TrainedModel, Metrics 
from app.models.lstm_model import LSTMModel

mlflow.set_tracking_uri("file:./mlruns")
device = torch.device("cpu")

def generateSequences(dataset, time_steps=20):
    print(f'# Gerar sequencias para treinamento #')
    X, y = [], []
    for i in range(len(dataset) - time_steps):
        X.append(dataset[i:i+time_steps])
        y.append(dataset[i+time_steps]) 
    return torch.tensor(np.array(X), dtype=torch.float32) , torch.tensor(np.array(y), dtype=torch.float32)


def LSTMTrainingTask(symbol, start_date, end_date, calibration):
    print(f'################# Treinamento do Modelo - ACAO {symbol} #################')
    print(f'Data de início / fim: {start_date} / {end_date} ')
    print(f'Dados de Calibração {calibration}')
    
    trainedModel = TrainedModel.objects(name=f'lstm_model_{symbol}').first()

    df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaledDf = scaler.fit_transform(df[['Close']].values)

    # scaledDf = MinMaxScaler().fit_transform(df[['Open', 'High', 'Low', 'Close', 'Volume']].values)

    print('# Gerar as sequencias para a realização dos testes #')
    X, y = generateSequences(scaledDf, time_steps=calibration['time_steps'])

    print('# Separação dos dados de treinamento e testes #')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    train_loader = DataLoader(dataset=train_dataset, batch_size=calibration['batch_size'], shuffle=True)
    test_loader = DataLoader(dataset=test_dataset, batch_size=calibration['batch_size'], shuffle=False)

    print('# Carregamento do Modelo LSTM #')
    model = LSTMModel(
        input_size=calibration['input_size'],
        hidden_size=calibration['hidden_size'],
        num_layers=calibration['num_layers'],
        output_size=calibration['output_size'],
        dropout=calibration['dropout']
    ).to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=calibration['learning_rate'])
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=calibration['step_size'], gamma=calibration['gamma'])

    mlflow.set_experiment("LSTM_Stock_Prediction")

    with mlflow.start_run():
        
        for epoch in range(calibration['epochs']):
            model.train()
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

            scheduler.step()

            model.eval()
            with torch.no_grad():
                test_preds = model(X_test)
                test_loss = criterion(test_preds, y_test).item()

            print(f"Epoch [{epoch+1}/{calibration['epochs']}], Train Loss: {loss.item():.4f}, Test Loss: {test_loss:.4f}")

            mlflow.log_metric("train_loss", loss.item(), step=epoch)
            mlflow.log_metric("test_loss", test_loss, step=epoch)

        mlflow.pytorch.log_model(model, name=f'lstm_model_{symbol}')
        torch.save(model.state_dict(), f'./mlruns/saved_models/lstm_model_{symbol}')

        model.eval()
        test_loss = 0.0
        with torch.no_grad():
            for sequences, labels in test_loader:
                sequences, labels = sequences.to(device), labels.to(device)
                outputs = model(sequences)
                loss = criterion(outputs, labels)
                test_loss += loss.item()

        average_test_loss = test_loss / len(test_loader)
        print(f"Test Loss: {average_test_loss:.4f}")
        mlflow.log_metric("test_loss", average_test_loss)
        
        trainedModel.status = 'SUCCESS'
        trainedModel.metrics = Metrics(**{
            "mse_loss" : average_test_loss
        })

        trainedModel.save()
    return 'Finalizado com sucesso!'
