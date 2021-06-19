# substrate-study
The purpose of this repository is to demonstrate the ability to perform integration testing with a Substrate blockchain, one or more smart contracts, and associated tools.  All of this runs in docker containers.

By following the README the user can build a set of suitable docker images that build a canvas node
as well as any relevant ink! contracts.  The user can then execute a Python script that will
load the contracts onto the canvas node block chain and invoke a variety of operations on said contracts.

This is the foundation for how you can build an integration test of several contracts working together.

## Getting started

From a shell window on the host in a suitable directory:

```sh
git clone https://github.com/bostontrader/substrate-study
cd substrate-study
docker build --file Dockerfile.canvas_node --tag substrate-study-canvas-node .
docker build --file Dockerfile.contract-builder --tag substrate-study-contract-builder .
docker build --file Dockerfile.flipper --tag substrate-study-flipper .
docker build --file Dockerfile.j --tag substrate-study-j .
```

Turn on the canvas-node...
```sh
docker run -it --rm --network=host substrate-study-canvas-node
```

This is a single computer block chain that makes blocks and comes to its own consensus.  Perfect for this application.

Finally, run the main.py script.  This will execute the test.  Observe the results.

```sh
./venv/bin/python main.py
```

## Digging deeper...

Substrate is a general-purpose toolkit for building block-chains, written in Rust.

The "Canvas node" from https://github.com/paritytech/canvas-node.git is a specific implementation
of a block-chain using the Substrate software.  It's also written in Rust.

Substrate block-chains don't necessarily support smart contracts.  Said support must be 
included via a pallet such as the contracts pallet.  The Canvas node includes this pallet and 
therefore supports smart contracts.

## The RPC API

After the Canvas node is built and executed, we can communicate with the block-chain via 
websockets and RPC.  The pieces of this puzzle that I have found 
 are:

* https://github.com/polkascan/py-substrate-interface

This is a python interface to substrate nodes.  It is the single example I could find that can actually load a contract onto the block chain.  This after I opened an issue about their prior deprecated example whereupon they very quickly de-deprecated witha functioning examples.  Hats off to them! Thanks guys!

* https://paritytech.github.io/canvas-ui

This is a publicly visible website that contains a React/JS/TS application that
works very well with a functioning Canvas node.  Unfortunately, how it communicates
with the node is deeply buried inside source code.  Untangle this at your leisure.

* https://polkadot.js.org/docs/api/

This is a fairly decent overview of the API.  Although this looks like it's just for Polkadot,
it's broadly applicable for any Substrate chain.  This is an excellent source for an overview.  Unfortunately, the examples that we tried were outdated, missing other important elements of usage, and just didn't work.  These docs guide you to use the npm package @polkadot/api, which is JS/TS.  It also tells us that it's using ES2015, async/await, import and so we need to make sure our environment supports all this.

* https://polkadot.js.org/docs/api-contract

This is a fairly decent overview of the API features required to install, instantiate, 
and invoke smart contracts.  This is directly accessible as a chapter in the /docs/api link,
but there's a separate npm package @polkadot/api-contract.  As with @polkadot/api, this is ES2015
and the examples that we tried didn't actually work.

* https://polkadot.js.org/docs/

Generally we can use a brower's developer tools to observe ws traffic between a web app and the Canvas chain.
Although we can see this traffic, there's little sense of a higher-level pattern of messages.  There's also
lots of opaque numbers in parameters and results to figure out.


## A few words about docker networking

We need networking in order to build the containers initially and for them to do their jobs thereafter.  We may also have a variety of networking woes host involving firewalls, proxies, etc.  This topic is far too complex to address here, beyond a few simple warnings most relevant for this project.

Recall that we can generally use --network=host in docker build and docker run commands.  When used with docker build, this option will cause docker to use the host network in order to execute RUN commands.  Whatever you have to do with your host to punch through the firewall will therefore generally accrue to the benefit of docker build.

When used with docker run, the container will use the host network as expected.


## A few words about cargo

How does rust get the source code?  Can it use a socks5 proxy or mirror sites?
Does it really need to update crates.io all the time?  These deep questions may
cause trouble when building Dockerfiles which we can deal with via
rust configuration.  Here is an example to get you started:

[http]
proxy = "socks5://localhost:8080"

[net]
retry = 2                   # network retries
git-fetch-with-cli = true   # use the `git` executable for git operations

[source.crates-io]
#registry = "https://github.com/rust-lang/crates.io-index"
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"

https://doc.rust-lang.org/cargo/reference/config.html
