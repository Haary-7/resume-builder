FROM python:3.12-alpine AS builder
WORKDIR /build
COPY index.html release.py ./
RUN python release.py --out /site

FROM caddy:2-alpine
RUN addgroup -g 10001 studio && adduser -D -u 10001 -G studio studio \
    && mkdir -p /srv /config /data && chown -R studio:studio /srv /config /data
COPY --from=builder /site /srv
COPY Caddyfile /etc/caddy/Caddyfile
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
