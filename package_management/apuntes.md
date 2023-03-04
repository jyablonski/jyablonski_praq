[Article](https://realpython.com/python-wheels/)

Python Wheels are pre-built bundles of packages that you install via Pip.  The alternative is for you to download the source installation for a package and then compile it yourself, which takes time.  Pip automatically tries finding & using wheels for packages if they're available.  
- Different wheels depending on OS such as Windows, Mac, or Linux.
- Some packages don't offer wheels because of how complex they are.
- Wheels are typically smaller in size to download, and faster to install from than a source distribution.
- Installing from source distributions often requires special compilation libraries like gcc or OpenSSL.  With wheels, you dont have to worry about this.
- Wheels target specific OS platform's and Python versions.


Python Egg or .egg-info is metadata related to the package to help specify package dependencies and other things.  Users aren't affected by it.