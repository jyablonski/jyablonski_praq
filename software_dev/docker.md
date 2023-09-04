# How Docker Works
Docker is a containerization platform that allows you to package, distribute, and run applications and their dependencies within lightweight, isolated containers. Docker containers are portable and consistent environments that make it easier to develop, test, and deploy applications across different systems. 

- Docker Daemon: This background service manages Docker containers on the host system. It listens for Docker API requests and interacts with the host's operating system to create, start, stop, and manage containers.

- Docker CLI: The Docker Command-Line Interface (CLI) is a user-friendly tool that allows users to interact with the Docker Daemon. It provides commands for building, running, and managing containers.

# Docker on Linux vs Windows
Running Docker on Windows and on a Linux distribution like Ubuntu involves some key differences due to the underlying architecture and the way Docker is implemented on each platform. Here are the main differences:

### Operating System Compatibility:

- Windows: Docker on Windows runs on top of the Windows kernel, using a component called Hyper-V or Windows Subsystem which implements an installation for Linux 2 (WSL 2). It allows you to run either Windows and Linux containers, but Linux containers must run from within a Virtual Machine.

- Linux (ex. Ubuntu): On Linux, Docker interacts directly with the host's kernel. It can only run Linux containers natively. This means that you can't run Windows containers on a Linux-based Docker host.

### Resource Overhead:

- Windows: Running Docker on Windows have higher resource overhead when running normal non-Windows containers due to the need for virtualization components like Hyper-V or WSL 2, which consume additional memory and CPU resources.

- Linux (e.g., Ubuntu): Docker on Linux typically has lower resource overhead because it operates directly on the host's kernel. This can lead to better performance and resource utilization.

### Filesystem and Line Endings:

- Windows: When using Docker on Windows, you might encounter differences in filesystem behavior and line endings in text files compared to Linux. This can sometimes lead to unexpected issues when sharing code and files between Windows and Linux containers.

- Linux (e.g., Ubuntu): Running Docker on Linux avoids these filesystem and line-ending issues, as it operates in a consistent Linux environment.

### Networking:

- Windows: Docker for Windows uses a networking layer to connect Windows containers to the host and other containers. This network integration can sometimes introduce complexities when dealing with networking configurations.

- Linux (e.g., Ubuntu): Docker on Linux has more straightforward networking because it operates directly with the host's network stack, making it easier to manage networking configurations.

### Ecosystem and Compatibility:

- Windows: Some Docker images and software may not be readily available or as well-supported on Windows compared to Linux. The Docker ecosystem has historically been more Linux-centric.

- Linux (e.g., Ubuntu): Linux is the native platform for Docker, and you'll find a broader selection of Docker images and software optimized for Linux.
