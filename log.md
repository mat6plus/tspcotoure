2026-07-24T00:23:53.533Z The files belonging to this database system will be owned by user "postgres".
2026-07-24T00:23:53.533Z This user must also own the server process.
2026-07-24T00:23:53.534Z The database cluster will be initialized with locale "en_US.utf8".
2026-07-24T00:23:53.534Z The default database encoding has accordingly been set to "UTF8".
2026-07-24T00:23:53.534Z The default text search configuration will be set to "english".
2026-07-24T00:23:53.534Z Data page checksums are disabled.
2026-07-24T00:23:53.535Z fixing permissions on existing directory /var/lib/postgresql/data ... ok
2026-07-24T00:23:53.536Z creating subdirectories ... ok
2026-07-24T00:23:53.536Z selecting dynamic shared memory implementation ... posix
2026-07-24T00:23:53.586Z selecting default max_connections ... 100
2026-07-24T00:23:53.628Z selecting default shared_buffers ... 128MB
2026-07-24T00:23:53.741Z selecting default time zone ... UTC
2026-07-24T00:23:53.743Z creating configuration files ... ok
2026-07-24T00:23:53.946Z running bootstrap script ... ok
2026-07-24T00:23:54.210Z sh: locale: not found
2026-07-24T00:23:54.210Z 2026-07-24 00:23:54.210 UTC [35] WARNING:  no usable system locales were found
2026-07-24T00:23:54.922Z performing post-bootstrap initialization ... ok
2026-07-24T00:23:55.116Z syncing data to disk ... ok
2026-07-24T00:23:55.116Z initdb: warning: enabling "trust" authentication for local connections
2026-07-24T00:23:55.117Z initdb: hint: You can change this by editing pg_hba.conf or using the option -A, or --auth-local and --auth-host, the next time you run initdb.
2026-07-24T00:23:55.117Z Success. You can now start the database server using:
2026-07-24T00:23:55.117Z pg_ctl -D /var/lib/postgresql/data -l logfile start
2026-07-24T00:23:55.172Z waiting for server to start....2026-07-24 00:23:55.172 UTC [41] LOG:  starting PostgreSQL 16.14 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
2026-07-24T00:23:55.174Z 2026-07-24 00:23:55.173 UTC [41] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-07-24T00:23:55.179Z 2026-07-24 00:23:55.179 UTC [44] LOG:  database system was shut down at 2026-07-24 00:23:54 UTC
2026-07-24T00:23:55.187Z 2026-07-24 00:23:55.186 UTC [41] LOG:  database system is ready to accept connections
2026-07-24T00:23:55.248Z done
2026-07-24T00:23:55.248Z server started
2026-07-24T00:23:55.342Z CREATE DATABASE
2026-07-24T00:23:55.344Z /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
2026-07-24T00:23:55.346Z 2026-07-24 00:23:55.346 UTC [41] LOG:  received fast shutdown request
2026-07-24T00:23:55.349Z waiting for server to shut down....2026-07-24 00:23:55.349 UTC [41] LOG:  aborting any active transactions
2026-07-24T00:23:55.360Z 2026-07-24 00:23:55.360 UTC [41] LOG:  background worker "logical replication launcher" (PID 47) exited with exit code 1
2026-07-24T00:23:55.360Z 2026-07-24 00:23:55.360 UTC [42] LOG:  shutting down
2026-07-24T00:23:55.362Z 2026-07-24 00:23:55.361 UTC [42] LOG:  checkpoint starting: shutdown immediate
2026-07-24T00:23:55.406Z 2026-07-24 00:23:55.406 UTC [42] LOG:  checkpoint complete: wrote 926 buffers (5.7%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.019 s, sync=0.023 s, total=0.046 s; sync files=301, longest=0.013 s, average=0.001 s; distance=4283 kB, estimate=4283 kB; lsn=0/1925D68, redo lsn=0/1925D68
2026-07-24T00:23:55.414Z 2026-07-24 00:23:55.414 UTC [41] LOG:  database system is shut down
2026-07-24T00:23:55.447Z done
2026-07-24T00:23:55.447Z server stopped
2026-07-24T00:23:55.449Z PostgreSQL init process complete; ready for start up.
2026-07-24T00:23:55.474Z 2026-07-24 00:23:55.473 UTC [1] LOG:  starting PostgreSQL 16.14 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
2026-07-24T00:23:55.474Z 2026-07-24 00:23:55.474 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-07-24T00:23:55.474Z 2026-07-24 00:23:55.474 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-07-24T00:23:55.476Z 2026-07-24 00:23:55.476 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-07-24T00:23:55.481Z 2026-07-24 00:23:55.481 UTC [57] LOG:  database system was shut down at 2026-07-24 00:23:55 UTC
2026-07-24T00:23:55.488Z 2026-07-24 00:23:55.488 UTC [1] LOG:  database system is ready to accept connections
2026-07-24T00:28:55.580Z 2026-07-24 00:28:55.579 UTC [55] LOG:  checkpoint starting: time
2026-07-24T00:28:59.804Z 2026-07-24 00:28:59.804 UTC [55] LOG:  checkpoint complete: wrote 45 buffers (0.3%); 0 WAL file(s) added, 0 removed, 0 recycled; write=4.218 s, sync=0.003 s, total=4.226 s; sync files=12, longest=0.002 s, average=0.001 s; distance=261 kB, estimate=261 kB; lsn=0/19671A0, redo lsn=0/1967168