# Wazuh Virtual Machines Technical Documentation

This folder contains the technical documentation for the Wazuh OVA and the Wazuh AMI. The documentation is organized into the following guides:

- **Development Guide**: Instruction for building, testing and generate the OVA and AMI artifacts.
- **Reference Manual**: Detailed information about the OVA and AMI architecture, configuration and usage.

## Requirements

To work with this documentation, you need **mdBook** installed. For installation instructions, refer to the [mdBook documentation](https://rust-lang.github.io/mdBook/).

## Usage

- To build the documentation, run:

  ```bash
  ./build.sh
  ```

  The output will be generated in the `book` directory.

- To serve the documentation locally for preview, run:

  ```bash
  ./server.sh
  ```

  The documentation will be available at [http://127.0.0.1:3000](http://127.0.0.1:3000).
