# Repeating Arguments — Worked Examples

## Basic: Paired Data Groups

Accept repeating (x, y) pairs for plotting:

```matlab
function plotMultiSeries(x, y)
    arguments (Repeating)
        x (1,:) double {mustBeFinite}
        y (1,:) double {mustBeFinite}
    end

    figure;
    hold on;
    for i = 1:numel(x)
        plot(x{i}, y{i});
    end
    hold off;
end
```

Call: `plotMultiSeries([1 2 3], [4 5 6], [1 2 3], [7 8 9])`

In the function body, `x` and `y` are cell arrays. `numel(x)` gives the number of repetitions.

## Three-Element Groups

Accept (x, y, lineSpec) triplets:

```matlab
function styledPlot(x, y, lineSpec)
    arguments (Repeating)
        x (1,:) double {mustBeFinite}
        y (1,:) double {mustBeFinite}
        lineSpec (1,1) string
    end

    figure;
    hold on;
    for i = 1:numel(x)
        plot(x{i}, y{i}, lineSpec{i});
    end
    hold off;
end
```

Call: `styledPlot([1 2 3], [4 5 6], "-r", [1 2 3], [7 8 9], "--b")`

## Two-Block Pattern: Repeating + Name-Value

Combine repeating groups with name-value options using two `arguments` blocks:

```matlab
function stackedBarChart(categories, values, options)
    arguments (Repeating)
        categories (1,:) string
        values (1,:) double {mustBeFinite}
    end
    arguments
        options.Title (1,1) string = ""
        options.ColorMap (1,1) string = "parula"
        options.Normalize (1,1) logical = false
    end

    numGroups = numel(categories);

    % Collect all unique categories
    allCats = categories{1};
    for i = 2:numGroups
        allCats = union(allCats, categories{i}, 'stable');
    end

    % Build data matrix
    dataMatrix = zeros(numel(allCats), numGroups);
    for i = 1:numGroups
        for j = 1:numel(categories{i})
            idx = find(allCats == categories{i}(j), 1);
            dataMatrix(idx, i) = values{i}(j);
        end
    end

    if options.Normalize
        colSums = sum(dataMatrix, 1);
        colSums(colSums == 0) = 1;
        dataMatrix = dataMatrix ./ colSums * 100;
    end

    figure;
    bar(categorical(allCats, allCats), dataMatrix, 'stacked');
    colormap(options.ColorMap);
    if options.Title ~= ""
        title(options.Title);
    end
end
```

Call: `stackedBarChart(["A","B","C"], [10,20,30], ["A","B","C"], [5,15,25], Title="Sales")`

## Key Rules

1. **All args in the repeating block repeat together** — you cannot have some repeat and others not
2. **Variables become cell arrays** — access with `{i}` indexing
3. **No defaults allowed** in repeating blocks
4. **Zero repetitions is valid** — produces 1x0 empty cell arrays
5. **Name-value args go in a separate block** — they cannot be in the same block as repeating args
6. **Only one repeating input block** per function
7. **Do NOT use `varargin`** with argument validation — declare named variables instead

## Repeating Outputs

`arguments (Output, Repeating)` declares a function whose number of outputs
scales with `nargout`. **Only one name is allowed in the block** — MATLAB
rejects multi-name repeating output blocks at parse time with
`MATLAB:functionValidation:MultipleRepeatingOutputs`.

```matlab
% GOOD — single name, pack triples into one cell array
function out = productTriples()
    arguments (Output, Repeating)
        out (1,1) double
    end
    out = cell(1, nargout);
    for k = 1:3:nargout
        b = rand;
        c = rand;
        out{k}   = b * c;
        out{k+1} = b;
        out{k+2} = c;
    end
end
```

Caller: `[p1, a1, b1, p2, a2, b2] = productTriples();`

```matlab
% BAD — multi-name (Output, Repeating) — does not parse
function [p, a, b] = productTriples()
    arguments (Output, Repeating)
        p (1,1) double
        a (1,1) double
        b (1,1) double
    end
    % Error: Declaring multiple repeating output arguments is not supported.
end
```

Key rules:
- One name only; pack groups via convention (e.g. every third output is the
  product, the next two are factors)
- Validators on the single declared name apply to **each cell element**
- Body assigns a `1×nargout` cell; comma-list expansion at the call site
  distributes elements across the requested LHS variables
- Zero outputs is valid (`nargout == 0` ⇒ empty cell)

## Anti-Pattern: varargin in Repeating Block

This is syntactically valid but useless — it provides no validation benefit:

```matlab
% BAD — do not do this
function bad(varargin)
    arguments (Repeating)
        varargin
    end
    % varargin is still just a cell array with no validation
end
```

Instead, declare named variables with types and validators.

----

Copyright 2026 The MathWorks, Inc.

----
