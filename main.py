import argparse
from pathlib import Path

from configurer.ami import ami_configurer_main
from configurer.core import core_configurer_main
from configurer.ova.ova_post_configurer import ova_post_configurer_main
from configurer.ova.ova_pre_configurer import ova_pre_configurer_main
from generic import change_inventory_user
from provisioner import provisioner_main

DEPENDENCIES_FILE_NAME = "wazuh_dependencies.yaml"
DEPENDENCIES_FILE_PATH = Path("provisioner") / "static" / DEPENDENCIES_FILE_NAME


def parse_arguments():
    """
    Parse command-line arguments for the Provisioner and Configurer.

    Returns:
        argparse.Namespace: Parsed command-line arguments.

    Arguments:
        --inventory (str): Path to the inventory file (optional).
        --packages-url-path (str): Path to the packages URL file (required if the provisioner module will be executed).
        --package-type (str): Type of package to provision (optional, default: "rpm", choices: ["rpm", "deb"]).
        --arch (str): Architecture type (optional, default: "x86_64", choices: ["x86_64", "amd64", "arm64", "aarch64"]).
        --dependencies (str): Path to the dependencies file (optional, default: DEPENDENCIES_FILE_PATH).
        --component (str): Component to provision (optional, default: "all", choices: ["wazuh_indexer", "wazuh_server", "wazuh_dashboard", "all"]).
        --execute (str): Module to execute (required, choices: ["provisioner", "core-configurer", "ami-configurer", "ova-pre-configurer", "ova-post-configurer", "all-ami"]).
    """
    parser = argparse.ArgumentParser(description="Component Provisioner")
    parser.add_argument("--inventory", required=False, help="Path to the inventory file")
    parser.add_argument("--packages-url-path", required=False, help="Path to the packages URL file")
    parser.add_argument("--package-type", required=False, default="rpm", choices=["rpm", "deb"])
    parser.add_argument(
        "--execute",
        required=True,
        choices=[
            "provisioner",
            "core-configurer",
            "ami-configurer",
            "ova-pre-configurer",
            "ova-post-configurer",
            "all-ami",
        ],
    )
    parser.add_argument(
        "--arch",
        required=False,
        default="x86_64",
        choices=["x86_64", "amd64", "arm64", "aarch64"],
    )
    parser.add_argument(
        "--dependencies",
        required=False,
        default=DEPENDENCIES_FILE_PATH,
        help="Path to the dependencies file",
    )
    parser.add_argument(
        "--component",
        required=False,
        default="all",
        choices=["wazuh_indexer", "wazuh_server", "wazuh_dashboard", "all"],
        help="Component to provision",
    )

    return parser.parse_args()


def check_required_arguments(parsed_args):
    if parsed_args.execute in ["provisioner", "all-ami", "ova-post-configurer"] and not parsed_args.packages_url_path:
        raise ValueError(
            '--packages-url-path is required for the "provisioner", "all-ami" and "ova-post-configurer" --execute value'
        )

    if parsed_args.execute in ["ami-configurer", "all-ami"] and not parsed_args.inventory:
        raise ValueError('--inventory is required for the "ami-configurer" and "all-ami" --execute value')


def main():
    """
    Main entry point for the script.

    This function parses the command-line arguments and executes the appropriate
    subcommands based on the `--execute` argument. It supports the following
    subcommands:
    - `provisioner`: Executes the provisioner logic, which requires the
        `--packages-url-path` argument along with other optional arguments.
    - `configurer`: Executes the core configurer logic.
    - `all`: Executes both the provisioner and configurer logic.

    Raises:
            ValueError: If the `--packages-url-path` argument is missing when the
            `provisioner` or `all` subcommand is executed.
    """

    parsed_args = parse_arguments()
    check_required_arguments(parsed_args)

    if parsed_args.execute in ["ami-configurer", "all-ami"]:
        ami_configurer_main(inventory_path=parsed_args.inventory)
        change_inventory_user(inventory_path=parsed_args.inventory, new_user="wazuh-user")

    if parsed_args.execute in ["ova-pre-configurer"]:
        ova_pre_configurer_main()

    if parsed_args.execute in ["provisioner", "all-ami", "ova-post-configurer"]:
        provisioner_main(
            packages_url_path=Path(parsed_args.packages_url_path),
            package_type=parsed_args.package_type,
            arch=parsed_args.arch,
            dependencies=Path(parsed_args.dependencies),
            component=parsed_args.component,
            inventory=parsed_args.inventory,
        )

    if parsed_args.execute in ["core-configurer", "all-ami", "ova-post-configurer"]:
        core_configurer_main(inventory_path=parsed_args.inventory)

    if parsed_args.execute in ["ova-post-configurer"]:
        ova_post_configurer_main()


if __name__ == "__main__":
    main()
