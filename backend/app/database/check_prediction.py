from mongodb import spread_predictions_collection

data = spread_predictions_collection.find_one()

print(data)