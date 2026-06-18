
# Grouping and Aggregation

**Contents:** groupsummary (methods, binning), groupcounts, groupfilter, grouptransform, pivot

## Use `groupsummary` for grouping operations, not loops or `accumarray`
```matlab
G = groupsummary(T,"Category",["min" "mean" "max"],"Value");

% Multiple grouping variables
G = groupsummary(T,["Category" "Region"],"mean","Value");

% Multiple data variables
G = groupsummary(T,"Category","mean",["Sales" "Cost" "Margin"]);

% Custom aggregation with a function handle
G = groupsummary(T,"Category",@(x) quantile(x,[0.25 0.75]),"Value");

% Avoid: Loop over groups
groups = unique(T.Category);
result = table();
for i = 1:numel(groups)
    subset = T(T.Category == groups(i), :);
    result(i,:) = table(groups(i),mean(subset.Value),std(subset.Value));
end

% Avoid: accumarray (cumbersome, does not support tables)
[G,groupNames] = findgroups(T.Category);
means = accumarray(G,T.Value,[],@mean);
```

When using `groupsummary` with tabular input, the output table always includes a `GroupCount` variable, so there is no need to specify a separate count method. If you only need counts, use `groupcounts` instead.

**Note:** Do not use `"numel"` or `"counts"` as `groupsummary` method names - these are not valid and will error. Valid built-in method names: `"sum"`, `"mean"`, `"median"`, `"mode"`, `"var"`, `"std"`, `"min"`, `"max"`, `"range"`, `"nummissing"`, `"numunique"`, `"nnz"`, `"all"`.

**Prefer string method names over function handles** (e.g., `"mean"` not `@mean`). Named methods use accelerated code paths and are significantly faster on large datasets.

**Pitfall:** Do not use `findgroups`+`accumarray` for aggregation when `groupsummary` can do the job — `groupsummary` is simpler, faster, and works directly with tables. Use `findgroups` alone only when you need group indices without aggregation (e.g., to assign a group ID column).

### On-the-fly binning

`groupsummary` (and `groupcounts`, `groupfilter`, `grouptransform`) support binning rules as the grouping variable, so you don't need to create a binned column with `discretize` first:
```matlab
% Bin a numeric variable with custom edges
G = groupsummary(T,"Age",[0 18 35 50 Inf],"mean","Income");

% Equal-width bins
G = groupsummary(T,"Score",10,"mean","Value");   % 10 bins

% Time-based binning
G = groupsummary(TT,"Time","hour","mean","Temperature");
G = groupsummary(TT,"Time","month",["mean" "std"],"Sales");

% Mix regular grouping and binning
G = groupsummary(T,{"Region","Age"},{"none",[0 18 35 50 Inf]},"mean","Salary");
```

## Use `groupsummary` not `grpstats`
```matlab
G = groupsummary(T,"Category",["min" "mean" "max"],"Value");
G = groupsummary(T,"Category",@(x) [min(x,[],"omitnan") mean(x,"omitnan") max(x,[],"omitnan")],"Value");

% Less portable: Statistics Toolbox required
[means,groups] = grpstats(T.Value,T.Category,"mean");
```

## Use `groupcounts` not manual tabulation
```matlab
G = groupcounts(T,"Category");

% Avoid: Manual counting
categories = unique(T.Category);
counts = zeros(numel(categories),1);
for i = 1:numel(categories)
    counts(i) = sum(T.Category == categories(i));
end

% Less portable: Statistics Toolbox required, does not support tables
counts = tabulate(T.Category);
```

When using `groupcounts` or `groupsummary`, consider:
- `IncludeMissingGroups=false` to exclude groups defined by a missing value (such as `NaN` for numeric types), which can otherwise dominate results (default: `true`).
- `IncludeEmptyGroups=true` to include all categories of a categorical variable, even those with no rows (default: `false`). Useful when you need a complete picture of all possible groups.

## Use `groupfilter` to filter rows based on group properties

`groupfilter` has two distinct use cases:

**Use case 1: Keep or remove entire groups based on a group-level condition.**
For example, keep only categories that have enough observations to be meaningful:
```matlab
% Keep only groups with at least 10 observations
T = groupfilter(T,"Category",@(x) numel(x) >= 10);

% Keep only groups where the mean value exceeds a threshold
T = groupfilter(T,"Region",@(x) mean(x) > 50,"Sales");
```

**Use case 2: Filter individual rows within each group.**
For example, remove outliers separately within each group rather than globally:
```matlab
% Remove outliers within each group (not across the whole table)
T = groupfilter(T,"Category",@(x) ~isoutlier(x),"Value");

% Keep only the top 3 rows per group by Value
T = groupfilter(T,"Category",@topN,"Value");

function tf = topN(x)
    [~,idx] = maxk(x,3,ComparisonMethod="abs");
    tf = false(size(x));
    tf(idx) = true;
end
```

The key distinction: when the function returns one logical per group, it filters entire groups. When it returns one logical per row, it filters individual rows within each group.

## Use `grouptransform` to transform data within each group

`grouptransform` applies a transformation within each group and returns a same-size result - use it to normalize, fill, center, or apply custom per-group logic without reducing rows:
```matlab
% Normalize values within each group (per-group z-score)
T = grouptransform(T,"Category","zscore","Value");

% Other built-in methods:
%   "norm"       - normalize by 2-norm
%   "meancenter" - subtract group mean
%   "rescale"    - rescale to [0, 1] within each group
%   "meanfill"   - fill missing values with group mean
%   "linearfill" - fill missing values by linear interpolation within group

% Custom function handle: return same-size or scalar (broadcast) result
T.PctOfGroup = grouptransform(T,"Category", ...
    @(x) x / sum(x) * 100,"Value");
```

## Use `pivot` not `unstack` workarounds
```matlab
% Direct pivot (introduced in R2023a)
% Default (no DataVariable/Method) returns counts per group for non-numeric
% data variables and sum for numeric
P = pivot(T, Rows="Category", Columns="Region");

% Aggregate a specific variable with DataVariable and Method
P = pivot(T, Rows="Category", Columns="Region", DataVariable="Sales", Method="sum");

% Avoid: Manual pivot
G = groupsummary(T,["Row" "Col"],"sum","Value");
P = unstack(G,"sum_Value","Col");
```

---

Copyright 2026 The MathWorks, Inc.
