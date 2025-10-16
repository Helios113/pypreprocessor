import codecs
import encodings
from encodings import utf_8
import traceback
from .preprocessor import preprocess


class CodecError(Exception): ...


class Decoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):
        """not used"""

    @staticmethod
    def do_decode(data: bytes, errors="strict") -> tuple[str, int]:
        decoded, consumed = codecs.utf_8_decode(data, errors, True)
        try:
            processed = preprocess(decoded)
        except Exception:
            traceback.print_exc()
            raise
        return processed, consumed

    def decode(self, data, final=False) -> str:
        self.buffer += data

        if self.buffer and final:
            buffer = self.buffer
            self.reset()
            return self.do_decode(buffer, self.errors)[0]

        return ""


def search_function(encoding):
    """Search function to register our custom codec."""
    if encoding != "pypreprocessor":
        return None

    # Get the UTF-8 codec info
    utf8 = encodings.search_function("utf-8")

    # Return a CodecInfo object with our custom decoder
    try:
        return codecs.CodecInfo(
            name="pypreprocessor",
            encode=utf8.encode,
            decode=Decoder.decode,
            incrementalencoder=utf8.incrementalencoder,
            incrementaldecoder=Decoder,
        )
    except CodecError as exc:
        print(exc)
    except Exception:
        traceback.print_exc()


# Register the codec
codecs.register(search_function)
