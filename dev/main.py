"""Entry-point CLI para fast-pdf.

Uso: fast-pdf archivo.pdf
"""

import sys


def main() -> int:
    """Entry point que delega al CLI del cliente.

    Returns:
        Código de salida (0 = éxito, 1 = error)
    """
    from dev.client.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
