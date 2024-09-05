# still App Manager
still App Manager (SAM) is a Python alternative for package kit explicitly built for stillOS. SAM supports Flatpaks and stillOS system upgrades and is not trying to be an all-in-one solution for every distribution.

It works by using a daemon running to manage apps through it and a library to access the daemon.

The main project this is used in is stillCenter

![image](https://github.com/user-attachments/assets/394f756f-5e6a-4c96-9d23-c280327b3ebd)

# Installation
You most likely do not need to install this, because it's made solely for stillOS, and preinstalled, but if you need to install this for some reason, you can build RPMs using the .spec file.

pip installation is not supported because this is supposed to be installed and managed through the distro package manager as part of stillOS.

You can also manually install it into your Python site-packages directory, and then putting systemd/sam.service into your systemd unit dir, putting systemd/95-sam.preset into your system dir unit dir, and putting io.stillhq.sam.conf into /etc/dbus-1/system.d directory

Then run `sudo systemctl enable sam.service`


# Dependencies
```
Requires:       python3-pydbus
Requires:       python3-gobject
Requires:       python3
Requires:       libappstream-glib
```
