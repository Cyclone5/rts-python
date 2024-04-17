from typing import Optional, Any, List
from enum import Enum
from pydantic import BaseModel, field_validator
from matplotlib import pyplot as plt


class PacerState(int, Enum):
    INIT = 0
    PROCESS = 1
    UPDATE = 2
    WAIT = 3
    FINISH = 4
    END = 5
    OVERRUN = 6
    SERIAL = 7


class SerialStore(int, Enum):
    LIST = 0
    SINGLE_VALUE = 1


class PacerPoint(int, Enum):
    BEFORE = 0
    AFTER = 1


class PacerFunction(BaseModel):
    state: PacerState
    mode: PacerPoint
    function: Any
    args: Optional[tuple] = None
    kwargs: Optional[dict] = None

    @field_validator('function')
    def function_validator(cls, v):
        print(type(v))
        if not callable(v):
            raise ValueError('function must be callable')
        return v


# Plots

class PlotType(int, Enum):
    LINE = 0
    SCATTER = 1
    BAR = 2
    HIST = 3
    BOX = 4
    HEATMAP = 5
    CONTOUR = 6


class Plot(BaseModel):
    name: str
    type: PlotType
    x: Optional[List] = None
    y: Optional[List] = None
    z: Optional[List] = None

    @field_validator('x', 'y', 'z')
    def none_control(cls, v):
        if v is not None:
            if v[0] is None:
                return []
            else:
                return v
        else:
            return []


class Plots(BaseModel):
    plots: Optional[List[Plot]] = []

    def add_data(self,
                 plot_name: str,
                 plot_type: Optional[PlotType] = PlotType.LINE,
                 x: Optional[Any] = None,
                 y: Optional[Any] = None,
                 z: Optional[Any] = None
                 ):
        for plot in self.plots:
            if plot.name == plot_name:
                if x is not None:
                    plot.x.append(x)
                if y is not None:
                    plot.y.append(y)
                if z is not None:
                    plot.z.append(z)
                return
        # if plot not found
        self.plots.append(Plot(name=plot_name, type=plot_type, x=[x], y=[y], z=[z]))

    def get_plot_names(self):
        return [plot.name for plot in self.plots]

    def get_plot(self, plot_name):
        for plot in self.plots:
            if plot.name == plot_name:
                return plot
        return None

    def get_plots(self):
        return self.plots

    def show(self, plot_name):
        plot = self.get_plot(plot_name)
        if plot is None:
            return
        Plots._type_matcher(plot)
        plt.show()

    def show_all(self):
        for plot in self.plots:
            Plots._type_matcher(plot)
        plt.show()

    @staticmethod
    def _type_matcher(plot):
        match plot.type:
            case PlotType.LINE:
                plt.plot(plot.x, plot.y)
            case PlotType.SCATTER:
                plt.scatter(plot.x, plot.y)
            case PlotType.BAR:
                plt.bar(plot.x, plot.y)
            case PlotType.HIST:
                plt.hist(plot.x, plot.y)
            case PlotType.BOX:
                plt.boxplot(plot.x, plot.y)
            case PlotType.HEATMAP:
                plt.imshow(plot.z)
            case PlotType.CONTOUR:
                plt.contour(plot.x, plot.y, plot.z)
            case _:
                raise ValueError('plot type not supported')
