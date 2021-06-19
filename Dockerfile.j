FROM substrate-study-contract-builder
LABEL maintainer Thomas Radloff <bostontrader@gmail.com>

# 1. Create the j contract.

# 1.1 Create the contract
RUN git clone https://github.com/bostontrader/j
WORKDIR j

# 1.2 Use this cargo config file to help with firewalls and proxy woes.
COPY config.toml /root/.cargo

# 1.2 Test it
RUN ~/.cargo/bin/cargo +nightly test

# 1.3 Compile to wasm
RUN ~/.cargo/bin/cargo +nightly contract build

FROM ubuntu:20.04
COPY --from=0 /j/target/ink/j.wasm /root/j.wasm
COPY --from=0 /j/target/ink/metadata.json /root/metadata.json
