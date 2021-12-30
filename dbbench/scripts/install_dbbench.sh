#!/bin/bash
wget -c "https://github.com/memsql/dbbench/archive/refs/tags/v0.4.zip"
unzip ./v0.4.zip
cd dbbench-0.4
sudo apt -y install golang git
mkdir $HOME/go
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
go build