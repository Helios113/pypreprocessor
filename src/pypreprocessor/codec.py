# codec.py
import codecs
import encodings
from encodings import utf_8
import traceback
from .preprocessor import preprocess


class CodecError(Exception): ...


class Decoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):
        """not used"""
        pass

    def decode(self, data, final=False) -> str:
        """Instance method that processes the buffered data"""
        self.buffer += data
        if self.buffer and final:
            buffer = self.buffer
            self.reset()
            # Decode UTF-8 first
            decoded, consumed = codecs.utf_8_decode(buffer, self.errors, True)
            try:
                # Apply preprocessing
                processed = preprocess(decoded)
            except Exception:
                traceback.print_exc()
                raise
            return processed
        return ""


def decode_function(data: bytes, errors="strict") -> tuple[str, int]:
    """Standalone decode function for the codec"""
    decoded, consumed = codecs.utf_8_decode(data, errors, True)
    try:
        processed = preprocess(decoded)
    except Exception:
        traceback.print_exc()
        raise
    return processed, consumed


def search_function(encoding):
    """Search function to register our custom codec."""
    if encoding != "pypreprocessor":
        return None

    # Get the UTF-8 codec info
    utf8 = encodings.search_function("utf-8")

    try:
        return codecs.CodecInfo(
            name="pypreprocessor",
            encode=utf8.encode,
            decode=decode_function,  # Use the standalone function
            incrementalencoder=utf8.incrementalencoder,
            incrementaldecoder=Decoder,
        )
    except CodecError as exc:
        print(exc)
    except Exception:
        traceback.print_exc()


# Register the codec
codecs.register(search_function)
