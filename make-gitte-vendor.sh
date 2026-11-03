#!/usr/bin/env bash
# Create the two source archives required by the vendored Gitte COPR spec.
# Usage: ./make-gitte-vendor.sh [version] [output_directory]
set -euo pipefail

version="${1:-0.11.1}"
output="${2:-$PWD}"
mkdir -p -- "$output"
output="$(cd "$output" && pwd -P)"

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

source_url="https://codeberg.org/ckruse/Gitte/archive/${version}.tar.gz"
source_archive="${output}/${version}.tar.gz"
vendor_archive="${output}/gitte-${version}-vendor.tar.xz"

for cmd in curl tar cargo xz; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd" >&2; exit 1; }
done

printf 'Fetching Gitte %s...\n' "$version"
curl --fail --location --retry 3 --output "$source_archive" "$source_url"
tar -xzf "$source_archive" -C "$tmp"

project="${tmp}/gitte"
if [[ ! -f "${project}/Cargo.toml" || ! -f "${project}/Cargo.lock" ]]; then
  echo 'Expected Gitte source root gitte/ with Cargo.toml and Cargo.lock.' >&2
  exit 1
fi

(
  cd "$project"
  # Internet access is needed only during SRPM preparation (including COPR
  # SCM make_srpm); the binary RPM build remains offline for Rust crates.
  cargo vendor --locked --versioned-dirs vendor > cargo-vendor-config.toml
  test -s cargo-vendor-config.toml
  test -d vendor

  tar -cJf "$vendor_archive" vendor cargo-vendor-config.toml
)

printf '\nReady for rpmbuild:\n  Source0: %s\n  Source1: %s\n' "$source_archive" "$vendor_archive"
printf 'Keep these archives together with the matching gitte.spec.\n'
