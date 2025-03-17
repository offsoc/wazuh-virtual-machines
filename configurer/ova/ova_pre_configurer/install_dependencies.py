import os
import re

import requests

from configurer.utils import run_command
from utils import Logger

logger = Logger("OVA PreConfigurer - Dependencies Installer")

VIRTUALBOX_DOWNLOAD_BASE_URL = "https://download.virtualbox.org/virtualbox/"
REQUIRED_PACKAGES = [
    "kernel-devel",
    "kernel-headers",
    "dkms",
    "elfutils-libelf-devel",
    "gcc",
    "make",
    "perl",
    "python3-pip",
    "git",
]
VAGRANT_REPO_URL = "https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo"


def update_packages() -> None:
    """
    Updates all system packages using the 'yum' package manager.

    Returns:
        None
    """
    logger.info("Updating all system packages.")
    run_command("sudo yum update -y")


def download_virtualbox_installer() -> None:
    """
    Downloads the latest VirtualBox installer for Linux (amd64) and makes it executable.
    This function performs the following steps:
    1. Retrieves the latest stable version of VirtualBox from the official VirtualBox website.
    2. Constructs the download page URL for the latest version.
    3. Downloads the installer to the /tmp directory.
    4. Makes the downloaded installer executable.

    Raises:
        RuntimeError: If there is an error retrieving the latest VirtualBox version.
        Exception: If the installer URL cannot be found on the download page.
        requests.exceptions.RequestException: If there is an error during any of the HTTP requests.
        RuntimeError: If there is an error getting the VirtualBox download page.

    Returns:
        None
    """

    version_url = VIRTUALBOX_DOWNLOAD_BASE_URL + "LATEST-STABLE.TXT"

    try:
        response = requests.get(version_url)
        response.raise_for_status()
        latest_version = response.text.strip()
        logger.info(f"Latest VirtualBox version: {latest_version}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting latest VirtualBox version: {e}")
        raise RuntimeError("Error getting latest VirtualBox version.") from e

    download_page_url = VIRTUALBOX_DOWNLOAD_BASE_URL + f"{latest_version}/"

    try:
        response = requests.get(download_page_url)
        response.raise_for_status()

        match = re.search(rf"VirtualBox-{latest_version}-\d+-Linux_amd64.run", response.text)
        if match:
            installer_url = download_page_url + match.group(0)
            dest = f"/tmp/VirtualBox-{latest_version}.run"

            response = requests.get(installer_url, stream=True)
            response.raise_for_status()

            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"VirtualBox installer version {latest_version} downloaded to {dest}")

            logger.info("Making installer executable.")
            os.chmod(dest, 0o755)

        else:
            logger.error("Could not find VirtualBox installer URL.")
            raise Exception("Could not find VirtualBox installer URL.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting VirtualBox download page: {e}")
        raise RuntimeError("Error getting VirtualBox download page.") from e


def install_required_packages() -> None:
    """
    Installs the required packages and development tools on a system using yum.

    Returns:
        None
    """
    logger.info(f"Installing required packages: {', '.join(REQUIRED_PACKAGES)}")
    run_command("sudo yum install -y " + " ".join(REQUIRED_PACKAGES))

    logger.info("Installing Development tools.")
    run_command("sudo yum groupinstall 'Development Tools' -y")


def run_virtualbox_installer() -> None:
    """
    Executes the VirtualBox installer script.

    Returns:
        None
    """
    logger.info("Running VirtualBox installer.")
    run_command("sudo bash /tmp/VirtualBox-*.run")


def rebuild_virtualbox_kernel_modules() -> None:
    """
    Rebuilds the VirtualBox kernel modules by running the vboxconfig command.

    Returns:
        None
    """
    logger.info("Rebuilding VirtualBox kernel modules.")
    run_command("sudo /sbin/vboxconfig")


def install_vagrant() -> None:
    """
    Installs Vagrant and its dependencies using the specified repository URL.

    Returns:
        None
    """
    logger.info("Installing Vagrant.")
    commands = [
        "sudo yum install -y yum-utils shadow-utils",
        f"sudo yum-config-manager --add-repo {VAGRANT_REPO_URL}",
        "sudo yum -y install vagrant",
    ]
    run_command(commands)


def main() -> None:
    """
    Main function to install dependencies for the OVA PreConfigurer.
    This function performs the following steps:
    1. Updates the package list.
    2. Installs the required packages.
    3. Downloads the VirtualBox installer.
    4. Runs the VirtualBox installer.
    5. Updates the package list again.
    6. Rebuilds the VirtualBox kernel modules.
    7. Installs Vagrant.

    Returns:
        None
    """
    logger.info("Installing dependencies of the OVA PreConfigurer.")

    update_packages()
    install_required_packages()
    download_virtualbox_installer()
    run_virtualbox_installer()
    update_packages()
    rebuild_virtualbox_kernel_modules()
    install_vagrant()


if __name__ == "__main__":
    main()
