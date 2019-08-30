# ppa-mirror

make it easier to manage deb package in local network

## purpose
mirror for debian repo, manage with web UI

## install
refer to `install.md`

## why?

It's really painful to install debian package, especially ppa package in local network in China. Link is slow, you always open public outband for your server (indeed you do not need it other than install software). So is there a easy way to manage debian package in local cluser?

Here's `ppa-mirror`. Install it in Master node with public network access, then other server in local network can install debian package from it.

You can also manage debian packages in master node, edit source your use and it will later used by local nodes.

With help of `ansible`, now you can easily install software in local network.


## features

* efficient mirror: only mirror package you install and depends on
* managable: a web UI to edit mirror rules
* easy setup: your client only add one line in source.list and start to use
* security: same insurance as debian public repo

## why not

`prerepo`, `apt-mirror` are good tools to make mirror, but they always make full mirror of source and you don't have much control of mirror package.

## license

MIT

