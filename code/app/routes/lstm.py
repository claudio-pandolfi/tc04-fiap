from app.resources.lstm import LSTMTraining, LSTMPredict, LSTMTrainedModelsList

def lstm_routes(api):
    api.add_resource(LSTMTraining, '/lstm/training')
    api.add_resource(LSTMPredict, '/lstm/predict')
    api.add_resource(LSTMTrainedModelsList, '/lstm/trained_models')