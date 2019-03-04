# Dockerize Jupyter kernels

This creates a new Jupyter kernel, which executes the `python` process
inside of Docker, while forwarding all of the five control parts back
to the host.  Thus, all Jupyter itself runs on the *host*, but only
the *kernel process* runs in the container.  This is not something
which is normally useful, unless you trust Jupyter itself (e.g. you
are running nbgrader) but you don't trust the code itself
(e.g. autograding student code).

When this is used, the kernel itself doesn't necessarily do I/O.  The
Jupyter on the host reads the notebook and sends it to the kernel via
the network sockets.  Output is likewise returned to the host via the
network sockets, where it might be saved or used.  However, if the
notebook code itself reads or writes files, this will be done inside
of the container, and thus you may need to mount directories inside of
the container.

This should currently be considered Alpha.



## Installation

There is no installation - just put the Python file on the path and
make executable.  The script is run in two contexts: first, to set up
a new kernel.  Second, when that kernel is invoked, the script runs
again to set up Docker properly.



## Usage

Install a new kernel:

```
./jupyter_docker_kernel.py setup --name=python3secure --image=aaltoscienceit/notebook-server:0.5.9 --user
```

Important options:

* `--user`: install kernel as a user (recommended)

* `--name=NAME`: Identifier of the python kernel, like `python3secure`
  or some such.

* `--mount=HOST:MOUNTPOINT`: mount a host directory inside the
  container.  By default, the working directory is mounted inside of
  the container (at the same path as on the host).  Jupyter chdirs to
  the notebook directory before running the notebook.  If you add
  `:ro` after, it will be mounted read-only, and if you specify
  `:copy` it will be copied on the host before mounting.

Other options:

* `--workdir`: The container always uses the jupyter workdir from the
  host as the source of workdir files.  This option only specifies the
  *mountpoint* of that directory inside the image.

* `--copy-workdir`: copy the working directory to a tmpdir before
  mounting it.

* `--python=/PATH/TO/PYTHON`: Path to Python to run in the container.
  Defaults to `/opt/conda/bin/python3` which is suitable for the
  upstream Jupyter docker stacks.

* `--prefix` and `--replace`: same as normal Jupyter kernel
  installation options: prefix to install to and replace existing
  kernel.

This kernel can now be used on the *host* system, with all code
running in the docker container.  Note that the kernel itself doesn't
read the notebook file or write outputs: the host system's Jupyter is
doing that.



## Use with nbgrader

1. Install the kernel as above, with some `--name=NAME`.  You may need
to give any special options as above, in order to make your
environment work.

2. `nbgrader autograde --ExecutePreprocessor.kernel_name=NAME`.



## See also

* https://github.com/tamera-lanham/ipython-kernel-docker - basically same as here, not standalone utility
* https://gist.github.com/mariusvniekerk/09062bc8974e5d1f4af6 - basically same as here, less automatic configuration and requires special image
* https://github.com/clemsonciti/singularity-in-jupyter-notebook - Jupyter kernel in singularity.  Manual process, this tool can be extended to do that too.
* https://groups.google.com/forum/#!topic/jupyter/kQ9ZDX4rDEE - list with links and pointers
* https://github.com/jupyter/enterprise_gateway - not yet investigated, but supposed to allow remote kernels and so on.
* https://github.com/AaltoScienceIT/isolate-namespace - more primitive solution also by Aalto Science-IT.  Written in pure bash, uses 'unshare' to run the kernel in a separate isolated namespace on the same host system.
