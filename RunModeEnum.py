from enum import Enum

class RunMode(Enum):
    CSV_CSV_TESTING = "csv_to_csv_testing"
    SQL_SQL_TESTING = "sql_to_sql_testing"
    CSV_SQL_TESTING = "csv_to_sql_testing"
    SQL_CSV_TESTING = "sql_to_csv_testing"
    CSV_CSV_FULL = "csv_to_csv_full"
    SQL_SQL_FULL = "sql_to_sql_full"
    CSV_SQL_FULL = "csv_to_sql_full"
    SQL_CSV_FULL = "sql_to_csv_full"

    def str(self) -> str:
        return self.value