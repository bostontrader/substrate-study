FROM ubuntu:20.04
LABEL maintainer Thomas Radloff <bostontrader@gmail.com>

# 0. In the beginning...
RUN apt update
RUN apt install -y --no-install-recommends \
    ca-certificates \
    clang \
    curl \
    git \
    libssl-dev libudev-dev \
    llvm

# 1. https://substrate.dev/docs/en/knowledgebase/getting-started/

# This is the rust installation from rust and we to do some sourcing via
# .bashrc so that we have rust commands in the path in subsequent bash sessions.
# See https://stackoverflow.com/questions/49676490/when-installing-rust-toolchain-in-docker-bash-source-command-doesnt-work
# Unfortunately this doesn't work so just use the full path when necessary.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc

RUN ~/.cargo/bin/rustup default stable
RUN ~/.cargo/bin/rustup update
RUN ~/.cargo/bin/rustup update nightly
RUN ~/.cargo/bin/rustup target add wasm32-unknown-unknown --toolchain nightly

# 2. https://substrate.dev/substrate-contracts-workshop/#/0/setup
RUN ~/.cargo/bin/rustup component add rust-src --toolchain nightly
RUN ~/.cargo/bin/rustup target add wasm32-unknown-unknown --toolchain stable

# 3. Download and build the software that runs your block-chain node.
# This will take a long time to build so start this and then go get some coffee.
RUN ~/.cargo/bin/cargo install canvas-node --git https://github.com/paritytech/canvas-node.git --tag v0.1.7 --force --locked

# 4. Install the ink! cli tool that will make initializing, building, and testing
# ink! smart contract projects easier.
RUN ~/.cargo/bin/cargo install cargo-contract --vers ^0.12 --force --locked


# Random notes
# How does rust get the source code?  Can it use a socks5 proxy or mirror sites?
# Does it really need to update crates.io all the time?  These deep questions may
# cause trouble when building this Dockerfile which we can deal with via
# rust configuration.  Here is an example to get you started:

#[http]
#proxy = "socks5://localhost:8080"

#[net]
#retry = 2                   # network retries
#git-fetch-with-cli = true   # use the `git` executable for git operations

#[source.crates-io]
#registry = "https://github.com/rust-lang/crates.io-index"
#registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"

#https://doc.rust-lang.org/cargo/reference/config.html

