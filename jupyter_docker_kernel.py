#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

print(sys.argv)

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', action='store_true', default=False, help="Install kernel to user dir")
    parser.add_argument('--prefix', action='store_true', help="Install kernel to this prefix")
    parser.add_argument('--replace', action='store_true', help="Replace existing kernel?")

    parser.add_argument('--python', default='/opt/conda/bin/python3')
    parser.add_argument('--name', required=True, default='python3secure2')
    parser.add_argument('--workdir')
    parser.add_argument('--copy-workdir', action='store_true')
    parser.add_argument('--image', required=True)
    parser.add_argument('--mount', action="append", default=[],
                        help="mount to set up, format hostDir:containerMountPoint")

    #parser.add_argument('remainder', nargs=argparse.REMAINDER)

    args = parser.parse_args(sys.argv[2:])

    argv = [
        os.path.realpath(sys.argv[0]),
        '--image', args.image,
        *[ '--mount={}'.format(x) for x in args.mount],
        #*args.remainder,
        args.python,
        "-m",
        "ipykernel_launcher",
        "-f",
        "{connection_file}",
    ]
    if args.workdir:
        argv.insert(1, '--workdir={}'.format(args.workdir))
    if args.copy_workdir:
        argv.insert(1, '--copy-workdir')

    kernel = {
        "argv": argv,
        "display_name": "Docker kernel of {}".format(args.image),
        "language": "python",
        }

    import jupyter_client.kernelspec
    #jupyter_client.kernelspec.KernelSpecManager().get_kernel_spec('python3').argv

    with tempfile.TemporaryDirectory(prefix='jupyter-kernel-secure-') as kernel_dir:
        open(os.path.join(kernel_dir, 'kernel.json'), 'w').write(json.dumps(kernel, sort_keys=True, indent=4))
        jupyter_client.kernelspec.KernelSpecManager().install_kernel_spec(kernel_dir, kernel_name=args.name,
                                                                          user=args.user, replace=args.replace, prefix=args.prefix)

    print()
    print("Kernel saved to {}".format(jupyter_client.kernelspec.KernelSpecManager().get_kernel_spec(args.name).resource_dir))
    print("Kernel command line is:", argv)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', help='image name')
    parser.add_argument('--mount', '-m', action='append', default=[],
                            help='mount to set up, format hostDir:containerMountPoint')
    parser.add_argument('--python', default='/opt/conda/bin/python3')
    parser.add_argument('--copy-workdir', default=False, action='store_true')
    parser.add_argument('--workdir')

    parser.add_argument('remainder', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    expose_ports = [ ]
    expose_mounts = [ ]

    # working dir
    workdir = os.getcwd()
    if args.workdir:
        workdir = args.workdir
    else:
        workdir = os.getcwd()
    expose_mounts.append(dict(src=os.getcwd(), dst=workdir, copy=args.copy_workdir, workdir=True))

    # Parse connection file
    for i in range(len(args.remainder)):
        if args.remainder[i] == '-f':
            json_file = args.remainder[i+1]
            connection_data = json.load(open(json_file))
            # Find all the (five) necessary ports
            for var in ('shell_port', 'iopub_port', 'stdin_port', 'control_port', 'hb_port'):
                # Forward each port to itself
                expose_ports.append((connection_data[var], connection_data[var]))
            # Mount the connection file inside the container
            expose_mounts.append(dict(src=json_file, dst=json_file))

            # Change connection_file to bind to all IPs.
            connection_data['ip'] = '0.0.0.0'
            open(json_file, 'w').write(json.dumps(connection_data))
            break

    cmd = [
        "docker", "run", "--rm", "-i",
        "--user", "%d:%d"%(os.getuid(), os.getgid()),
        ]

    # Add options to expose the ports
    for port_host, port_container in expose_ports:
        cmd.extend(['--expose={}'.format(port_container), "-p", "{}:{}".format(port_host, port_container)])

    # Add options for exposing mounts
    tmpdirs = [ ]  # keep reference to clean up later
    for mount in expose_mounts:
        src = mount['src']  # host data
        dst = mount['dst']  # container mountpoint
        if mount.get('copy'):
            tmpdir = tempfile.TemporaryDirectory(prefix='jupyter-secure-')
            tmpdirs.append(tmpdir)
            src = tmpdir.name + '/copy'
            shutil.copytree(mount['src'], src)
        cmd.extend(["--mount", "type=bind,source={},destination={},ro={}".format(src, dst, 'true' if mount.get('ro') else 'false')])  # ro=true
    cmd.extend(("--workdir", workdir))

    # Image name
    cmd.append(args.image)

    # Remainder of all other arguments from the kernel specification
    cmd.extend([
        *args.remainder,
        '--debug',
        ])

    # Run...
    print(cmd)
    ret = subprocess.call(cmd)

    # Clean up all temparary directories
    for tmpdir in tmpdirs:
        tmpdir.cleanup()
    exit(ret)



if sys.argv[1] == 'setup':
    setup()
else:
    run()


#import jupyter_client.kernelspec
#jupyter_client.kernelspec.KernelSpecManager().get_kernel_spec('python3').argv
#jupyter_client.kernelspec.KernelSpecManager().install_kernel_spec(source_dir, kernel_name=None, user=False, replace=None, prefix=None)


