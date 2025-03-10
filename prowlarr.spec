# mock configuration:
# - Requires network for running yarn/dotnet build

%global debug_package %{nil}
%define _build_id_links none

%global user %{name}
%global group %{name}

%global dotnet 8.0

%ifarch x86_64
%global rid x64
%endif

%ifarch aarch64
%global rid arm64
%endif

%ifarch armv7hl
%global rid arm
%endif

%if 0%{?fedora}
%global __requires_exclude ^liblttng-ust\\.so\\.0.*$
%endif

Name:           prowlarr
Version:        1.31.2.4975
Release:        1%{?dist}
Summary:        Indexer manager/proxy to integrate with your various PVR apps
License:        GPLv3
URL:            https://prowlarr.com/

BuildArch:      x86_64 aarch64 armv7hl

Source0:        https://github.com/Prowlarr/Prowlarr/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source10:       %{name}.service
Source11:       %{name}.xml

BuildRequires:  dotnet-sdk-%{dotnet}
BuildRequires:  firewalld-filesystem
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  nodejs
BuildRequires:  systemd
BuildRequires:  tar
BuildRequires:  yarnpkg

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       libmediainfo
Requires:       sqlite
Requires(pre):  shadow-utils

%description
Prowlarr supports management of both Torrent Trackers and Usenet Indexers. It
integrates seamlessly with Lidarr, Mylar3, Radarr, Readarr, and Sonarr offering
complete management of your indexers with no per app Indexer setup required (we
do it all).

%prep
%autosetup -n Prowlarr-%{version}

# Remove test coverage and Windows specific stuff from project file
pushd src
dotnet sln Prowlarr.sln remove \
  NzbDrone.Automation.Test \
  NzbDrone.Common.Test \
  NzbDrone.Core.Test \
  NzbDrone.Host.Test \
  NzbDrone.Integration.Test \
  NzbDrone.Libraries.Test \
  NzbDrone.Mono.Test \
  NzbDrone.Test.Common \
  NzbDrone.Test.Dummy \
  NzbDrone.Update.Test \
  NzbDrone.Windows.Test \
  NzbDrone.Windows \
  Prowlarr.Api.V1.Test \
  Prowlarr.Benchmark.Test \
  ServiceHelpers/ServiceInstall \
  ServiceHelpers/ServiceUninstall
