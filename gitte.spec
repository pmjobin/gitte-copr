# Gitte native GNOME Git client for Fedora COPR.
# Rust dependencies are bundled as sources in Source1 and built offline.
# GTK4, libadwaita, GLib, libgit2 and OpenSSL remain system libraries.
#
# COPR SCM: use the "make srpm" source-build method and .copr/Makefile.
# It generates Source0 and Source1 from this release's Cargo.lock.
# Do not mix vendor archives across versions.

Name:           gitte
Version:        0.11.1
Release:        5%{?dist}
Summary:        Native Git client for GNOME

# Upstream license; review the generated Cargo license summary after the
# first build to determine the full license expression for linked crates.
License:        AGPL-3.0-or-later
URL:            https://codeberg.org/ckruse/Gitte
Source0:        https://codeberg.org/ckruse/Gitte/archive/%{version}.tar.gz
Source1:        gitte-%{version}-vendor.tar.xz

ExclusiveArch:  %{rust_arches}

# Meson handles the native GNOME install; Cargo uses the vendored sources.
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  cargo-rpm-macros
BuildRequires:  cargo
BuildRequires:  rust
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
# The Codeberg / Forgejo release archive has a top-level "gitte" directory.
%autosetup -n gitte

# Archive contains vendor/ and cargo-vendor-config.toml, both generated
# from the matching, unmodified upstream Cargo.lock.
tar -xJf %{SOURCE1}
test -d vendor
test -s cargo-vendor-config.toml
test -s Cargo.lock

# Fedora's cargo_prep installs RPM build profile/configuration, but may
# delete Cargo.lock. Preserve the lockfile so versions remain pinned.
cp -p Cargo.lock Cargo.lock.rpm-pinned
%cargo_prep -N
mv -f Cargo.lock.rpm-pinned Cargo.lock

# Use Cargo's OWN `cargo vendor` config: it covers crates.io and any
# Git-sourced crates, unlike a hand-written crates.io-only config.
printf '\n' >> .cargo/config.toml
cat cargo-vendor-config.toml >> .cargo/config.toml

%build
export CARGO_NET_OFFLINE=true
export LIBGIT2_SYS_USE_PKG_CONFIG=1
export RUSTFLAGS="%{build_rustflags}"

# Verify that the pinned lockfile and vendored sources resolve offline.
cargo metadata --locked --offline --format-version 1 > /dev/null

# Meson drives Cargo directly; do not run a second Cargo build.
%meson -Dflatpak=false
%meson_build

# Keep a machine-readable inventory of bundled crates and their licenses.
%cargo_license_summary
%{cargo_license} > LICENSE.dependencies
%cargo_vendor_manifest

%install
%meson_install
%find_lang %{name}

%check
export CARGO_NET_OFFLINE=true
%meson_test
desktop-file-validate \
    %{buildroot}%{_datadir}/applications/de.wwwtech.gitte.desktop
glib-compile-schemas --strict --dry-run \
    %{buildroot}%{_datadir}/glib-2.0/schemas

%files -f %{name}.lang
%license COPYING LICENSE.dependencies cargo-vendor.txt
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
* Tue Nov 03 2026 COPR maintainer - 0.11.1-5
- Avoid expansion of Cargo RPM macro inside a shell comment
- Fix stray argument passed to Cargo during the build phase

* Tue Nov 03 2026 COPR maintainer - 0.11.1-4
- Generate upstream and vendored source archives during COPR SCM SRPM build
- Use the make srpm workflow instead of rpkg for SCM source generation

* Tue Nov 03 2026 COPR maintainer - 0.11.1-3
- Build all Rust crates from pinned, vendored sources, fully offline
- Preserve upstream Cargo.lock and Cargo's generated source configuration
- Remove generated Fedora crate BuildRequires and record bundled crates

* Tue Nov 03 2026 COPR maintainer - 0.11.1-2
- Document Fedora 44 missing crate versions found in COPR build 11249235

* Tue Nov 03 2026 COPR maintainer - 0.11.1-1
- Initial Fedora-native COPR spec for Gitte 0.11.1
