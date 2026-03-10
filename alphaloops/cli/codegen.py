"""Code generation — print SDK usage examples for any CLI command."""

import click


PYTHON_HEADER = '''\
from alphaloops.freight import AlphaLoops

al = AlphaLoops()  # reads key from ~/.alphaloops or ALPHALOOPS_API_KEY
'''

TS_HEADER = '''\
import AlphaLoops from "alphaloops";

const al = new AlphaLoops();  // reads key from ~/.alphaloops or ALPHALOOPS_API_KEY
'''


def _format_kwargs_py(kwargs):
    """Format keyword arguments for Python."""
    parts = []
    for k, v in kwargs.items():
        if v is None:
            continue
        if isinstance(v, str):
            parts.append(f'{k}="{v}"')
        elif isinstance(v, bool):
            parts.append(f'{k}={v}')
        elif isinstance(v, list):
            items = ", ".join(f'"{x}"' for x in v)
            parts.append(f'{k}=[{items}]')
        else:
            parts.append(f'{k}={v}')
    return ", ".join(parts)


def _format_kwargs_ts(kwargs):
    """Format keyword arguments for TypeScript."""
    parts = []
    for k, v in kwargs.items():
        if v is None:
            continue
        # Convert snake_case to camelCase
        camel = "".join(w if i == 0 else w.capitalize() for i, w in enumerate(k.split("_")))
        if isinstance(v, str):
            parts.append(f'{camel}: "{v}"')
        elif isinstance(v, bool):
            parts.append(f'{camel}: {"true" if v else "false"}')
        elif isinstance(v, list):
            items = ", ".join(f'"{x}"' for x in v)
            parts.append(f'{camel}: [{items}]')
        else:
            parts.append(f'{camel}: {v}')
    if not parts:
        return ""
    return "{ " + ", ".join(parts) + " }"


def print_python(method, positional_args, kwargs=None):
    """Print Python SDK example code."""
    kwargs = kwargs or {}
    args_str = ", ".join(f'"{a}"' for a in positional_args)
    kw_str = _format_kwargs_py(kwargs)
    if args_str and kw_str:
        call_args = f"{args_str}, {kw_str}"
    elif args_str:
        call_args = args_str
    else:
        call_args = kw_str

    click.echo(PYTHON_HEADER)
    click.echo(f"result = al.{method}({call_args})")
    click.echo("print(result)")


def print_typescript(method, positional_args, kwargs=None):
    """Print TypeScript SDK example code."""
    kwargs = kwargs or {}
    args_str = ", ".join(f'"{a}"' for a in positional_args)
    opts_str = _format_kwargs_ts(kwargs)
    if args_str and opts_str:
        call_args = f"{args_str}, {opts_str}"
    elif args_str:
        call_args = args_str
    else:
        call_args = opts_str

    click.echo(TS_HEADER)
    click.echo(f"const result = await al.{method}({call_args});")
    click.echo("console.log(result);")
