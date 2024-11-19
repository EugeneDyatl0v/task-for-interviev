FROM python:3.12

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN apt-get update; \
        apt-get install -y cron;

COPY contrib/docker/cron_app/cron_scripts/crontab /etc/cron.d/crontab_1
COPY ./ /app/

RUN set -eux; \
    chmod 0744 /app/contrib/docker/cron_app/cron_scripts/delete_conf_codes.sh \
    && chmod 0644 /etc/cron.d;

RUN set -eux; \
        crontab /etc/cron.d/crontab_1

RUN touch /var/log/cron.log

CMD ["cron",  "-f"]