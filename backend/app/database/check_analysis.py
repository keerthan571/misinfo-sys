from mongodb import analyses_collection

data = analyses_collection.find_one()

print(data)