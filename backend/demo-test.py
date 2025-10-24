from datetime import datetime

date_obj = datetime.strptime('2025-09-20', '%Y-%m-%d').date()
print(date_obj.month)
print(type(date_obj))
