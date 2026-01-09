
from app.resources import queue
from app.tasks.lstm import LSTMTrainingTask
from flask_jwt_extended import jwt_required
from flask import request
from flask_restful import Resource
from flasgger import swag_from
from rq import Retry
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import torch
import torch.nn as nn
import datetime
from app.models.trained_model import TrainedModel, Calibration, Metrics
from app.models.lstm_model import LSTMModel

class LSTMPredict(Resource):
    @jwt_required()
    @swag_from('../docs/lstm/predict.yml', methods=["GET"])
    def get(self):
        
        days = 20
        if request.args.get('days'):
            days = int(request.args.get('days').strip())

        if request.args.get('symbol'):
            symbol = request.args.get('symbol').strip()
        trainedModel = TrainedModel.objects(name=f'lstm_model_{symbol}',status='SUCCESS').first()

        if not trainedModel:
            return { 'status': 404, 'message' : 'Modelo não encontrado.'}, 404

        loaded_model = LSTMModel(
            input_size=trainedModel.calibration.input_size,
            hidden_size=trainedModel.calibration.hidden_size,
            num_layers=trainedModel.calibration.num_layers,
            output_size=trainedModel.calibration.output_size,
            dropout=trainedModel.calibration.dropout
        )

        loaded_state_dict = torch.load(f'./mlruns/saved_models/lstm_model_{symbol}')
        loaded_model.load_state_dict(loaded_state_dict)

        loaded_model.eval()
        end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (datetime.datetime.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

        df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)
        features = df[['Close']].values

        # Normalizar com o mesmo scaler usado no treino
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(features)

        last_sequence = scaled[-days:]

        seq = last_sequence.copy()
        predictions = []
        prediction_dates = []
        feature_dates = df.index.strftime("%Y-%m-%d").tolist()


        for day in range(days):

            prediction_date = datetime.datetime.today() + datetime.timedelta(days=day-1)
            
            if prediction_date.weekday() < 5:
                prediction_dates.append(prediction_date.strftime("%Y-%m-%d"))
                input_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0)
                with torch.no_grad():
                    prediction = loaded_model(input_tensor)

                pred_value = prediction.tolist()

                real_close = scaler.inverse_transform(pred_value)
                predictions.append(real_close.tolist()[0])

                new_day = pred_value[0] 
                seq = np.vstack([seq[1:], new_day])  # desliza janela
            

        return {'details': {'days': days, 'symbol': symbol}, 'predictions': {'values': predictions, 'dates' : prediction_dates}, 'features': {'values': features.tolist(), 'dates' : feature_dates}}

class LSTMTrainedModelsList(Resource):
    @jwt_required()
    @swag_from('../docs/lstm/trained_models.yml', methods=["GET"])
    def get(self):
        try:
            filter = {}
            if request.args.get('symbol'):
                filter['symbol'] = request.args.get('symbol')
            if request.args.get('status'):
                filter['status'] = request.args.get('status')

            trainedModels = TrainedModel.objects(**filter)
            if not trainedModels:
                return { 'status': 404, 'message' : 'Modelos treinados não encontrado'}, 404
            
            return [trainedModel.to_dict() for trainedModel in trainedModels]
        except:
            return { 'status': 400, 'message' : 'Erro ao buscar os registros sobre modelos treinados'}, 400
        
class LSTMTraining(Resource):
    @jwt_required()
    @swag_from('../docs/lstm/training.yml', methods=["POST"])
    def post(self):
        try:
            body = request.get_json()
            symbols = ['DIS']
            start_date =  '2018-01-01'
            end_date = '2025-11-30'
            calibration = {
                "batch_size" :  64,
                "time_steps" :  10,
                "hidden_size" :  256,
                "num_layers" :  2,
                "dropout" :  0.5,
                "epochs" :  300,
                "learning_rate" :  0.0001,
                "step_size" : 30,
                "gamma" : 0.5
            }
            
            if body['symbols']:
                symbols =  body['symbols']
            
            if body['start_date']:
                start_date = body['start_date'].strip()
            
            if body['end_date']:
                end_date = body['end_date'].strip()

            if body['calibration']:
                calibration = body['calibration']
                calibration['input_size'] = 1
                calibration['output_size'] = 1
            
            jobs = []
            for symbol in symbols:
                trainedModel = TrainedModel.objects(name=f'lstm_model_{symbol}').first()

                if trainedModel:
                    trainedModel.status = 'IN_PROGRESS'
                    trainedModel.start_date = start_date
                    trainedModel.end_date = end_date
                    trainedModel.calibration = Calibration(**calibration)
                    trainedModel.metrics = Metrics(**{
                        "mse_loss" : None
                    })
                    trainedModel.save()
                else:
                    trainedModel = TrainedModel(
                        **{ 
                            "name": f'lstm_model_{symbol}',
                            "symbol": symbol,
                            "status": 'IN_PROGRESS',
                            "start_date": start_date,
                            "end_date": end_date,
                            "calibration" : Calibration(**calibration),
                            "metrics" : Metrics(**{
                                "mse_loss" : None
                            })
                        }
                    ).save()
                
                job = queue.enqueue(
                    LSTMTrainingTask,
                    args=(symbol, start_date, end_date, calibration),
                    retry=Retry(max=3), 
                    job_timeout=6000
                )
                jobs.append({'job_id': job.id, 'job_name': 'LSTMTrainingTask', 'product': symbol, 'start_date': start_date, 'end_date': end_date, 'calibration': calibration})
        
            return { 
                'status': 200, 
                'message' : 'Agendamento do treinamento realizado com sucesso', 
                'symbols': symbols, 
                'start_date': start_date, 
                'end_date': end_date, 
                'calibration': calibration, 
                'jobs': jobs 
            }, 200            
        except:
           return { 'status': 400, 'message' : 'Ocorreu um erro para iniciar o treinamento.'}, 400