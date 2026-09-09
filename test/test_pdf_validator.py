"""Tests para el módulo de validación de PDFs."""

from dev.servers.services.pdf_validator import calculate_checksum


class TestCalculateChecksum:
    """Tests que verifican el cálculo del checksum SHA-256."""

    def test_returns_sha256_hex_digest(self) -> None:
        """El checksum es el hash SHA-256 en hexadecimal del contenido."""
        assert (
            calculate_checksum(b"hello")
            == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        )

    def test_returns_64_char_hex_string(self) -> None:
        """El checksum es un string hexadecimal de 64 caracteres."""
        result = calculate_checksum(b"%PDF-1.4")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_is_deterministic(self) -> None:
        """El mismo contenido produce siempre el mismo checksum."""
        content = b"mismo contenido"
        assert calculate_checksum(content) == calculate_checksum(content)

    def test_different_content_produces_different_checksum(self) -> None:
        """Contenidos distintos producen checksums distintos."""
        assert calculate_checksum(b"contenido A") != calculate_checksum(b"contenido B")
