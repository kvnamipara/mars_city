Tango Setup
===========

.. highlightlang:: sh

This page documents how to install Tango on Ubuntu.  These instructions
have been tested on Ubuntu 13.10.

MySQL
-----

First you have to install MySQL::

  sudo apt-get install mysql-server mysql-client

During the installation of **mysql**, you can leave the root password empty.
If you specify a password you will have to enter it later, while installing
**tango-db**.


Tango
-----

After installing MySQL you can install tango::

  sudo apt-get install tango-common tango-db tango-starter tango-test python-pytango libtango8-doc libtango8-dev

If you are still using Ubuntu 13.04 you should use ``libtango7-*`` instead of
``libtango8-*``.

During the installation of **tango-common**, enter ``pcname:10000`` as
TANGO host, where *pcname* is the name of your machine.

During the installation **tango-db** select:

* Configure database for tango-db with dbconfig-common? [yes]
* Password of the database's administrative user: [leave empty]
* MySQL application password for tango-db: [leave empty]

Next you have to install **libtango-java**.  If this is not available in the
repositories, you can add the launchpad repository manually::

    sudo add-apt-repository 'deb http://ppa.launchpad.net/tango-controls/core/ubuntu precise main'
    sudo apt-get update
    sudo apt-get install libtango-java


If you get this warning during the ``sudo apt-get update``::

    W: GPG error: http://ppa.launchpad.net precise Release: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY A8780D2D6B2E9D50

and/or this warning during the ``sudo apt-get install libtango-java``::

    WARNING: The following packages cannot be authenticated!
        libtango-java
    Install these packages without verification [y/N]?

you can fix it by doing::

    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A8780D2D6B2E9D50
    sudo apt-key update
    sudo apt-get update

.. note::
    Currently the repository doesn't have packages for *quantal*/*raring*/*saucy*,
    so it is necessary to specify *precise* even if you are running a more
    recent version.
    If you use ``sudo add-apt-repository ppa:tango-controls/core``, your
    version of Ubuntu will be selected, and you will have to change it to
    *precise* manually.

You should now be able to lauch **astor** and **jive** from the terminal.

For more information see the Troubleshooting section below and this link:
http://www.tango-controls.org/howtos/binary_deb


Troubleshooting
---------------

At the end of the installation, you should have two tango processes running::

    $ ps aux | grep tango
    tango    15451  1.0  0.1  71800  9820 ?        Sl   10:56   0:00 /usr/lib/tango/Starter pcname
    tango    21109  0.0  0.1  94396 10752 ?        Sl   May18   0:20 /usr/lib/tango/DataBaseds 2 -ORBendPoint giop:tcp::10000

The first one is from **tango-starter**, the second one from **tango-db**.

If you don't see them, you can try to reinstall these two packages, using::

    sudo apt-get remove package-name
    sudo apt-get install package-name

If you are reinstalling **tango-db** and/or if you get this error::

    An error occurred while installing the database:
    ERROR 2002 (HY000): Can't connect to local MySQL server through socket
    '/var/run/mysqld/mysqld.sock' (2)

you have to select <Yes> when asked "Deconfigure database for tango-db with
*dbconfig-common*?".

If you are still having problem you can try the following things:

* check that ``/etc/tangorc`` contains ``TANGO_HOST=pcname:10000``;
* try to set the environment variable ``TANGO_HOST``.  You can also add
  the following line to your ``~/.bashrc`` to make it automatic (you will have
  to restart bash)::

    export TANGO_HOST=pcname:10000

* try to (re)start **tango-db** and/or **tango-starter** manually using::

    sudo /etc/init.d/tango-db start
    sudo /etc/init.d/tango-starter start

* if it still doesn't work try completely removing the packages::

    sudo apt-get purge tango-db tango-starter

  * Deconfigure database for tango-db with dbconfig-common? [yes]
  * Do you want to purge the database for tango-db? [yes]
  * Password of the database's administrative user: [leave empty]

  and then reinstalling them::

    sudo apt-get install tango-db tango-starter

  * Configure database for tango-db with dbconfig-common? [yes]
  * Password of the database's administrative user: [leave empty]
  * MySQL application password for tango-db: [leave empty]

Fix for Ubuntu 13.04
--------------------
If you are running on Ubuntu 13.04 you have to install this patch in order to avoid a Segmentation fault (core dumped) at every python server run.
Install first libboost-python-dev::

    sudo apt-get install libboost-python-dev

Download the patch from:

https://pypi.python.org/packages/source/P/PyTango/PyTango-7.2.4.tar.gz

untar and install it:

* $ tar xzvf PyTango-7.2.4.tar.gz
* $ cd PyTango-7.2.4
* $ python setup.py build
* $ sudo python setup.py install

Adding a new server in Tango
----------------------------
To register a new server run **jive**, select ``Edit -> Create Server`` and provide:

* the executable name and the instance name (ex: legorcx/c1b8)
* the Class name 
* the device name in the format: ``C3/subsystem/device``

Then start the java/python/C++ application always providing the instance name, example::

  python legorcx c1b8

and the Class properties will be automatically filled in the database


