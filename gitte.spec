# Gitte: native Fedora / COPR RPM, using distro-packaged Rust crates.
# Target: Fedora 44. No vendored Cargo dependencies or Flatpak runtime.
#
# NOTE (2026-11-03): Relm4 0.11.0 is available in Fedora 44, but Gitte
# 0.11.x's lockfile uses gettext-rs 0.8.0 / gettext-sys 0.27.0, while
# Fedora 44 currently has gettext-rs 0.7.7 / gettext-sys 0.26.0.
# Backport the missing crate RPMs (or arrange compatible upstream patches)
# before expecting a successful Fedora-44 native-dependency build.
# Other missing crate versions may be identified by the first mock build.

Name:           gitte
Version:        0.11.1
Release:        1%{?dist}
Summary:        Native Git client for GNOME

License:        AGPL-3.0-or-later
URL:            https://codeberg.org/ckruse/Gitte
Source0:        https://codeberg.org/ckruse/Gitte/archive/%{version}.tar.gz

ExclusiveArch:  %{rust_arches}

# Meson installs the binary, .desktop, icons, D-Bus activation, schemas,
# translated messages, and AppStream metadata.
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  pkgconfig
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  appstream
BuildRequires:  glib2-devel
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(graphene-1.0)
BuildRequires:  pkgconfig(libgit2)
BuildRequires:  pkgconfig(openssl)

Requires:       git-core
Recommends:     git-lfs

%description
Gitte is a Git client built for the GNOME desktop using GTK4,
libadwaita, Rust, and Relm4. It provides commit-history browsing,
diff viewing, staging, and repository operations.

%prep
# Codeberg's Forgejo archive has a top-level directory named "gitte".
%autosetup -n gitte
# Use Fedora's packaged crates via /usr/share/cargo/registry.
%cargo_prep

%generate_buildrequires
# Reads the Cargo manifest and generates versioned crate(...) requirements,
# including Relm4 0.11.x, rather than pinning crate RPM package names.
%cargo_generate_buildrequires

%build
# Meson drives Cargo for this project, so do not call %cargo_build again.
export CARGO_NET_OFFLINE=true
export LIBGIT2_SYS_USE_PKG_CONFIG=1
export RUSTFLAGS="%{build_rustflags}"
%meson -Dflatpak=false
%meson_build

%install
%meson_install
%find_lang %{name}

%check
%meson_test
desktop-file-validate \
    %{buildroot}%{_datadir}/applications/de.wwwtech.gitte.desktop
glib-compile-schemas --strict --dry-run \
    %{buildroot}%{_datadir}/glib-2.0/schemas

%files -f %{name}.lang
%license COPYING
%doc README.md
%{_bindir}/gitte
%{_libexecdir}/gitte/
%{_datadir}/gitte/
%{_datadir}/applications/de.wwwtech.gitte.desktop
%{_datadir}/dbus-1/services/de.wwwtech.gitte.service
%{_datadir}/metainfo/de.wwwtech.gitte.metainfo.xml
%{_datadir}/glib-2.0/schemas/de.wwwtech.gitte.gschema.xml
%{_datadir}/icons/hicolor/scalable/apps/de.wwwtech.gitte.svg
%{_datadir}/icons/hicolor/symbolic/apps/de.wwwtech.gitte-symbolic.svg

%changelog
* Tue Nov 03 2026 COPR maintainer - 0.11.1-1
- Initial Fedora-native COPR spec for Gitte 0.11.1
- Generate Rust BuildRequires automatically using Fedora's crate packages
- Use Meson integration and system libgit2
