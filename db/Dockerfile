FROM postgres:latest

ENV POSTGRES_USER "postgres_user"
ENV POSTGRES_PASSWORD "postgres_password"
ENV POSTGRES_DB "postgres_db"
ENV PGDATA "/var/lib/postgresql/data/pgdata"

CMD ["postgres", "-c", "max_connections=1000",\
               "-c", "shared_buffers=256MB",\
               "-c", "effective_cache_size=768MB",\
               "-c", "maintenance_work_mem=64MB",\
               "-c", "checkpoint_completion_target=0.7",\
               "-c", "wal_buffers=16MB",\
               "-c", "default_statistics_target=100"]

