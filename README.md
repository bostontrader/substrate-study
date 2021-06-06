# substrate-study
The purpose of this repository is to demonstrate the ability to perform integration testing with a Substrate blockchain, one or more smart contracts, and associated tools.  All of this runs in a docker container and no external CI service need apply.

From a shell window on the host in a suitable directory:

```sh
git clone https://github.com/bostontrader/substrate-study
cd substrate-study
docker build -t substrate-study .
```

You may then
```sh
docker run -it --rm substrate-study bash
```