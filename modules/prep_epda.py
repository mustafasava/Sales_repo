from sqlalchemy import create_engine, text

def prep_epda(x,y,month=None,year=None):
    if y == 1:
        try:
            engine = create_engine("sqlite:///.\\DBs\\dist_native\\epda_db\\epda.db")

            with open(".\\DBs\\dist_native\\queries\\epda_prep.sql", "r", encoding="utf-8") as f:
                sql_query = f.read()

            with engine.begin() as conn:
                conn.execute(text("DELETE FROM prep_epda Where Month = :month AND Year = :year"),{"month": month, "year": year})
                conn.execute(text("PRAGMA incremental_vacuum;"))
                conn.execute(text(sql_query),{"month": month, "year": year})
                conn.execute(text("PRAGMA incremental_vacuum;"))
                x = f" {x} Data Prepared Successfully."
                return x,y
        except Exception as e:
            x = f"\n Error happened while preparing :\n Details : {e}"
            y=0
            return x,y
    else:
        return x,y
