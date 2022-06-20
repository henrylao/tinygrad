# Build Documentation

Run the following
```
make clean & make html
```

Output message
```
[1] 19713
Removing everything under 'build'...
Running Sphinx v5.0.2
making output directory... done
[autosummary] generating autosummary for: README.rst, _autosummary/tinygrad.helpers.rst, _autosummary/tinygrad.mlops.rst, _autosummary/tinygrad.nn.rst, _autosummary/tinygrad.ops.rst, _autosummary/tinygrad.optim.rst, _autosummary/tinygrad.rst, _autosummary/tinygrad.shapetracker.rst, _autosummary/tinygrad.tensor.rst, index.rst
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 10 source files that are out of date
updating environment: [new config] 10 added, 0 changed, 0 removed
reading sources... [100%] index                                                                          
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [100%] index                                                                           
generating indices... genindex py-modindex done
writing additional pages... search done
copying static files... done
copying extra files... done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.

The HTML pages are in build/html.
[1]+  Done                    make clean

```
