class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@forumDatabase:3306/forum"
    REDIS_HOST = "localhost"
    REDIS_THREADS_LIST = "glasovi"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
