FROM rust:1.93.0-alpine3.23 AS base

FROM base AS builder

WORKDIR /app

COPY ./apps/renderer/src/ src/
COPY ./apps/renderer/Cargo.toml ./apps/renderer/Cargo.lock ./
RUN cargo build --release
COPY ./apps/renderer/exports/ exports/
COPY ./apps/renderer/fonts/ fonts/


FROM builder AS runner

WORKDIR /app


ENTRYPOINT [ "./target/release/statalytics-renderer" ]
