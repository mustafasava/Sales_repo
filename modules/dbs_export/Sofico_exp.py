from sqlalchemy import create_engine, text,MetaData

def sofico_exp(x, y, month=None, year=None):

    if y == 1:
        try:
            # ✅ SQLite connection string (creates dist_native.db in the current folder)
            connection_string = "sqlite:///.\\DBs\\dist_native\\dist_native.db"
            engine = create_engine(connection_string)
            metadata = MetaData()
            metadata.reflect(bind=engine)
            sofico = metadata.tables["native_sofico"]
            
            for col in x.select_dtypes(include=["datetime64[ns]"]).columns:
                x[col] = x[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            with engine.begin() as conn:

                    conn.execute(text("PRAGMA journal_mode=WAL;"))
                    conn.execute(
                        text("DELETE FROM native_sofico WHERE month = :month AND year = :year"),
                        {"month": month, "year": year})
                    conn.execute(text("PRAGMA incremental_vacuum;"))
                    conn.execute(sofico.insert(), x.to_dict(orient="records"))
                    conn.execute(text("PRAGMA incremental_vacuum;"))
                    x = "Data Exported to Database Successfully."
                   
                    return x ,y,month,year

        except Exception as e:
            x= f"Error in exporting to Database : {e}"
            y=0
            return x,y
    else:
        return x,y
