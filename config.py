class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://escoutid:s#rbp;Gvn6]NxYXHaT>V7&@escoutid.database.windows.net:1433/eScoutID?driver=ODBC+Driver+18+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "8PvUV36JVw59"
    UPLOAD_FOLDER = "uploads/"