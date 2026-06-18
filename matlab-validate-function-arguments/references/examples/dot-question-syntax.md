# .?ClassName Syntax — Worked Examples

## Basic Constructor

Import all public settable properties as name-value arguments:

```matlab
classdef SensorConfig
    properties
        SampleRate (1,1) double {mustBePositive} = 1000
        Resolution (1,1) double {mustBePositive, mustBeInteger} = 16
        FilterOrder (1,1) double {mustBePositive, mustBeInteger} = 4
        Label (1,1) string = "unnamed"
    end

    methods
        function obj = SensorConfig(nvArgs)
            arguments
                nvArgs.?SensorConfig
            end
            props = fieldnames(nvArgs);
            for i = 1:numel(props)
                obj.(props{i}) = nvArgs.(props{i});
            end
        end
    end
end
```

Call: `s = SensorConfig(SampleRate=44100, Label="microphone")`

The `.?SensorConfig` line automatically:
- Imports all public properties as valid name-value argument names
- Inherits size, class, and validator constraints from property definitions
- Uses property default values (no need to redeclare)

## Overriding Specific Properties

Add constraints beyond what the property definition provides:

```matlab
function obj = PlotConfig(nvArgs)
    arguments
        nvArgs.?PlotConfig
        nvArgs.LineWidth (1,1) double {mustBeBetween(nvArgs.LineWidth, 0.5, 10, "closed")}
    end
    % Override lines can appear before or after the .? line
    % They add tighter validation than the property definition
end
```

## Static Factory with Forwarding

Use `namedargs2cell` to forward validated args to the constructor:

```matlab
classdef SensorConfig
    % ... properties as above ...

    methods (Static)
        function obj = fromPreset(presetName, nvArgs)
            arguments
                presetName (1,1) string {mustBeMember(presetName, ["audio","vibration"])}
                nvArgs.?SensorConfig
            end

            switch presetName
                case "audio"
                    defaults = struct(SampleRate=44100, Resolution=24, Label="audio");
                case "vibration"
                    defaults = struct(SampleRate=10000, Resolution=16, Label="vibration");
            end

            % Apply caller overrides on top of preset defaults
            overrides = fieldnames(nvArgs);
            for i = 1:numel(overrides)
                defaults.(overrides{i}) = nvArgs.(overrides{i});
            end

            % Forward to constructor
            args = namedargs2cell(defaults);
            obj = SensorConfig(args{:});
        end
    end
end
```

Call: `s = SensorConfig.fromPreset("audio", FilterOrder=8)`

## Wrapper Function Pattern

Wrap another function and forward its name-value args:

```matlab
function myBar(x, y, barArgs)
    arguments
        x (:,:) double
        y (:,:) double
        barArgs.?matlab.graphics.chart.primitive.Bar
    end

    nvCell = namedargs2cell(barArgs);
    bar(x, y, nvCell{:});
end
```

Call: `myBar(x, y, FaceColor="magenta", BarLayout="grouped")`

This imports ALL public settable properties of the `Bar` class as valid name-value args — hundreds of properties, automatically validated.

## Key Rules

1. **Only one `.?ClassName` per arguments block**
2. **Override lines can appear before or after the `.?` line**
3. **Properties must be public and settable** — Dependent, Constant, and private properties are excluded
4. **Defaults come from property definitions** — no need to redeclare them
5. **The struct only contains fields the caller passed** — `fieldnames(nvArgs)` returns only what the user explicitly provided, not all properties. Unpassed properties retain their declared defaults on the object.
6. **Use `namedargs2cell`** to convert the struct back to a cell array for forwarding
7. **Tab completion works automatically** — users see all valid property names

## When NOT to Use .?ClassName

- The class has many properties but only a few should be constructor-settable → manually list the subset
- You need different defaults in the constructor vs the property definition → manually declare with custom defaults
- The class is not yours and you only want to expose a few of its properties → manually list what you want

----

Copyright 2026 The MathWorks, Inc.

----
