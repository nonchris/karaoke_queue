from karaoke_queue.database.db_base import *
from karaoke_queue.database.db_writers import *
from karaoke_queue.database.db_getters import *

# ensure DB exists
setup_db()

if __name__ == '__main__':
    setup_db()
    s = Song("Never gonna give you up", "rick astley", 6.9, 10)
