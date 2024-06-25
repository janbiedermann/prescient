<img src="https://raw.githubusercontent.com/janbiedermann/prescient/master/prescient.webp" alt="Prescient">
<small>(Original Image by <a href="https://www.freepik.com/free-photo/fortune-teller-with-crystal-globe-front-view_35816174.htm">Freepik</a>)</small>

# Pres**ci**ent

A simple, reliable, *nixish (that also includes Windows/Cygwin) continuous integration for Git and:
- FreeBSD hosts with bhyve and [laminar](https://github.com/ohwgiles/laminar)
- Windows/Linux hosts with VirtualBox and either [nq](https://github.com/leahneukirchen/nq) or [laminar](https://github.com/ohwgiles/laminar)
in ~150 lines of sh.
Running forever with little maintenenace required.

## Features

- use any script language you love for CI runs, no need for YAML
- using very little CPU/RAM resources for itself
- can scale up to many virtual machines on different hosts
- very adaptable to individual needs, just a few lines of sh

## Installation and Configuration

Choose your path, either:

- [FreeBSD hosts using bhyve and laminar](https://github.com/janbiedermann/prescient/blob/master/bhyve/README.md)

or:

- [Linux or Windows hosts using VirtualBox and nq or laminar](https://github.com/janbiedermann/prescient/blob/master/VirtualBox/README.md)
