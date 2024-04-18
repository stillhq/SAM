Name:           sam
Version:        1.0
Release:        1
Summary:        Daemon for managing packages

License:        GPL v3
URL:            https://github.com/stillhq/SAM
Source0:        https://github.com/stillhq/SAM/archive/refs/heads/main.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-gobject
BuildRequires:  python3-pydbus
BuildRequires:  systemd-rpm-macros

%description
Daemon that runs in the background to manage package installation, updates, and more. Required for stillCenter.

%prep
%autosetup -n SAM-main
%build
%install
mkdir -p %{buildroot}%{python3_sitelib}/sam
install -m 0755 *.py %{buildroot}%{python3_sitelib}/sam
cp -a managers %{buildroot}%{python3_sitelib}/sam

# SystemD
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_presetdir}
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d
install -m 0755 systemd/sam.service %{buildroot}%{_unitdir}
install -m 0755 systemd/95-sam.preset %{buildroot}%{_presetdir}
install -m 0755 io.stillhq.sam.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d

mkdir -p %{buildroot}%{_datadir}/applications
install -m 0755 io.stillhq.sam.desktop %{buildroot}%{_datadir}/applications

%post
%systemd_user_post sam.service

%preun
%systemd_user_preun sam.service

%files
%{python3_sitelib}/sam/*.py*
%{python3_sitelib}/sam/managers/*.py*
%{_unitdir}/sam.service
%{_presetdir}/95-sam.preset
%{_sysconfdir}/dbus-1/system.d/io.stillhq.sam.conf

%changelog
* Thu Apr 18 2024 Cameron Knauff
- Initial build