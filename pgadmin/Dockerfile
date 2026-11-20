FROM dpage/pgadmin4:9

USER root

# RUN chown -R pgadmin:root /var/lib/pgadmin
# RUN chown -R pgadmin:root /var/log/pgadmin
RUN chown -R pgadmin:root /pgadmin4

COPY --chown=pgadmin:root ./servers.json /pgadmin4/servers.json

USER pgadmin