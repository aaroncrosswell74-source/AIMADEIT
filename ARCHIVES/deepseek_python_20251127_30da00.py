# At the top of enforcement.py - REPLACE THIS:
# from app.db import get_pool

# WITH THIS:
from app.persistence import get_pool

# EVERYTHING ELSE STAYS EXACTLY THE SAME
# The interface is identical - zero code changes needed