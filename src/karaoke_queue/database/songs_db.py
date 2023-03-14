from .db_base import *
from .db_writers import *

if __name__ == '__main__':
    setup_db()
    s = Song("Never gonna give you up", "rick astley", 6.9)
