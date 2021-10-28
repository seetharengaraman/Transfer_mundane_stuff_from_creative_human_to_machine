--If Fusion pipeline existing model evaluation condition fails, need to retrain model with all data

INSERT INTO `gcpproject1.OrderData.ProcessedOrderDetails`
SELECT
    * EXCEPT (ACTUAL_LABEL_VALUE), ACTUAL_LABEL_VALUE FULFILLMENT_DATE_IN_HOURS
    FROM
      `gcpproject1.OrderData.ShipDateInstances`

CREATE OR REPLACE MODEL
  `gcpproject1.OrderData.ShipDateDeterminationBQModel` OPTIONS(model_type='AUTOML_REGRESSOR',
               input_label_cols=['FULFILLMENT_DATE_IN_HOURS'],
               budget_hours=5.0,
               OPTIMIZATION_OBJECTIVE='MINIMIZE_RMSLE')
AS
SELECT * 
FROM `gcpproject1.OrderData.ProcessedOrderDetails`

SELECT
  *
FROM
  ML.EVALUATE(MODEL `gcpproject1.OrderData.ShipDateDeterminationBQModel`)

SELECT
  *
FROM
  ML.FEATURE_INFO(MODEL `gcpproject1.OrderData.ShipDateDeterminationBQModel`)
  
  
SELECT
  *
FROM
  ML.TRAINING_INFO(MODEL `gcpproject1.OrderData.ShipDateDeterminationBQModel`)
  
  --After testing on new data, export to storage for deployment
  
EXPORT MODEL `gcpproject1.OrderData.ShipDateDeterminationBQModel` OPTIONS(URI = 'gs://modelregistry/ShipDateEstimationModel')