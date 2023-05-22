# 1+ upper, 1+ lower, 1+ number, 1+ special (@$!%*?&), 8-50 char
PASSWORD = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,50}$'

# snake case with dunders
ERROR_RESPONSE = r'^[a-z0-9]+(?:_{1,2}[a-z0-9]+)*$'

UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
