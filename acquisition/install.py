# !/usr/bin/env python3
import argparse
import os
import shutil
import sys
import subprocess
import stat
from pathlib import Path

from util.utils import Logger

def cleanup(tmp_dir, build_dir):
    Logger.info("Removing previous installation and temporary files")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    shutil.rmtree(build_dir, ignore_errors=True)


def try_run(command, error_message, **kwargs):
    try:
        subprocess.run(command, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        Logger.error(f"{error_message} (Return code: {e.returncode})")
        sys.exit(1)


def chmod_x(filepath):
    path_obj = Path(filepath)
    if path_obj.exists():
        path_obj.chmod(path_obj.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                                               | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH )

def load_bash_config(filepath):
    """Natively parses a basic bash configuration file (VAR=value) into a dictionary."""
    config = {}
    path_obj = Path(filepath)
    if not path_obj.exists():
        return config

    with open(path_obj, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                # Strip quotes and spaces
                config[key.strip()] = val.strip(' \'"')
    return config

def install_noigena(tmp_dir, build_dir, custom_env):
    #TODO Move Noigena logic here
    Logger.success("NOIGENA installed successfully.")

def main():
    ## folder structure ##
    base_dir = Path(__file__).resolve().parent
    config_dir = base_dir / "config"
    build_dir = base_dir / "build"
    bin_dir = build_dir / "bin"
    lib_dir = build_dir / "lib"
    tmp_dir = base_dir / "tmp"

    for directory in [config_dir, build_dir, bin_dir, lib_dir, tmp_dir]:
        directory.mkdir(parents=True, exist_ok=True)


    ## args processing ##
    parser = argparse.ArgumentParser(description='Setup for Data Acquisition')
    parser.add_argument('-f', '--force', action='store_true', help="Force-rebuilding everything.")
    parser.add_argument('-s', '--skip', action='store_true', help="Skipping installation.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Skipping interactive prompts.")
    args = parser.parse_args()

    do_install = not args.skip
    if args.force:
        Logger.info("-f specified. Force-rebuilding everything.")
        cleanup(tmp_dir, build_dir)
        for directory in [config_dir, build_dir, bin_dir, lib_dir, tmp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    if args.skip:
        Logger.info("-s specified. Skipping installation.")
    if args.quiet:
        Logger.info("-q specified. Skipping interactive prompts.")

    ## config check ##
    config_done_file = config_dir / "config_done"
    build_settings_file = config_dir / "build_settings.sh"

    if not args.quiet and not config_done_file.exists():
        var = input("Is the configuration updated for this system? [y/N]: ")
        if var.lower() != "y":
            # TODO replace with python ? What about native Counter?
            config_assist_path = base_dir / "util" / "config_assistent.sh"
            chmod_x(config_assist_path)
            try_run([str(config_assist_path)], "Configuration not finalized!")
        config_done_file.touch()

    # Load settings into Python dictionary
    settings = load_bash_config(build_settings_file)
    use_spack = settings.get("USE_SPACK", "true").lower() == "true"
    spack_version_suffix = settings.get("SPACK_VERSION_SUFFIX", "")
    scorep_version = settings.get("SCOREP_VERSION", "8.3")

    local_run = (config_dir / "force_local_run").exists()
    if local_run:
        Logger.info("Local installation. Skipping loading modules")
    else:
        Logger.info("Loading modules")
        Logger.warn("Not Implemented yet")
        modules_sh_path = config_dir / "modules.sh"
        # TDOD Capture paths? aftet config assist
        #subprocess.run(str(modules_sh_path))

    # sh compatability
    macros_source = base_dir / "util" / "macros.sh"
    if macros_source.exists():
        shutil.copy(macros_source, build_dir)

    ## Virtual Environment Noigenia Setup ##
    venv_dir = tmp_dir / ".venv"
    venv_bin_dir = venv_dir / "bin"
    if not venv_dir.is_dir():
        try_run([sys.executable, "-m", "venv", str(venv_dir)], "Could not make .venv")
        try_run([str(venv_bin_dir / "pip"), "install", "--upgrade", "pip", "numpy", "PyYaml"],
                "Could not install dependencies in venv")

    # Prepend venv to python os.environ natively
    os.environ["PATH"] = f"{venv_bin_dir}:{os.environ.get('PATH', '')}"
    env_sh_path = f"{venv_bin_dir}:{bin_dir}:/bin:/usr/sbin"

    env_script = build_dir / "env.sh"
    init_script = build_dir / "init.sh"

    # TODO Maybe move to func with bottom half
    with open(env_script, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Basic environment for running and evaluating benchmarks.\n")
        f.write("# This script should be sourced before running benchmarks.\n\n")

    with open(init_script, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("source ./env.sh\n")

    chmod_x(env_script)
    chmod_x(init_script)

    Logger.info(f"Installing into target directory {build_dir}")

    def install_spack():
        Logger.info("Setting up Spack...")
        spack_dir = build_dir / "spack"
        if not spack_dir.is_dir():
            Logger.info("Cloning Spack repository...")
            try_run(["git", "clone", "-c", "feature.manyFiles=true",
                     "https://github.com/spack/spack.git"], "Failed to download Spack", cwd=build_dir)
        else:
            Logger.info("Spack is already installed. Skipping download. ")
        return spack_dir

    def get_spack_package(spack_bin_path, package_name, binary_name):
        try:
            prefix = subprocess.check_output([str(spack_bin_path), "location", "-i", package_name], text=True).strip()
            package_bin_path = Path(prefix) / "bin" / binary_name
            if not package_bin_path.exists():
                Logger.error(f"Binary {binary_name} of Package {package_name} not found.")
                sys.exit(1)
            return package_bin_path
        except subprocess.CalledProcessError:
            Logger.error(f"Spack could not locate package: {package_name}")
            sys.exit(1)

    spack_bin = ""
    spack_root = ""
    # TODO temp environment for "install_niogena.sh" and "build.sh" files
    custom_env = os.environ.copy()
    custom_env.update({
        'CONFIG_DIR': str(config_dir),
        'BASE_DIR': str(base_dir),
        'INSTALL_DIR': str(build_dir),
        'TMP_DIR': str(tmp_dir)
    })

    #todo move to own funktion
    if do_install:
        Logger.info("Installing dependencies...")
        if use_spack:
            spack_root = install_spack()
            spack_bin = spack_root / "bin" / "spack"

            # Score-P with PAPI
            Logger.info("Installing Score-P with Spack.")
            scorep_name = f"scorep@{scorep_version}"
            try_run([str(spack_bin), "install", scorep_name, "+papi", "+mpi", spack_version_suffix],
                    "Failed to install Score-P")
            shutil.copy(get_spack_package(spack_bin, f"{scorep_name}{spack_version_suffix}", "scorep-score"), bin_dir)
            Logger.success("Successfully installed Score-P.")

            # PAPI
            Logger.info("Loading PAPI with Spack.")
            papi_name = f"papi{spack_version_suffix}"
            shutil.copy(get_spack_package(spack_bin, papi_name, "papi_avail"), bin_dir)
            shutil.copy(get_spack_package(spack_bin, papi_name, "papi_event_chooser"), bin_dir)
            Logger.success("Successfully loaded PAPI.")

            # SIONlib
            Logger.info("Installing SIONlib with Spack.")
            sionlib_name = "sionlib fflags=-fallow-argument-mismatch" + spack_version_suffix
            try_run([str(spack_bin), "install", "sionlib", "fflags=-fallow-argument-mismatch", spack_version_suffix],
                    "Failed to install SIONlib")
            shutil.copy(get_spack_package(spack_bin, sionlib_name, "sionconfig"), bin_dir)
            Logger.success("Successfully installed SIONlib.")

            # CMake
            Logger.info("Building CMake via Spack...")
            try_run([str(spack_bin), "install", "cmake", spack_version_suffix], "Failed to install CMake")
            Logger.success("Successfully installed CMake.")

        #Noigena Install + cmake for builds?
        #Spack loader
        if use_spack:
            Logger.info("Injecting Spack modules into NOIGENA build environment...")
            try:
                mpi_prefix = subprocess.check_output([str(spack_bin), "location", "-i", "mpi"], text=True).strip()
                sionlib_prefix = subprocess.check_output([str(spack_bin), "location", "-i", "sionlib"],text=True).strip()
                cmake_prefix = subprocess.check_output([str(spack_bin), "location", "-i", "cmake"], text=True).strip()
                # Prepend Spack bin directories to the PATH
                custom_env["PATH"] = f"{cmake_prefix}/bin:{mpi_prefix}/bin:{sionlib_prefix}/bin:{custom_env.get('PATH', '')}"
            except subprocess.CalledProcessError:
                Logger.error("Could not fetch Spack module paths for NOIGENA")
                sys.exit(1)

            custom_env["PATH"] = f"{mpi_prefix}/bin:{custom_env.get('PATH', '')}"
            custom_env["PATH"] = f"{sionlib_prefix}/bin:{custom_env.get('PATH', '')}"

        custom_env["PATH"] = f"{tmp_dir / '.venv' / 'bin'}:{custom_env.get('PATH', '')}"
        install_noigena_path = base_dir / "util" / "install_noigena.sh"
        chmod_x(install_noigena_path)
        if install_noigena_path.exists():
            try_run([str(install_noigena_path)], "Setup failed for NOIGENA", env=custom_env)

        install_noigena(tmp_dir,build_dir,custom_env)
        #TODO put things above in the actual function

    os.environ['PATH'] = f"{bin_dir}:{os.environ.get('PATH', '')}"
    custom_env['PATH'] = f"{bin_dir}:{custom_env.get('PATH', '')}"
    # prepends all spack bin directories to env_sh_path
    if spack_root:
        spack_opt = Path(spack_root) / "opt" / "spack"
        bin_folders = [str(p) for p in spack_opt.rglob("bin") if p.is_dir()]
        bin_folders_joined = ":".join(bin_folders)
        env_sh_path = bin_folders_joined+":"+env_sh_path

    # TODO Maybe move to func with top half
    # finish env.sh
    env_sh_path = str(bin_dir) + ":"+ env_sh_path
    with open(env_script, "a") as f:
        f.write(f'export PATH="{env_sh_path}"\n')
        #f.write(f'export LD_LIBRARY_PATH="{os.environ.get("LD_LIBRARY_PATH", "")}"\n')
        f.write(f'export LD_LIBRARY_PATH="{build_dir}/lib:$LD_LIBRARY_PATH"\n')
        f.write('export SCOREP_ENABLE_PROFILING="true"\n')
        f.write('export SCOREP_ENABLE_TRACING="false"\n')
        if use_spack:
            f.write(f'\nsource "{build_dir}/spack/share/spack/setup-env.sh"\n')
            f.write('spack load mpi\n')

    tmp_bin_dir = tmp_dir / "bin"
    tmp_bin_dir.mkdir(exist_ok=True)
    os.environ['PATH'] = f"{os.environ.get('PATH', '')}:{tmp_bin_dir}"
    custom_env['PATH'] = f"{custom_env.get('PATH', '')}:{tmp_bin_dir}"

    # Compiler alias mapping
    try:
        scorep_loc = subprocess.check_output(
            [str(spack_bin), "location", "-i", f"scorep@{scorep_version}{spack_version_suffix}"], text=True).strip()
        scorep_bin_path = Path(scorep_loc) / "bin"

        # 1. Symlink for C++ compiler
        mpicpp_orig_path = scorep_bin_path / "scorep-mpic++"
        mpicpp_symlink_path = tmp_bin_dir / "scorep-mpicxx"
        mpicpp_symlink_path.unlink(missing_ok=True)
        mpicpp_symlink_path.symlink_to(mpicpp_orig_path)

        # 2. Symlink for C compiler
        mpicc_orig_path = scorep_bin_path / "scorep-mpicc"
        mpicc_symlink_path = tmp_bin_dir / "scorep-mpicc"
        mpicc_symlink_path.unlink(missing_ok=True)
        mpicc_symlink_path.symlink_to(mpicc_orig_path)

        Logger.success("Successfully aliased Score-P MPI compilers.")

    except subprocess.CalledProcessError:
        Logger.error("No Score-P compilers found.")
        sys.exit(1)
    try:
       subprocess.run(["which", "scorep-mpicxx"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        Logger.error("No Score-P MPI C++ compiler found.")
        sys.exit(1)

    try:
       subprocess.run(["which", "scorep-mpicc"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        Logger.error("No Score-P MPI C compiler found.")
        sys.exit(1)

    try:
        subprocess.run(["which", "papi_avail"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        Logger.error("No PAPI command found.")
        sys.exit(1)


    #### Experiment Structure ####
    def ensure_newline(filepath):
        if Path(filepath).exists() and Path(filepath).stat().st_size > 0:
            with open(filepath, "r+b") as _f:
                _f.seek(-1, os.SEEK_END)
                if _f.read(1) != b'\n':
                    _f.write(b'\n')

    experiment_dir = build_dir / "experiment"
    shutil.rmtree(experiment_dir, ignore_errors=True)
    experiment_dir.mkdir(parents=True, exist_ok=True)

    # Place central configuration into the experiment directory
    experiment_config_dir = experiment_dir / "config"
    shutil.copytree(config_dir, experiment_config_dir, dirs_exist_ok=True)

    for cfg_file in ["experiments.cfg", "metrics.cfg", "noise.cfg"]:
        ensure_newline(experiment_config_dir / cfg_file)

    # Put run script in the build directory for execution
    runner_dir = base_dir / "runner"
    Path(runner_dir).mkdir(parents=True, exist_ok=True)
    shutil.copytree(runner_dir, build_dir, dirs_exist_ok=True)
    for runner_file in runner_dir.iterdir():
        if runner_file.is_file():
            chmod_x(runner_file)

    run_benchmarks_sh = build_dir / "run_benchmarks.sh"
    if run_benchmarks_sh.exists():
        chmod_x(run_benchmarks_sh)

    # Create per-benchmark configuration directory
    (experiment_config_dir / "benchmarks").mkdir(parents=True, exist_ok=True)

    # Automatically install all specified benchmarks
    benchmarks_dir = base_dir / "benchmarks"
    if benchmarks_dir.exists():
        for benchmark_path in benchmarks_dir.iterdir():
            benchmark_name = benchmark_path.name

            # Skip if it's the 'template' directory or if not a directory
            if benchmark_name == "template" or not benchmark_path.is_dir():
                continue

            # Skip if 'build.sh' is missing
            build_script = benchmark_path / "build.sh"
            if not build_script.exists():
                continue

            Logger.info(f"Processing benchmark: {benchmark_name}")

            # Put the resources where the runner expects them
            target_bench_dir = experiment_config_dir / "benchmarks" / benchmark_name
            shutil.copytree(benchmark_path, target_bench_dir, dirs_exist_ok=True)
            (target_bench_dir / "build.sh").unlink(missing_ok=True)

            # Build the benchmark
            if (bin_dir / benchmark_name).exists():
                Logger.info(f"{benchmark_name} is already built.")
                continue

            chmod_x(build_script)
            # TODO Missing Shebangs ?
            # try_run(["./build.sh"], f"Failed to build {benchmark_name}", cwd=benchmark_path, env=custom_env)
            try_run(["/bin/bash","./build.sh"], f"Failed to build {benchmark_name}", cwd=benchmark_path, env=custom_env, stdout=subprocess.DEVNULL)
    else:
        Logger.warn("No benchmarks found.")

    # permission fixing
    run_sh = base_dir / "run.sh"
    if run_sh.exists():
        chmod_x(run_sh)
    fake_slurm = build_dir / "fake_slurm"
    if fake_slurm.exists():
        for file in fake_slurm.iterdir():
            chmod_x(file)

    Logger.success("Successfully installed and configured all components.")


if __name__ == "__main__":
    main()