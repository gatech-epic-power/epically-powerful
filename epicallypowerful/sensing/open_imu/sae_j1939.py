"""Basic conversions for some SAE-J1939 CAN protocol."""


class ExtendedID29Bit:
    """Contains a parsed CAN SAE J1939 extended 29 bit id."""

    __slots__ = (
        "_extended_id",
        "_pgn",
        "_source",
        "_priority",
        "_pgn_reserved",
        "_pgn_data_page",
        "_pdu_format",
        "_pdu_specific",
    )

    @classmethod
    def make(cls, priority: int, pgn: int, source: int):
        """ "Construct an ExtendedId29Bit from constituent parameters."""
        if not 0 <= priority < (2**3):
            raise ValueError("Priority must fit into 3 bits")
        
        if not 0 <= pgn < (2**18):
            raise ValueError("PGN must fit into 18 bits")
        
        if not 0 <= source < (2**8):
            raise ValueError("Source must fit into 8 bits")

        extended_id_int = (priority << (18 + 8)) | (pgn << 8) | source

        return cls(extended_id_int)


    def __init__(self, extended_id: int):
        self._extended_id = extended_id
        bits = f"{extended_id:029b}"
        if len(bits) != 29:
            raise ValueError("Require an extended_id that fits into 29 bits")
        pgn_bits = bits[3:-8]

        self._priority = int(bits[:3], base=2)
        self._pgn = int(pgn_bits, base=2)
        self._source = int(bits[-8:], base=2)

        self._pgn_reserved = int(pgn_bits[0], base=2)
        self._pgn_data_page = int(pgn_bits[1], base=2)
        self._pdu_format = int(pgn_bits[2:10], base=2)
        self._pdu_specific = int(pgn_bits[10:18], base=2)


    @property
    def extended_id(self) -> int:
        return self._extended_id


    @property
    def priority(self) -> int:
        return self._priority


    @property
    def pgn(self) -> int:
        return self._pgn


    @property
    def source(self) -> int:
        return self._source


    @property
    def pgn_reserved(self) -> int:
        return self._pgn_reserved


    @property
    def pgn_data_page(self) -> int:
        return self._pgn_data_page


    @property
    def pdu_format(self) -> int:
        return self._pdu_format


    @property
    def pdu_specific(self) -> int:
        return self._pdu_specific
