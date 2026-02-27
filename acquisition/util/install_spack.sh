#!/bin/bash
# Data acquisition script for install_spack.sh in the NORC performance measurement pipeline.
#
# Copyright (c) 2026 TU Darmstadt, Germany
# Version: v0.2
# Date: 2025-08-08
#
# Licensed under the BSD 3-Clause License.
# For more information, see the LICENSE file in the project root:
# https://github.com/tuda-parallel/NORC/blob/main/LICENSE
pushd "$INSTALL_DIR"

if [ ! -d "spack" ]; then
  print_info "Downloading Spack"
  git clone -c feature.manyFiles=true https://github.com/spack/spack.git
  check_failure "Failed to download Spack"
else
  print_info "Spack is already installed"
fi

#if spack exist prior, unload it
if ! command -v spack >/dev/null 2>&1; then
  if [ -f ../config/force_local_run ]; then
    # Remove Spack shell functions
    unset -f spack
    unset SPACK_ROOT
    unset SPACK_ENV
    unset SPACK_USER_CACHE
  else
    module unload spack
  fi
fi

# Always use local Spack regardless of system install
export SPACK_ROOT=$(pwd)/spack
source "$SPACK_ROOT/share/spack/setup-env.sh"
check_failure "Failed to setup environment for using Spack"
# add new compilers to spack

if ! spack compiler find; then
  spack compiler find /usr/bin /bin /usr/local/bin
  check_failure "Failed to setup compilers for using Spack"
fi

print_success "Successfully installed Spack"
popd
