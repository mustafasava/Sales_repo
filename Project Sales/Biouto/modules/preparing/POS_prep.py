from sqlalchemy import create_engine, text

def pos_prep(x,y,month=None,year=None):
    if y == 1:
        try:
            engine = create_engine("sqlite:///.\\DBs\\dist_native\\dist_native.db")

            with open(".\\DBs\\dist_native\\queries\\pos_prep.sql", "r", encoding="utf-8") as f:
                sql_query = f.read()

            with engine.begin() as conn:
                conn.execute(text("DELETE FROM prep_pos Where Month = :month AND Year = :year"),{"month": month, "year": year})
                conn.execute(text(sql_query))
                x = f" {x} Data Prepared Successfully."
                return x,y
        except Exception as e:
            x = f"\n Error happened while preparing :\n Details : {e}"
            y=0
            return x,y
    else:
        return x,y