popd

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
dotnet msbuild -restore src/Prowlarr.sln \
    -p:RuntimeIdentifiers=linux-%{rid} \
    -p:Configuration=Release \
    -p:Platform=Posix \
    -p:SelfContained=true \
    -v:normal

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
yarn run build --mode production

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/net*/* _output/UI %{buildroot}%{_libdir}/%{name}/

install -D -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

find %{buildroot} -name "*.pdb" -delete
find %{buildroot} -name "ffprobe" -exec chmod 0755 {} \;

%pre
getent group %{group} >/dev/null || groupadd -r %{group}
getent passwd %{user} >/dev/null || \
    useradd -r -g %{group} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "%{name}" %{user}
exit 0

%post
%systemd_post %{name}.service
%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%attr(750,%{user},%{group}) %{_sharedstatedir}/%{name}
%{_libdir}/%{name}
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
* Mon Mar 10 2025 Simone Caronni <negativo17@gmail.com> - 1.31.2.4975-1
- Update to 1.31.2.4975.

* Tue Feb 04 2025 Simone Caronni <negativo17@gmail.com> - 1.30.2.4939-1
- Update to 1.30.2.4939.

* Mon Jan 06 2025 Simone Caronni <negativo17@gmail.com> - 1.29.2.4915-1
- Update to 1.29.2.4915.

* Fri Dec 20 2024 Simone Caronni <negativo17@gmail.com> - 1.28.2.4885-1
- Update to 1.28.2.4885.

* Thu Nov 28 2024 Simone Caronni <negativo17@gmail.com> - 1.27.0.4852-1
- Update to 1.27.0.4852.

* Sun Oct 27 2024 Simone Caronni <negativo17@gmail.com> - 1.25.4.4818-1
- Update to 1.25.4.4818.
- Switch to .net 8.0 for building.

* Thu Oct 10 2024 Simone Caronni <negativo17@gmail.com> - 1.24.3.4754-1
- Update to 1.24.3.4754.

* Tue Sep 24 2024 Simone Caronni <negativo17@gmail.com> - 1.24.2.4749-1
- Update to 1.24.2.4749.

* Thu Sep 12 2024 Simone Caronni <negativo17@gmail.com> - 1.24.0.4721-1
- Update to 1.24.0.4721.

* Thu Aug 29 2024 Simone Caronni <negativo17@gmail.com> - 1.23.0.4690-1
- Update to 1.23.0.4690.

* Sun Aug 18 2024 Simone Caronni <negativo17@gmail.com> - 1.22.0.4670-1
- Update to 1.22.0.4670.

* Sun Aug 04 2024 Simone Caronni <negativo17@gmail.com> - 1.21.2.4649-1
- Update to 1.21.2.4649.

* Wed Jul 10 2024 Simone Caronni <negativo17@gmail.com> - 1.20.1.4603-1
- Update to 1.20.1.4603.

* Wed Jul 03 2024 Simone Caronni <negativo17@gmail.com> - 1.20.0.4590-1
- Update to 1.20.0.4590.

* Fri Jun 21 2024 Simone Caronni <negativo17@gmail.com> - 1.19.0.4568-1
- Update to 1.19.0.4568.

* Thu Jun 06 2024 Simone Caronni <negativo17@gmail.com> - 1.18.0.4543-1
- Update to 1.18.0.4543.

* Thu May 16 2024 Simone Caronni <negativo17@gmail.com> - 1.17.2.4511-1
- Update to 1.17.2.4511.

* Wed May 08 2024 Simone Caronni <negativo17@gmail.com> - 1.17.1.4483-1
- Update to 1.17.1.4483.

* Wed Apr 24 2024 Simone Caronni <negativo17@gmail.com> - 1.16.2.4435-1
- Update to 1.16.2.4435.

* Tue Apr 16 2024 Simone Caronni <negativo17@gmail.com> - 1.16.1.4420-1
- Update to 1.16.1.4420.

* Tue Apr 02 2024 Simone Caronni <negativo17@gmail.com> - 1.15.0.4361-1
- Update to 1.15.0.4361.

* Wed Mar 20 2024 Simone Caronni <negativo17@gmail.com> - 1.14.3.4333-1
- Update to 1.14.3.4333.

* Tue Mar 12 2024 Simone Caronni <negativo17@gmail.com> - 1.14.2.4318-1
- Update to 1.14.2.4318.

* Sun Mar 03 2024 Simone Caronni <negativo17@gmail.com> - 1.14.1.4316-1
- Update to 1.14.1.4316.

* Tue Feb 20 2024 Simone Caronni <negativo17@gmail.com> - 1.14.0.4286-1
- Update to 1.14.0.4286.

* Mon Feb 12 2024 Simone Caronni <negativo17@gmail.com> - 1.13.3.4273-1
- Update to 1.13.3.4273.

* Mon Feb 05 2024 Simone Caronni <negativo17@gmail.com> - 1.13.2.4251-1
- Update to 1.13.2.4251.

* Wed Jan 31 2024 Simone Caronni <negativo17@gmail.com> - 1.13.1.4243-1
- Update to 1.13.1.4243.

* Thu Jan 25 2024 Simone Caronni <negativo17@gmail.com> - 1.13.0.4217-1
- Update to 1.13.0.4217.

* Wed Jan 17 2024 Simone Caronni <negativo17@gmail.com> - 1.12.1.4201-1
- Update to 1.12.1.4201.

* Mon Jan 08 2024 Simone Caronni <negativo17@gmail.com> - 1.12.0.4188-1
- Update to 1.12.0.4188.

* Sat Jan 06 2024 Simone Caronni <negativo17@gmail.com> - 1.11.4.4173-1
- Update to 1.11.4.4173.

* Thu Dec 28 2023 Simone Caronni <negativo17@gmail.com> - 1.11.3.4163-1
- Update to 1.11.3.4163.

* Thu Dec 21 2023 Simone Caronni <negativo17@gmail.com> - 1.11.2.4160-1
- Update to 1.11.2.4160.

* Tue Dec 12 2023 Simone Caronni <negativo17@gmail.com> - 1.11.1.4146-1
- Update to 1.11.1.4146.

* Mon Dec 04 2023 Simone Caronni <negativo17@gmail.com> - 1.11.0.4128-1
- Update to 1.11.0.4128.

* Sun Nov 26 2023 Simone Caronni <negativo17@gmail.com> - 1.10.4.4088-1
- Update to 1.10.4.4088.

* Wed Nov 15 2023 Simone Caronni <negativo17@gmail.com> - 1.10.3.4070-1
- Update to 1.10.3.4070.

* Mon Oct 30 2023 Simone Caronni <negativo17@gmail.com> - 1.10.1.4059-1
- Update to 1.10.1.4059.

* Tue Oct 17 2023 Simone Caronni <negativo17@gmail.com> - 1.9.4.4039-1
- Update to 1.9.4.4039.

* Tue Oct 03 2023 Simone Caronni <negativo17@gmail.com> - 1.9.2.3992-1
- Update to 1.9.2.3992.

* Wed Sep 27 2023 Simone Caronni <negativo17@gmail.com> - 1.9.1.3981-1
- Update to 1.9.1.3981.

* Fri Sep 22 2023 Simone Caronni <negativo17@gmail.com> - 1.9.0.3966-1
- Update to 1.9.0.3966.

* Mon Sep 11 2023 Simone Caronni <negativo17@gmail.com> - 1.8.6.3946-1
- Update to 1.8.6.3946.
- Change build to more closely match upstream.

* Mon Sep 04 2023 Simone Caronni <negativo17@gmail.com> - 1.8.5.3896-1
- Update to 1.8.5.3896.

* Sun Aug 27 2023 Simone Caronni <negativo17@gmail.com> - 1.8.4.3884-1
- Update to 1.8.4.3884.

* Wed Aug 23 2023 Simone Caronni <negativo17@gmail.com> - 1.8.3.3880-1
- Update to 1.8.3.3880.

* Sun Aug 20 2023 Simone Caronni <negativo17@gmail.com> - 1.8.2.3860-1
- Update to 1.8.2.3860.

* Mon Aug 07 2023 Simone Caronni <negativo17@gmail.com> - 1.8.1.3837-1
- Update to 1.8.1.3837.

* Mon Jul 17 2023 Simone Caronni <negativo17@gmail.com> - 1.7.2.3710-1
- Update to 1.7.2.3710.

* Tue Jul 11 2023 Simone Caronni <negativo17@gmail.com> - 1.7.1.3684-2
- Drop selinux-policy requirement (for now).

* Tue Jul 11 2023 Simone Caronni <negativo17@gmail.com> - 1.7.1.3684-1
- Update to 1.7.1.3684.

* Fri Jul 07 2023 Simone Caronni <negativo17@gmail.com> - 1.7.0.3623-1
- First build.
