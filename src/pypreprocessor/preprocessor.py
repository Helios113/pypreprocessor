from io import StringIO
import keyword
from tokenize import TokenInfo, generate_tokens
import tokenize


def preprocess_directives(data: str, defines=None):
    """
    Process #ifdef, #ifndef, #else, #elif, #endif, #define, #undef, #execute, #endexecute directives.
    Returns the processed source code as a string.
    """
    if defines is None:
        defines = set()
    else:
        defines = set(defines)

    lines = data.splitlines(keepends=True)
    output_lines = []

    # Stack to track conditional compilation state
    # Each entry is (condition_met, else_seen)
    state_stack = []

    # Track execute blocks
    in_execute_block = False
    execute_code_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()

        # Check if this is a preprocessor directive
        if stripped.startswith("# "):
            directive_parts = stripped[2:].split(None, 1)
            if not directive_parts:
                i += 1
                continue

            directive = directive_parts[0]
            args = directive_parts[1].strip() if len(directive_parts) > 1 else ""

            # Determine if we're currently in an active block
            currently_active = all(cond for cond, _ in state_stack)

            # Handle execute/endexecute specially
            if directive == "execute":
                if currently_active:
                    in_execute_block = True
                    execute_code_lines = []
                i += 1
                continue

            elif directive == "endexecute":
                if currently_active and in_execute_block:
                    # Execute the collected code
                    exec_code = "".join(execute_code_lines)
                    exec_globals = {"defines": defines}
                    try:
                        exec(exec_code, exec_globals)
                    except Exception as e:
                        raise SyntaxError(
                            f"Error executing code block at line {i + 1}: {e}"
                        )
                    in_execute_block = False
                    execute_code_lines = []
                i += 1
                continue

            if directive == "define":
                if currently_active:
                    defines.add(args)

            elif directive == "undef":
                if currently_active:
                    defines.discard(args)

            elif directive == "ifdef":
                condition_met = args in defines
                state_stack.append((condition_met, False))

            elif directive == "ifndef":
                condition_met = args not in defines
                state_stack.append((condition_met, False))

            elif directive == "else":
                if not state_stack:
                    raise SyntaxError(
                        f"#else without matching #ifdef/#ifndef at line {i + 1}"
                    )
                condition_met, else_seen = state_stack.pop()
                if else_seen:
                    raise SyntaxError(
                        f"Multiple #else for same #ifdef/#ifndef at line {i + 1}"
                    )
                # Flip the condition: if previous was true, now false; if false, now true
                state_stack.append((not condition_met, True))

            elif directive == "elif":
                if not state_stack:
                    raise SyntaxError(
                        f"#elif without matching #ifdef/#ifndef at line {i + 1}"
                    )
                condition_met, else_seen = state_stack.pop()
                if else_seen:
                    raise SyntaxError(f"#elif after #else at line {i + 1}")
                # If previous condition was met, skip this elif
                if condition_met:
                    state_stack.append((False, False))
                else:
                    # Evaluate the elif condition
                    new_condition = args in defines
                    state_stack.append((new_condition, False))

            elif directive == "endif":
                if not state_stack:
                    raise SyntaxError(
                        f"#endif without matching #ifdef/#ifndef at line {i + 1}"
                    )
                state_stack.pop()

            else:
                # Unknown directive, keep it if we're in an active block
                if currently_active:
                    output_lines.append(line)

        else:
            # Regular line - check if we're in an execute block first
            if in_execute_block and all(cond for cond, _ in state_stack):
                execute_code_lines.append(line)
            # Otherwise include it if all conditions are met
            elif all(cond for cond, _ in state_stack):
                output_lines.append(line)

        i += 1

    if state_stack:
        raise SyntaxError("Unclosed #ifdef/#ifndef directive")

    return "".join(output_lines)


def preprocess(data: str, defines=None):
    """
    Process preprocessor directives (#ifdef, #define, etc.)
    """
    return preprocess_directives(data, defines)
