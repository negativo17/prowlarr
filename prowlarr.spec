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
Version:        2.5.2.5491
Release:        2%{?dist}
Summary:        Indexer manager/proxy to integrate with your various PVR apps
License:        GPLv3
URL:            https://prowlarr.com/

BuildArch:      x86_64 aarch64 armv7hl

Source0:        https://github.com/Prowlarr/Prowlarr/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}.sysusers.conf
Source2:        %{name}.service
Source3:        %{name}.xml
Patch0:         https://patch-diff.githubusercontent.com/raw/Prowlarr/Prowlarr/pull/2808.patch

BuildRequires:  dotnet-sdk-%{dotnet}
BuildRequires:  firewalld-filesystem
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  nodejs
BuildRequires:  systemd-rpm-macros
BuildRequires:  tar
BuildRequires:  yarnpkg

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       libmediainfo
Requires:       sqlite

%description
Prowlarr supports management of both Torrent Trackers and Usenet Indexers. It
integrates seamlessly with Lidarr, Mylar3, Radarr, Readarr, and Sonarr offering
complete management of your indexers with no per app Indexer setup required (we
do it all).

%prep
%autosetup -p1 -n Prowlarr-%{version}

# Accomodate old SDK versions
rm -f global.json

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

find . -name libcoreclrtraceptprovider.so -delete

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/net*/* _output/UI %{buildroot}%{_libdir}/%{name}/

install -D -m 0644 -p %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -D -m 0644 -p %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 -p %{SOURCE3} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

find %{buildroot} -name "*.pdb" -delete
find %{buildroot} -name "ffprobe" -exec chmod 0755 {} \;

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
%{_sysusersdir}/%{name}.conf
%{_unitdir}/%{name}.service

%changelog
* Wed Sep 02 2026 Simone Caronni <negativo17@gmail.com> - 2.5.2.5491-2
- Drop unused package references: Microsoft.Data.SqlClient, System.ServiceModel.Syndication,
  System.Memory and System.Configuration.ConfigurationManager. Microsoft.Data.SqlClient pulls in
  Microsoft.Identity.Client.NativeInterop, whose prebuilt libmsalruntime.so requires
  libcurl.so.4(CURL_OPENSSL_4), which is not available on Fedora/EPEL.
- Trim changelog.

* Sun Aug 09 2026 Simone Caronni <negativo17@gmail.com> - 2.5.2.5491-1
- Update to 2.5.2.5491.

* Wed Jun 10 2026 Simone Caronni <negativo17@gmail.com> - 2.4.0.5397-1
- Update to 2.4.0.5397.
