dealauth
===========================================================================

dealauth is the simple tool to propagate public keys among the servers via rsync.

How to use
---------------------------------------------------------------------------

1. Let's create `pubkey.d/` directory in this directory. This directory is ignored by Git. Alternatively you can also specify the exact path of arbitrary directory (actually the directory name needs not to be `pudbkey.d`) with `-k` or `--key-dir` option.

   The sample `pubkey.d/` directory exists in `doc/` directory and it will help you to understand the guide below.

2. In `pubkey.d/`, you have to create config file `dealauth.conf`. The example of contents is shown below.

   ```
   [foo]
   Allow: bar client

   [foobar]
   Allow: bar client
   VcsAllow: foo
   GitAllow: baz
   ```

   This configfile can read like this:
    * `foo` group allows log-in from `bar` and `client` groups.
    * `foobar` group allows log-in from `bar` and `client` groups.
      `foobar` also allows VCS access from `foo` and Git access from `baz`.

   You have to be careful not to use `tmp` for group name since `pubkey.d/tmp/` is used for temporal directory. Otherwise you have to specify temporal directory explicitly with `-t` or `--tmp-dir` option.

3. Next step is to prepare public keys. In `pubkey.d/`, you should create directories corresponding to groups in config file. You should create `foo`, `bar`, `client`, `foobar`, and `baz` in the above example. Then you should place each hosts' public keys into their group directories. The name of the public keys should `<hostname>.pub`.

4. This is the last step! Let's invoke the command.

   ```
   ./dealauth.py
   ```

   dealauth create authorized_keys for each groups in temporal directory and propagate them through rsync.
