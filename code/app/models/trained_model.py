from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, ObjectIdField, StringField, IntField, FloatField

class Calibration(EmbeddedDocument):
    batch_size = IntField()
    time_steps = IntField()
    input_size = IntField()
    hidden_size = IntField()
    num_layers = IntField()
    dropout = FloatField()
    output_size = IntField()
    epochs = IntField()
    learning_rate = FloatField()
    step_size = IntField()
    gamma = FloatField()
    
    def to_dict(self):
        return {
            'batch_size': self.batch_size,
            'time_steps': self.time_steps,
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'output_size': self.output_size,
            'epochs': self.epochs,
            'learning_rate': self.learning_rate,
            'step_size': self.step_size,
            'gamma': self.gamma

        }

class Metrics(EmbeddedDocument):
    mse_loss = FloatField()

    def to_dict(self):
        return {
            'mse_loss': self.mse_loss
        }

class TrainedModel(Document):
    name = StringField(required=True, unique=True)
    symbol = StringField(required=True, unique=True)
    status = StringField(required=True)
    start_date = StringField(required=True)
    end_date = StringField(required=True)
    calibration = EmbeddedDocumentField(Calibration)
    metrics = EmbeddedDocumentField(Metrics)

    def to_dict(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'status': self.status,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'calibration': self.calibration.to_dict(),
            'metrics': self.metrics.to_dict()

        }

