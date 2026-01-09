def get_schemas():
    return {
        "Message" : {
            "type": "object",
            "properties": {
                "status": { "type" : "string"},
                "message": { "type" : "string"}
            }
        },
        "Login" : {
            "type": "object",
            "properties": {
                "status": { "type" : "number"},
                "access_token": { "type" : "string"}
            }
        },
        "Calibration" : {
            "type": "object",
            "properties": {
                "batch_size": { "type" : "number"},
                "time_steps": { "type" : "number"},
                "input_size": { "type" : "number"},
                "hidden_size": { "type" : "number"},
                "num_layers": { "type" : "number"},
                "dropout": { "type" : "number"},
                "output_size": { "type" : "number"},
                "epochs": { "type" : "number"},
                "learning_rate": { "type" : "number"},
                "step_size": { "type" : "number"},
                "gamma": { "type" : "number"}
            }
        },
        "Metrics" : {
            "type": "object",
            "properties": {
                "mse_loss": { "type" : "number"}
            }
        },
        "TrainedModel" : {
            "type": "object",
            "properties": {
                "name": { "type" : "string"},
                "symbol": { "type" : "string"},
                "status": { "type" : "string"},
                "start_date": { "type" : "string"},
                "end_date": { "type" : "string"},
                'calibration': {
                    'type': 'object',
                    '$ref': '#/components/schemas/Calibration'
                },
                'metrics': {
                    'type': 'object',
                    '$ref': '#/components/schemas/Metrics'
                },
            }
        },
        "DataTraining" : {
            "type": "object",
            "properties": {
                "symbols": {
                    'type': 'array',
                    'items': { "type" : "string"}
                },
                "start_date": { "type" : "string"},
                "end_date": { "type" : "string"},
                'calibration': {
                    'type': 'object',
                    '$ref': '#/components/schemas/Calibration'
                }
            }
        },
        "Details" : {
            "type": "object",
            "properties": {
                "days": { "type" : "number"},
                "symbol": { "type" : "string"}
            }
        },
        "Predictions" : {
            "type": "object",
            "properties": {
                "values": {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': { "type" : "number"}
                    },
                },
                "dates": {
                    'type': 'array',
                    'items': { "type" : "string"}
                },
            }
        },
        "Features" : {
            "type": "object",
            "properties": {
                "values": {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': { "type" : "number"}
                    },
                },
                "dates": {
                    'type': 'array',
                    'items': { "type" : "string"}
                },
            }
        },
        "PredictInfos" : {
            "type": "object",
            "properties": {
                'details': {
                    'type': 'object',
                    '$ref': '#/components/schemas/Details'
                },
                'predictions': {
                    'type': 'object',
                    '$ref': '#/components/schemas/Predictions'
                },
                'features': {
                    'type': 'object',
                    '$ref': '#/components/schemas/Features'
                },
            }
        },
        "JobInfo" : {
            "type": "object",
            "properties": {
                "job_id": { "type" : "string"},
                "job_name": { "type" : "string"},
                "year": { "type" : "number"}
            }
        },
        "JobResponse" : {
            "type": "object",
            "properties": {
                "status": { "type" : "string"},
                "message": { "type" : "string"},
                "symbol": { "type" : "string"},
                "start_date": { "type" : "string"},
                "end_date": { "type" : "string"},
                'calibration': {
                        'type': 'object',
                        '$ref': '#/components/schemas/Calibration'
                    },
                'jobs': {
                        'type': 'array',
                        '$ref': '#/components/schemas/JobInfo'
                    },
            }
        }
    }