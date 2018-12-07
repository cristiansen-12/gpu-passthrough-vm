Name:           gpu-passthrough-vm
Version:        1.0
Release:        1%{?dist}
Summary:        Windows 10 VM install for Fedora
BuildRoot:	%{_builddir}/%{name}-%{version}

License:        GPLv2         
Source0:        33-vfio-hugepages-sysctl.conf
Source1:        33-vfio-memory-limits.conf
Source2:	ifcfg-xenbr0
Source3:	ifcfg-bridge-slave-tap0
Source4:	ifcfg-bridge-slave-eno1
Source5:	windows-vm.service
Source6:	33-vfio-modprobe.conf
Source7:	33-vfio-dracut.conf

Requires:      	tunctl
Requires:	bridge-utils
Requires:	qemu-kvm 
Requires:	qemu-img 
Requires:	libvirt
Requires:	virt-install 

%define __default_grub %{_sysconfdir}/default/grub

%description
Windows 10 QEMU VM

%prep
# Create Directory (and change to it) Before Unpacking; Do Not Perform Default Archive Unpacking
# %setup -n test -c -T

%build


%install
rm -rf %{buildroot}

%{__install} -D -m0644  %{SOURCE0} %{buildroot}%{_sysconfdir}/sysctl.d/%(basename %{SOURCE0})
%{__install} -D -m0644  %{SOURCE1} %{buildroot}%{_sysconfdir}/security/limits.d/%(basename %{SOURCE1})
%{__install} -D -m0644  %{SOURCE6} %{buildroot}%{_sysconfdir}/modprobe.d/%(basename %{SOURCE6})
%{__install} -D -m0644  %{SOURCE7} %{buildroot}%{_sysconfdir}/dracut.conf.d/%(basename %{SOURCE7})
%{__install} -D -m0644  %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/%(basename %{SOURCE2})
%{__install} -D -m0644  %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/%(basename %{SOURCE3})
%{__install} -D -m0644  %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/network-scripts/%(basename %{SOURCE4})
%{__install} -D -m0644  %{SOURCE5} %{buildroot}%{_unitdir}/%(basename %{SOURCE5})

%post
if [ "$1" -eq "1" ] ; then
	# Install the first time 
	echo "hugetlbfs    /run/hugepages/kvm    hugetlbfs    defaults    0 0" >> %{_sysconfdir}/fstab
	%{__grep} 'rd.driver.pre=vfio-pci' %{__default_grub} > /dev/null; test $? -eq 0 || %{__sed} -i.orig 's@GRUB_CMDLINE_LINUX="@GRUB_CMDLINE_LINUX="intel_iommu=on iommu=pt rd.driver.pre=vfio-pci @g' %{__default_grub}

	systemctl daemon-reload

	grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
	dracut -f --kver %(uname -r)

	nmcli con down eno1 &
	nmcli con up xenbr0 &
fi

%postun
if [ "$1" -eq "0" ] ; then
	#Remove last version of package
	%{__sed} -i.orig '/run\/hugepages\/kvm/d' %{_sysconfdir}/fstab
	%{__grep} 'rd.driver.pre=vfio-pci' %{__default_grub} > /dev/null; test $? -eq 0 && %{__sed} -i.orig 's@GRUB_CMDLINE_LINUX="intel_iommu=on iommu=pt rd.driver.pre=vfio-pci @GRUB_CMDLINE_LINUX="@g' %{__default_grub}

	systemctl daemon-reload

	grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg
	dracut -f --kver %(uname -r)

	nmcli con down xenbr0 || true &
	nmcli con up eno1 || true &
fi

%files
%defattr(0644,root,root)
/etc/sysctl.d/%(basename %{SOURCE0})
/etc/security/limits.d/%(basename %{SOURCE1})
/etc/modprobe.d/%(basename %{SOURCE6})
/etc/dracut.conf.d/%(basename %{SOURCE7})
/etc/sysconfig/network-scripts/%(basename %{SOURCE2})
/etc/sysconfig/network-scripts/%(basename %{SOURCE3})
/etc/sysconfig/network-scripts/%(basename %{SOURCE4})
%{_unitdir}/%(basename %{SOURCE5})


%changelog
* Tue Nov 27 2018 
- 

# nmcli connection add type tun ifname tap0 con-name tap0 mode tap owner `id -u cristiansen` ip4 10.1.0.1/24
# nmcli con add type bridge ifname xenbr0 con-name xenbr0 connection.autoconnect yes
# sudo nmcli con add type bridge-slave ifname tap0 master xenbr0
# sudo nmcli con add type bridge-slave ifname eno1 master xenbr0
# nmcli con modify xenbr0 bridge.stp no
# sudo nmcli con down eno1
# sudo nmcli con up xenbr0

# https://github.com/jleroy/plexmediaplayer-fedora/blob/master/SPECS/plexmediaplayer.spec
# https://github.com/izenn/ts3-spec/blob/master/teamspeak3-server.spec
# https://github.com/tilo/nginx-rpm/blob/master/nginx.spec
