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

Extra options:

* `--user`: install kernel as a user (recommended)

* `--mount=HOST:MOUNTPOINT`: mount a host directory inside the
  container.  By default, the working directory is mounted inside of
  the container (at the same path as on the host).  Jupyter chdirs to
  the notebook directory before running the notebook.

* `--copy-workdir`: copy the working directory to

This kernel can now be used on the *host* system, with all code
running in the docker container.  Note that the kernel itself doesn't
read the notebook file or write outputs: the host system's Jupyter is
doing that.


## Use with nbgrader

1. Install the kernel as above, with some `--name=NAME`.  You may need
to give any special options.

2. `nbgrader autograde --ExecutePreprocessor.kernel_name=NAME`.