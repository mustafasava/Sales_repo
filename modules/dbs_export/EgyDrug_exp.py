from sqlalchemy import create_engine, text,MetaData

def egydrug_exp(x, y, month=None, year=None):

    if y == 1:
        try:   
            for name,df in x.items():
             
            
                # ✅ SQLite connection string (creates dist_native.db in the current folder)
                connection_string = "sqlite:///.\\DBs\\dist_native\\egydrug_db\\egydrug.db"
                engine = create_engine(connection_string)
                metadata = MetaData()
                metadata.reflect(bind=engine)
                metav = metadata.tables[f"{name}"]
                
                for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
                    df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
                
                with engine.begin() as conn:

                        conn.execute(text("PRAGMA journal_mode=WAL;"))
                        conn.execute(
                            text(f"DELETE FROM {name} WHERE month = :month AND year = :year"),
                            {"month": month, "year": year})
                        conn.execute(text("PRAGMA incremental_vacuum;"))
                        conn.execute(metav.insert(), df.to_dict(orient="records"))
                        conn.execute(text("PRAGMA incremental_vacuum;"))
            x = "Data Exported to Database Successfully."
                   
            return x ,y, month , year
            
        except Exception as e:
            x= f"Error in exporting to Database : {e}"
            y=0
            return x,y
    else:
        return x,y