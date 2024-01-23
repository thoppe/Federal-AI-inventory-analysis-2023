from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.tools import HoverTool


def plot_data_bokeh(df, hover_columns=None, tooltips=None, height=600, width=1600):
    """
    Returns a Bokeh plot at coordinates df.ux and df.uy
    """

    p = figure(
        tools="pan,wheel_zoom,box_zoom,reset,save",
        active_scroll="wheel_zoom",
        output_backend="webgl",
        toolbar_location="below",
        height=height,
        width=width,
        # sizing_mode="scale_height",
        sizing_mode="stretch_both",
    )

    source = ColumnDataSource(df)
    
    p.circle(
        x="ux",
        y="uy",
        source=source,
        color="color",
        size="size",
        radius="size",
        line_width="line_width",
        fill_color="fill_color",
        line_color="black",
        alpha="alpha",
        radius_units="screen",
    )

    # Add the hovering options
    hover = HoverTool()
    hover.tooltips = []

    # Remove repeated columns

    if hover_columns:
        hover_columns = list(dict.fromkeys(hover_columns))

        for column in hover_columns:
            # Remove any null entries
            if column is None:
                continue

            hover.tooltips.append((column, f"@{column}"))

    '''
    if tooltips is not None:
                
        hover = HoverTool(
            tooltips=r"""
        <span>
            📝 @title </br>
        </span>
        """
        )

    '''
    p.add_tools(hover)

    # Hide tick labels
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.outline_line_color = None

    p.xaxis.visible = False
    p.yaxis.visible = False

    return p
