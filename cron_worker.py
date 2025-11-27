from database.db import init_db
from background_worker import check_prices_cycle

if __name__ == "__main__":
    init_db()
    check_prices_cycle()
