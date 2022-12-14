FROM rust:1.65-bullseye

WORKDIR /usr/src/client
COPY . .

RUN #apt update && apt install pkg-config -y && rm -rf /var/lib/apt/lists/*

RUN cargo run --release
# RUN cargo install --path .

#CMD ["client"]