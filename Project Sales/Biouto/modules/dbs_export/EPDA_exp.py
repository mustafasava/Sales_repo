from sqlalchemy import create_engine, text,MetaData

def epda_exp(x, y, month=None, year=None):  

    if y == 1:
        try:
            # ✅ SQLite connection string (creates dist_native.db in the current folder)
            connection_string = "sqlite:///.\\DBs\\dist_native\\dist_native.db"
            engine = create_engine(connection_string)
            metadata = MetaData()
            metadata.reflect(bind=engine)
            epda = metadata.tables["native_epda"]
            
            for col in x.select_dtypes(include=["datetime64[ns]"]).columns:
                x[col] = x[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            with engine.begin() as conn:

                    conn.execute(text("PRAGMA journal_mode=WAL;"))
                    conn.execute(
                        text("DELETE FROM native_epda WHERE month = :month AND year = :year"),
                        {"month": month, "year": year})
                    conn.execute(epda.insert(), x.to_dict(orient="records"))
                    x = "Data Exported to Database Successfully."
                   
                    return x ,y, month , year

        except Exception as e:
            x= f"Error in exporting to Database : {e}"
            y=0
            return x,y
    else:
        return x,y
