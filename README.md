# adopt-plot
### Or AdoptPlot
A library for plotting implicit functions using two rendering engines:

- `contour` from `matplotlib`.
- `plot_implicit` from `sympy` which internally uses **Adaptive Marching Squares (AMR)** — an adaptive algorithm that correctly handles the domain of definition and discontinuities.

**Automatic selection:** If the equation has domain restrictions (e.g., logarithm or square root), `plot_implicit` is used. If the function is smooth, the fast `contour` engine is chosen. Visually, they are indistinguishable, but the best algorithm is selected automatically.

---

## Installation

```bash
pip install adopt-plot
```
## Quick Start
Plot a graph in one line:

```python
from adopt_plot import AdoptPlot

# The plot will open immediately
plot = AdoptPlot("y = 2*x + 2")
```
Or with deferred display (to add custom elements first):

```python
from adopt_plot import AdoptPlot

plot = AdoptPlot("y = sqrt(x)", show=False)
# Add custom elements here:
plot.ax.scatter(2, 2, color='red')
plot.show()
# Show the plot after modifications
```
All plot elements (`axes`, `fig`,  `plt`) are accessible via the plot object and its attributes:

```python
from adopt_plot import AdoptPlot
plot = AdoptPlot("y = 1/x", show=False)
plot.ax.set_xlim(-10, 10)  # Change X-axis limits
plot.save("my_plot.png", dpi=300)# Save to file
```
[![my_plot.png](https://s6.iimage.su/s/06/g81ZrIAx4tGB8TvoKr0Rzd13wLuOoqnIAoEzBQVBz.png)](y=1/x)
```python
from adopt_plot import AdoptPlot

plot = AdoptPlot("sin(sqrt(x**2 + y**2)) / log(x**2 + y**2 + 1) = 0", show=False)

# Подкручиваем стиль под публикацию
plot.ax.set_title("Implicit function with radial oscillations")
plot.ax.grid(True, linestyle=':', alpha=0.5)

# Сохраняем с высоким DPI
plot.save("publication_ready.png", dpi=300, bbox_inches='tight')
plot.show()
```


[![publication_ready.png](https://s6.iimage.su/s/06/g98NejXxyBk91Qy5ygthSKyBm89B2OZZLlKcy5nUp.png)]("sin(sqrt(x**2 + y**2)) / log(x**2 + y**2 + 1) = 0)
## Methods
- **`show`**: Show the figure
- **`save`**: Save the figure
## Parameters

When creating an `AdoptPlot` object, the following parameters are available:

- **`expr`** (`str`): The equation string (e.g., `"y = 1/x"`).
- **`lib`** (`Literal['contour', 'implicit', None]`): Forced rendering engine. Default is `None` (automatic selection).
- **`xlims`, `ylims`** (`Tuple[float, float]`): Initial visible range for the plot. Default `(-20, 20)`.
- **`n`** (`int`): Grid density for the `contour` engine. Default `10000`.
- **`depth`** (`int`): Adaptive refinement depth for `plot_implicit`. Default `9`.
- **`linewidth`** (`float`): Thickness of the plot line. Default `2.0`.
- **`limit`** (`float | Tuple[float, float, float, float]`): Computational domain. Pass a single number (square) or a tuple of 4 numbers `(x_min, x_max, y_min, y_max)`. Default `100`.
- **`color`** (`str`): Line color. Default `'blue'`.
- **`legend`** (`bool`): Whether to display the legend. Default `True`.
- **`points`** (`bool`): Whether to display axis intersection points. Default `True`.
- **`grid`** (`bool`): Whether to display the grid. Default `True`.
- **`interact`** (`bool`): Allow zooming and panning via keyboard (`Ctrl +` and `Ctrl -`). Default `True`.
- **`show`** (`bool`): If `False`, the plot does not open immediately, allowing you to add elements. Default `True`.
- **`text_legend`** (`str`): Additional text for the legend. Default `None`.
## License

Distributed under the **BSD 3-Clause** license.