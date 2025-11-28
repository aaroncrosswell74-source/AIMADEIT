# At the top of admin.py - REPLACE THIS:
# from app.db import get_pool
# from init_db import MockConnection  # REMOVE THIS LINE

# WITH THIS:
from app.persistence import get_pool

# Remove any MockConnection references - they're handled automatically