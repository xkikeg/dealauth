dealauth
===========================================================================

dealauth is the simple tool to propagate public keys among the servers via rsync.

How to use
---------------------------------------------------------------------------

1. Let's create `pubkey.d` directory in this directory. This directory is ignored by Git. You can also specify the exact path of `pubkey.d`. To tell the truth, you can even change the name of directory.

2. In `pubkey.d`, you have to create config file `dealauth.conf`. The example of contents is shown below.

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

3. Next step is to prepare public keys. In `pubkey.d`, you should create directories corresponding to groups in config file. You should create `foo`, `bar`, `client`, `foobar`, and `baz` in above examples. Then you should place each hosts' public keys into their group directory. The name of the public keys should `<hostname>.pub`.

4. This is the last step! You invoke the command.

   ```
   ./dealauth.py
   ```

   dealauth create authorized_keys for each groups and propagate them through rsync.
