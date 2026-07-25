from mongodb import ocr_history_collection

data = ocr_history_collection.find_one()

print(data)