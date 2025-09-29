# renumber-notes: re-sequence-number notes filenames
Bart Massey 2025

This Python program operates in a directory containing file
or directory names with (usually) leading sequence
numbers. For example

```
01-beginning.txt
02-intermediate.txt
03-advanced.txt
```

The program can renumber the files conveniently. For example

```
renumber-notes +1 2
```

will `git mv` files to produce

```
01-beginning.txt
03-intermediate.txt
04-advanced.txt
```

Use `--help` to see the many options available.

## Acknowledgements

This program was improved with new features and a test suite
using Claude Code (Sonnet 2.0).

## License

This work is made available under the "MIT License". See the
file `LICENSE.txt` in this distribution for license terms.
