# Streamlit theme for Altair charts
## Simple Bar Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt
import pandas as pd

source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
})

chart = alt.Chart(source).mark_bar().encode(
    x='a',
    y='b'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>


## Simple Heatmap
<pre><code class="language-python">
import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

# Compute x^2 + y^2 across a 2D grid
x, y = np.meshgrid(range(-5, 5), range(-5, 5))
z = x ** 2 + y ** 2

# Convert this grid to columnar data expected by Altair
source = pd.DataFrame({'x': x.ravel(),
                        'y': y.ravel(),
                        'z': z.ravel()})

chart = alt.Chart(source).mark_rect().encode(
    x='x:O',
    y='y:O',
    color='z:Q'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Simple Histogram
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.movies.url

chart = alt.Chart(source).mark_bar().encode(
    alt.X("IMDB_Rating:Q", bin=True),
    y='count()',
)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Simple Line Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

x = np.arange(100)
source = pd.DataFrame({
    'x': x,
    'f(x)': np.sin(x / 5)
})

chart = alt.Chart(source).mark_line().encode(
    x='x',
    y='f(x)'
)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Tooltips
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.cars()

chart = alt.Chart(source).mark_circle(size=60).encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
).interactive()

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Simple Stacked Area Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.iowa_electricity()

chart = alt.Chart(source).mark_area().encode(
    x="year:T",
    y="net_generation:Q",
    color="source:N"
)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Strip Plot
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.cars()

chart = alt.Chart(source).mark_tick().encode(
    x='Horsepower:Q',
    y='Cylinders:O'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart With Highlighted Bar
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.wheat()

chart = alt.Chart(source).mark_bar().encode(
    x='year:O',
    y="wheat:Q",
    # The highlight will be set on the result of a conditional statement
    color=alt.condition(
        alt.datum.year == 1810,  # If the year is 1810 this test returns True,
        alt.value('orange'),     # which sets the bar orange.
        alt.value('steelblue')   # And if it's not true it sets the bar steelblue.
    )
).properties(width=600)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart With Labels
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.wheat()

bars = alt.Chart(source).mark_bar().encode(
    x='wheat:Q',
    y="year:O"
)

text = bars.mark_text(
    align='left',
    baseline='middle',
    dx=3  # Nudges text to right so it doesn't appear on top of the bar
).encode(
    text='wheat:Q'
)

chart = (bars + text).properties(height=900)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart With Mean Line
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.wheat()

bar = alt.Chart(source).mark_bar().encode(
    x='year:O',
    y='wheat:Q'
)

rule = alt.Chart(source).mark_rule(color='red').encode(
    y='mean(wheat):Q'
)

chart = (bar + rule).properties(width=600)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar And Line With Dual Axis
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.wheat()

base = alt.Chart(source).encode(x='year:O')

bar = base.mark_bar().encode(y='wheat:Q')

line =  base.mark_line(color='red').encode(
    y='wages:Q'
)

chart = (bar + line).properties(width=600)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart With Negatives
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.us_employment()

chart = alt.Chart(source).mark_bar().encode(
    x="month:T",
    y="nonfarm_change:Q",
    color=alt.condition(
        alt.datum.nonfarm_change > 0,
        alt.value("steelblue"),  # The positive color
        alt.value("orange")  # The negative color
    )
).properties(width=600)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar With Rolling Mean
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.wheat()

bar = alt.Chart(source).mark_bar().encode(
    x='year:O',
    y='wheat:Q'
)

line = alt.Chart(source).mark_line(color='red').transform_window(
    # The field to average
    rolling_mean='mean(wheat)',
    # The number of values before and after the current value to include.
    frame=[-9, 0]
).encode(
    x='year:O',
    y='rolling_mean:Q'
)

chart = (bar + line).properties(width=600)
 
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Rounded
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.seattle_weather()

chart = alt.Chart(source).mark_bar(
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
).encode(
    x='month(date):O',
    y='count():Q',
    color='weather:N'
)
   
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Layered Chart Bar Mark
<pre><code class="language-python">
import streamlit as st
import altair as alt
import pandas as pd

source = pd.DataFrame({
    'project': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    'score': [25, 57, 23, 19, 8, 47, 8],
    'goal': [25, 47, 30, 27, 38, 19, 4]
})

bar = alt.Chart(source).mark_bar().encode(
    x='project',
    y='score'
).properties(
    width=alt.Step(40)  # controls width of bar.
)

tick = alt.Chart(source).mark_tick(
    color='red',
    thickness=2,
    size=40 * 0.9,  # controls width of tick.
).encode(
    x='project',
    y='goal'
)

chart = bar + tick
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Percentage Of Total
<pre><code class="language-python">
import streamlit as st
import altair as alt
import pandas as pd

source = pd.DataFrame({'Activity': ['Sleeping', 'Eating', 'TV', 'Work', 'Exercise'],
                            'Time': [8, 2, 4, 8, 2]})

chart = alt.Chart(source).transform_joinaggregate(
    TotalTime='sum(Time)',
).transform_calculate(
    PercentOfTotal="datum.Time / datum.TotalTime"
).mark_bar().encode(
    alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
    y='Activity:N'
)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart Trellis Compact
<pre><code class="language-python">
import streamlit as st
import altair as alt
import pandas as pd

source = pd.DataFrame(
    [
        {"a": "a1", "b": "b1", "c": "x", "p": "0.14"},
        {"a": "a1", "b": "b1", "c": "y", "p": "0.60"},
        {"a": "a1", "b": "b1", "c": "z", "p": "0.03"},
        {"a": "a1", "b": "b2", "c": "x", "p": "0.80"},
        {"a": "a1", "b": "b2", "c": "y", "p": "0.38"},
        {"a": "a1", "b": "b2", "c": "z", "p": "0.55"},
        {"a": "a1", "b": "b3", "c": "x", "p": "0.11"},
        {"a": "a1", "b": "b3", "c": "y", "p": "0.58"},
        {"a": "a1", "b": "b3", "c": "z", "p": "0.79"},
        {"a": "a2", "b": "b1", "c": "x", "p": "0.83"},
        {"a": "a2", "b": "b1", "c": "y", "p": "0.87"},
        {"a": "a2", "b": "b1", "c": "z", "p": "0.67"},
        {"a": "a2", "b": "b2", "c": "x", "p": "0.97"},
        {"a": "a2", "b": "b2", "c": "y", "p": "0.84"},
        {"a": "a2", "b": "b2", "c": "z", "p": "0.90"},
        {"a": "a2", "b": "b3", "c": "x", "p": "0.74"},
        {"a": "a2", "b": "b3", "c": "y", "p": "0.64"},
        {"a": "a2", "b": "b3", "c": "z", "p": "0.19"},
        {"a": "a3", "b": "b1", "c": "x", "p": "0.57"},
        {"a": "a3", "b": "b1", "c": "y", "p": "0.35"},
        {"a": "a3", "b": "b1", "c": "z", "p": "0.49"},
        {"a": "a3", "b": "b2", "c": "x", "p": "0.91"},
        {"a": "a3", "b": "b2", "c": "y", "p": "0.38"},
        {"a": "a3", "b": "b2", "c": "z", "p": "0.91"},
        {"a": "a3", "b": "b3", "c": "x", "p": "0.99"},
        {"a": "a3", "b": "b3", "c": "y", "p": "0.80"},
        {"a": "a3", "b": "b3", "c": "z", "p": "0.37"},
    ]
)

chart = alt.Chart(source, width=60, height=alt.Step(8)).mark_bar().encode(
    y=alt.Y("c:N", axis=None),
    x=alt.X("p:Q", title=None, axis=alt.Axis(format="%")),
    color=alt.Color(
        "c:N", title="settings", legend=alt.Legend(orient="bottom", titleOrient="left")
    ),
    row=alt.Row("a:N", title="Factor A", header=alt.Header(labelAngle=0)),
    column=alt.Column("b:N", title="Factor B"),
)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Diverging Stacked Bar Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt

source = alt.pd.DataFrame([
        {
        "question": "Question 1",
        "type": "Strongly disagree",
        "value": 24,
        "percentage": 0.7,
        "percentage_start": -19.1,
        "percentage_end": -18.4
        },
        {
        "question": "Question 1",
        "type": "Disagree",
        "value": 294,
        "percentage": 9.1,
        "percentage_start": -18.4,
        "percentage_end": -9.2
        },
        {
        "question": "Question 1",
        "type": "Neither agree nor disagree",
        "value": 594,
        "percentage": 18.5,
        "percentage_start": -9.2,
        "percentage_end": 9.2
        },
        {
        "question": "Question 1",
        "type": "Agree",
        "value": 1927,
        "percentage": 59.9,
        "percentage_start": 9.2,
        "percentage_end": 69.2
        },
        {
        "question": "Question 1",
        "type": "Strongly agree",
        "value": 376,
        "percentage": 11.7,
        "percentage_start": 69.2,
        "percentage_end": 80.9
        },

        {
        "question": "Question 2",
        "type": "Strongly disagree",
        "value": 2,
        "percentage": 18.2,
        "percentage_start": -36.4,
        "percentage_end": -18.2
        },
        {
        "question": "Question 2",
        "type": "Disagree",
        "value": 2,
        "percentage": 18.2,
        "percentage_start": -18.2,
        "percentage_end": 0
        },
        {
        "question": "Question 2",
        "type": "Neither agree nor disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": 0,
        "percentage_end": 0
        },
        {
        "question": "Question 2",
        "type": "Agree",
        "value": 7,
        "percentage": 63.6,
        "percentage_start": 0,
        "percentage_end": 63.6
        },
        {
        "question": "Question 2",
        "type": "Strongly agree",
        "value": 11,
        "percentage": 0,
        "percentage_start": 63.6,
        "percentage_end": 63.6
        },

        {
        "question": "Question 3",
        "type": "Strongly disagree",
        "value": 2,
        "percentage": 20,
        "percentage_start": -30,
        "percentage_end": -10
        },
        {
        "question": "Question 3",
        "type": "Disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": -10,
        "percentage_end": -10
        },
        {
        "question": "Question 3",
        "type": "Neither agree nor disagree",
        "value": 2,
        "percentage": 20,
        "percentage_start": -10,
        "percentage_end": 10
        },
        {
        "question": "Question 3",
        "type": "Agree",
        "value": 4,
        "percentage": 40,
        "percentage_start": 10,
        "percentage_end": 50
        },
        {
        "question": "Question 3",
        "type": "Strongly agree",
        "value": 2,
        "percentage": 20,
        "percentage_start": 50,
        "percentage_end": 70
        },

        {
        "question": "Question 4",
        "type": "Strongly disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": -15.6,
        "percentage_end": -15.6
        },
        {
        "question": "Question 4",
        "type": "Disagree",
        "value": 2,
        "percentage": 12.5,
        "percentage_start": -15.6,
        "percentage_end": -3.1
        },
        {
        "question": "Question 4",
        "type": "Neither agree nor disagree",
        "value": 1,
        "percentage": 6.3,
        "percentage_start": -3.1,
        "percentage_end": 3.1
        },
        {
        "question": "Question 4",
        "type": "Agree",
        "value": 7,
        "percentage": 43.8,
        "percentage_start": 3.1,
        "percentage_end": 46.9
        },
        {
        "question": "Question 4",
        "type": "Strongly agree",
        "value": 6,
        "percentage": 37.5,
        "percentage_start": 46.9,
        "percentage_end": 84.4
        },

        {
        "question": "Question 5",
        "type": "Strongly disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": -10.4,
        "percentage_end": -10.4
        },
        {
        "question": "Question 5",
        "type": "Disagree",
        "value": 1,
        "percentage": 4.2,
        "percentage_start": -10.4,
        "percentage_end": -6.3
        },
        {
        "question": "Question 5",
        "type": "Neither agree nor disagree",
        "value": 3,
        "percentage": 12.5,
        "percentage_start": -6.3,
        "percentage_end": 6.3
        },
        {
        "question": "Question 5",
        "type": "Agree",
        "value": 16,
        "percentage": 66.7,
        "percentage_start": 6.3,
        "percentage_end": 72.9
        },
        {
        "question": "Question 5",
        "type": "Strongly agree",
        "value": 4,
        "percentage": 16.7,
        "percentage_start": 72.9,
        "percentage_end": 89.6
        },

        {
        "question": "Question 6",
        "type": "Strongly disagree",
        "value": 1,
        "percentage": 6.3,
        "percentage_start": -18.8,
        "percentage_end": -12.5
        },
        {
        "question": "Question 6",
        "type": "Disagree",
        "value": 1,
        "percentage": 6.3,
        "percentage_start": -12.5,
        "percentage_end": -6.3
        },
        {
        "question": "Question 6",
        "type": "Neither agree nor disagree",
        "value": 2,
        "percentage": 12.5,
        "percentage_start": -6.3,
        "percentage_end": 6.3
        },
        {
        "question": "Question 6",
        "type": "Agree",
        "value": 9,
        "percentage": 56.3,
        "percentage_start": 6.3,
        "percentage_end": 62.5
        },
        {
        "question": "Question 6",
        "type": "Strongly agree",
        "value": 3,
        "percentage": 18.8,
        "percentage_start": 62.5,
        "percentage_end": 81.3
        },

        {
        "question": "Question 7",
        "type": "Strongly disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": -10,
        "percentage_end": -10
        },
        {
        "question": "Question 7",
        "type": "Disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": -10,
        "percentage_end": -10
        },
        {
        "question": "Question 7",
        "type": "Neither agree nor disagree",
        "value": 1,
        "percentage": 20,
        "percentage_start": -10,
        "percentage_end": 10
        },
        {
        "question": "Question 7",
        "type": "Agree",
        "value": 4,
        "percentage": 80,
        "percentage_start": 10,
        "percentage_end": 90
        },
        {
        "question": "Question 7",
        "type": "Strongly agree",
        "value": 0,
        "percentage": 0,
        "percentage_start": 90,
        "percentage_end": 90
        },

        {
        "question": "Question 8",
        "type": "Strongly disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": 0,
        "percentage_end": 0
        },
        {
        "question": "Question 8",
        "type": "Disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": 0,
        "percentage_end": 0
        },
        {
        "question": "Question 8",
        "type": "Neither agree nor disagree",
        "value": 0,
        "percentage": 0,
        "percentage_start": 0,
        "percentage_end": 0
        },
        {
        "question": "Question 8",
        "type": "Agree",
        "value": 0,
        "percentage": 0,
        "percentage_start": 0,
        "percentage_end": 0
        },
        {
        "question": "Question 8",
        "type": "Strongly agree",
        "value": 2,
        "percentage": 100,
        "percentage_start": 0,
        "percentage_end": 100
        }
])

color_scale = alt.Scale(
    domain=[
        "Strongly disagree",
        "Disagree",
        "Neither agree nor disagree",
        "Agree",
        "Strongly agree"
    ],
    range=["#c30d24", "#f3a583", "#cccccc", "#94c6da", "#1770ab"]
)

y_axis = alt.Axis(
    title='Question',
    offset=5,
    ticks=False,
    minExtent=60,
    domain=False
)

chart = alt.Chart(source).mark_bar().encode(
    x='percentage_start:Q',
    x2='percentage_end:Q',
    y=alt.Y('question:N', axis=y_axis),
    color=alt.Color(
        'type:N',
        legend=alt.Legend( title='Response'),
        scale=color_scale,
    )
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Grouped Bar Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.barley()

chart = alt.Chart(source).mark_bar().encode(
    x='year:O',
    y='sum(yield):Q',
    color='year:N',
    column='site:N'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Grouped Bar Chart With Error Bars
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.barley()

bars = alt.Chart().mark_bar().encode(
    x='year:O',
    y=alt.Y('mean(yield):Q', title='Mean Yield'),
    color='year:N',
)

error_bars = alt.Chart().mark_errorbar(extent='ci').encode(
    x='year:O',
    y='yield:Q'
)

chart = alt.layer(bars, error_bars, data=source).facet(
    column='site:N'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart Horizontal
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.wheat()

chart = alt.Chart(source).mark_bar().encode(
    x='wheat:Q',
    y="year:O"
).properties(height=700)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Grouped Bar Chart Horizontal
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.barley()

chart = alt.Chart(source).mark_bar().encode(
    x='sum(yield):Q',
    y='year:O',
    color='year:N',
    row='site:N'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Horizontal Stacked Bar Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.barley()

chart = alt.Chart(source).mark_bar().encode(
    x='sum(yield)',
    y='variety',
    color='site'
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Layered Bar Chart
<pre><code class="language-python">
import streamlit as st
import altair as alt
from vega_datasets import data

source = data.iowa_electricity()

chart = alt.Chart(source).mark_bar(opacity=0.7).encode(
    x='year:O',
    y=alt.Y('net_generation:Q', stack=None),
    color="source",
)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Normalized Stacked Bar Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source).mark_bar().encode(
        x=alt.X('sum(yield)', stack="normalize"),
        y='variety',
        color='site'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart Sorted
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source).mark_bar().encode(
        x='sum(yield):Q',
        y=alt.Y('site:N', sort='-x')
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Stacked Bar Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source).mark_bar().encode(
        x='variety',
        y='sum(yield)',
        color='site'
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Stacked Bar Chart Sorted Segments
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source).mark_bar().encode(
        x='sum(yield)',
        y='variety',
        color='site',
        order=alt.Order(
          # Sort the segments of the bars by this field
          'site',
          sort='ascending'
        )
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Stacked Bar Chart With Text
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source=data.barley()

    bars = alt.Chart(source).mark_bar().encode(
        x=alt.X('sum(yield):Q', stack='zero'),
        y=alt.Y('variety:N'),
        color=alt.Color('site')
    )

    text = alt.Chart(source).mark_text(dx=-15, dy=3, color='white').encode(
        x=alt.X('sum(yield):Q', stack='zero'),
        y=alt.Y('variety:N'),
        detail='site:N',
        text=alt.Text('sum(yield):Q', format='.1f')
    )

    chart = bars + text
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Trellis Stacked Bar Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source).mark_bar().encode(
        column='year',
        x='yield',
        y='variety',
        color='site'
    ).properties(width=220)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bump Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data
    import pandas as pd

    stocks = data.stocks()
    source = stocks.groupby([pd.Grouper(key="date", freq="6M"),"symbol"]).mean().reset_index()

    chart = alt.Chart(source).mark_line(point = True).encode(
        x = alt.X("date:O", timeUnit="yearmonth", title="date"),
        y="rank:O",
        color=alt.Color("symbol:N")
    ).transform_window(
        rank="rank()",
        sort=[alt.SortField("price", order="descending")],
        groupby=["date"]
    ).properties(
        title="Bump Chart for Stock Prices",
        width=600,
        height=150,
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Filled Step Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    chart = alt.Chart(source).mark_area(
        color="lightblue",
        interpolate='step-after',
        line=True
    ).encode(
        x='date',
        y='price'
    ).transform_filter(alt.datum.symbol == 'GOOG')
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line With Ci
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    line = alt.Chart(source).mark_line().encode(
        x='Year',
        y='mean(Miles_per_Gallon)'
    )

    band = alt.Chart(source).mark_errorband(extent='ci').encode(
        x='Year',
        y=alt.Y('Miles_per_Gallon', title='Miles/Gallon'),
    )

    chart = band + line

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line Chart With Cumsum
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.wheat()

    chart = alt.Chart(source).mark_line().transform_window(
        # Sort the data chronologically
        sort=[{'field': 'year'}],
        # Include all previous records before the current record and none after
        # (This is the default value so you could skip it and it would still work.)
        frame=[None, 0],
        # What to add up as you go
        cumulative_wheat='sum(wheat)'
    ).encode(
        x='year:O',
        # Plot the calculated field created by the transformation
        y='cumulative_wheat:Q'
    ).properties(width=600)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Layer Line Color Rule
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    base = alt.Chart(source).properties(width=550)

    line = base.mark_line().encode(
        x='date',
        y='price',
        color='symbol'
    )

    rule = base.mark_rule().encode(
        y='average(price)',
        color='symbol',
        size=alt.value(2)
    )

    chart = line + rule

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line With Log Scale
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.population()

    chart = alt.Chart(source).mark_line().encode(
        x='year:O',
        y=alt.Y(
            'sum(people)',
            scale=alt.Scale(type="log")  # Here the scale is applied
        )
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line Percent
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.jobs.url

    chart = alt.Chart(source).mark_line().encode(
        alt.X('year:O'),
        alt.Y('perc:Q', axis=alt.Axis(format='%')),
        color='sex:N'
    ).transform_filter(
        alt.datum.job == 'Welder'
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line Chart With Points
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import numpy as np
    import pandas as pd

    x = np.arange(100)
    source = pd.DataFrame({
      'x': x,
      'f(x)': np.sin(x / 5)
    })

    chart = alt.Chart(source).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x='x',
        y='f(x)'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line Chart With Generator
<pre><code class="language-python">
import streamlit as st
    import altair as alt

    source = alt.sequence(start=0, stop=12.7, step=0.1, as_='x')

    chart = alt.Chart(source).mark_line().transform_calculate(
        sin='sin(datum.x)',
        cos='cos(datum.x)'
    ).transform_fold(
        ['sin', 'cos']
    ).encode(
        x='x:Q',
        y='value:Q',
        color='key:N'
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Trail Marker
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.wheat()

    chart = alt.Chart(source).mark_trail().encode(
        x='year:T',
        y='wheat:Q',
        size='wheat:Q'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line Chart With Datum
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    lines = (
        alt.Chart(source)
        .mark_line()
        .encode(x="date", y="price", color="symbol")
    )

    xrule = (
        alt.Chart()
        .mark_rule(color="cyan", strokeWidth=2)
        .encode(x=alt.datum(alt.DateTime(year=2006, month="November")))
    )

    yrule = (
        alt.Chart().mark_rule(strokeDash=[12, 6], size=2).encode(y=alt.datum(350))
    )chart = lines + yrule + xrule
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Line Chart With Color Datum
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies()

    chart = alt.Chart(source).mark_line().encode(
        x=alt.X("IMDB_Rating", bin=True),
        y=alt.Y(
            alt.repeat("layer"), aggregate="mean", title="Mean of US and Worldwide Gross"
        ),
        color=alt.datum(alt.repeat("layer")),
    ).repeat(layer=["US_Gross", "Worldwide_Gross"])

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Multi Series Line
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    chart = alt.Chart(source).mark_line().encode(
        x='date',
        y='price',
        color='symbol',
        strokeDash='symbol',
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Slope Graph
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source).mark_line().encode(
        x='year:O',
        y='median(yield)',
        color='site'
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Step Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    chart = alt.Chart(source).mark_line(interpolate='step-after').encode(
        x='date',
        y='price'
    ).transform_filter(
        alt.datum.symbol == 'GOOG'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Area Chart Gradient
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    chart = alt.Chart(source).transform_filter(
        'datum.symbol==="GOOG"'
    ).mark_area(
        line={'color':'darkgreen'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0),
                   alt.GradientStop(color='darkgreen', offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0
        )
    ).encode(
        alt.X('date:T'),
        alt.Y('price:Q')
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Cumulative Count Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    chart = alt.Chart(source).transform_window(
        cumulative_count="count()",
        sort=[{"field": "IMDB_Rating"}],
    ).mark_area().encode(
        x="IMDB_Rating:Q",
        y="cumulative_count:Q"
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Density Facet
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iris()

    chart = alt.Chart(source).transform_fold(
        ['petalWidth',
         'petalLength',
         'sepalWidth',
         'sepalLength'],
        as_ = ['Measurement_type', 'value']
    ).transform_density(
        density='value',
        bandwidth=0.3,
        groupby=['Measurement_type'],
        extent= [0, 8]
    ).mark_area().encode(
        alt.X('value:Q'),
        alt.Y('density:Q'),
        alt.Row('Measurement_type:N')
    ).properties(width=300, height=50)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Horizon Graph
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame([
        {"x": 1,  "y": 28}, {"x": 2,  "y": 55},
        {"x": 3,  "y": 43}, {"x": 4,  "y": 91},
        {"x": 5,  "y": 81}, {"x": 6,  "y": 53},
        {"x": 7,  "y": 19}, {"x": 8,  "y": 87},
        {"x": 9,  "y": 52}, {"x": 10, "y": 48},
        {"x": 11, "y": 24}, {"x": 12, "y": 49},
        {"x": 13, "y": 87}, {"x": 14, "y": 66},
        {"x": 15, "y": 17}, {"x": 16, "y": 27},
        {"x": 17, "y": 68}, {"x": 18, "y": 16},
        {"x": 19, "y": 49}, {"x": 20, "y": 15}
    ])

    area1 = alt.Chart(source).mark_area(
        clip=True,
        interpolate='monotone'
    ).encode(
        alt.X('x', scale=alt.Scale(zero=False, nice=False)),
        alt.Y('y', scale=alt.Scale(domain=[0, 50]), title='y'),
        opacity=alt.value(0.6)
    ).properties(
        width=500,
        height=75
    )

    area2 = area1.encode(
        alt.Y('ny:Q', scale=alt.Scale(domain=[0, 50]))
    ).transform_calculate(
        "ny", alt.datum.y - 50
    )

    chart = area1 + area2

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Interval Selection
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.sp500.url

    brush = alt.selection(type='interval', encodings=['x'])

    base = alt.Chart(source).mark_area().encode(
        x = 'date:T',
        y = 'price:Q'
    ).properties(
        width=600,
        height=200
    )

    upper = base.encode(
        alt.X('date:T', scale=alt.Scale(domain=brush))
    )

    lower = base.properties(
        height=60
    ).add_selection(brush)

    chart = upper & lower

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Layered Area Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iowa_electricity()

    chart = alt.Chart(source).mark_area(opacity=0.3).encode(
        x="year:T",
        y=alt.Y("net_generation:Q", stack=None),
        color="source:N"
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Normalized Stacked Area Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iowa_electricity()

    chart = alt.Chart(source).mark_area().encode(
        x="year:T",
        y=alt.Y("net_generation:Q", stack="normalize"),
        color="source:N"
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Density Stack
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iris()

    chart = alt.Chart(source).transform_fold(
        ['petalWidth',
         'petalLength',
         'sepalWidth',
         'sepalLength'],
        as_ = ['Measurement_type', 'value']
    ).transform_density(
        density='value',
        bandwidth=0.3,
        groupby=['Measurement_type'],
        extent= [0, 8],
        counts = True,
        steps=200
    ).mark_area().encode(
        alt.X('value:Q'),
        alt.Y('density:Q', stack='zero'),
        alt.Color('Measurement_type:N')
    ).properties(width=400, height=100)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Streamgraph
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.unemployment_across_industries.url

    chart = alt.Chart(source).mark_area().encode(
        alt.X('yearmonth(date):T',
            axis=alt.Axis(format='%Y', domain=False, tickSize=0)
        ),
        alt.Y('sum(count):Q', stack='center', axis=None),
        alt.Color('series:N',
            scale=alt.Scale(scheme='category20b')
        )
    ).interactive()

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Trellis Area
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iowa_electricity()

    chart = alt.Chart(source).mark_area().encode(
        x="year:T",
        y="net_generation:Q",
        color="source:N",
        row="source:N"
    ).properties(
        height=100
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Trellis Area Sort Array
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    chart = alt.Chart(source).transform_filter(
        alt.datum.symbol != 'GOOG'
    ).mark_area().encode(
        x='date:T',
        y='price:Q',
        color='symbol:N',
        row=alt.Row('symbol:N', sort=['MSFT', 'AAPL', 'IBM', 'AMZN'])
    ).properties(height=50, width=400)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Donut Chart
<pre><code class="language-python">
import streamlit as st
    import pandas as pd
    import altair as alt

    source = pd.DataFrame({"category": [1, 2, 3, 4, 5, 6], "value": [4, 6, 10, 3, 7, 8]})

    chart = alt.Chart(source).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="category", type="nominal"),
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Pacman Chart
<pre><code class="language-python">
import streamlit as st
    import numpy as np
    import altair as alt

    chart = alt.Chart().mark_arc(color="gold").encode(
        theta=alt.datum((5 / 8) * np.pi, scale=None),
        theta2=alt.datum((19 / 8) * np.pi),
        radius=alt.datum(100, scale=None),
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Pie Chart
<pre><code class="language-python">
import streamlit as st
    import pandas as pd
    import altair as alt

    source = pd.DataFrame({"category": [1, 2, 3, 4, 5, 6], "value": [4, 6, 10, 3, 7, 8]})

    chart = alt.Chart(source).mark_arc().encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="category", type="nominal"),
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Pie Chart With Labels
<pre><code class="language-python">
import streamlit as st
    import pandas as pd
    import altair as alt

    source = pd.DataFrame(
        {"category": ["a", "b", "c", "d", "e", "f"], "value": [4, 6, 10, 3, 7, 8]}
    )

    base = alt.Chart(source).encode(
        theta=alt.Theta("value:Q", stack=True), color=alt.Color("category:N", legend=None)
    )

    pie = base.mark_arc(outerRadius=120)
    text = base.mark_text(radius=140, size=20).encode(text="category:N")

    chart = pie + text
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Radial Chart
<pre><code class="language-python">
import streamlit as st
    import pandas as pd
    import altair as alt

    source = pd.DataFrame({"values": [12, 23, 47, 6, 52, 19]})

    base = alt.Chart(source).encode(
        theta=alt.Theta("values:Q", stack=True),
        radius=alt.Radius("values", scale=alt.Scale(type="sqrt", zero=True, rangeMin=20)),
        color="values:N",
    )

    c1 = base.mark_arc(innerRadius=20, stroke="#fff")

    c2 = base.mark_text(radiusOffset=10).encode(text="values:Q")

    chart = c1 + c2

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Binned Scatterplot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    chart = alt.Chart(source).mark_circle().encode(
        alt.X('IMDB_Rating:Q', bin=True),
        alt.Y('Rotten_Tomatoes_Rating:Q', bin=True),
        size='count()'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Linked Table
<pre><code class="language-python">
import streamlit as st

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bubble Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    chart = alt.Chart(source).mark_point().encode(
        x='Horsepower',
        y='Miles_per_Gallon',
        size='Acceleration'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Connected Scatterplot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.driving()

    chart = alt.Chart(source).mark_line(point=True).encode(
        alt.X('miles', scale=alt.Scale(zero=False)),
        alt.Y('gas', scale=alt.Scale(zero=False)),
        order='year'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Dot Dash Plot
<pre><code class="language-python">
import streamlit as st

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Multifeature Scatter Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iris()

    chart = alt.Chart(source).mark_circle().encode(
        alt.X('sepalLength', scale=alt.Scale(zero=False)),
        alt.Y('sepalWidth', scale=alt.Scale(zero=False, padding=1)),
        color='species',
        size='petalWidth'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Poly Fit Regression
<pre><code class="language-python">
import streamlit as st
    import numpy as np
    import pandas as pd
    import altair as alt

    # Generate some random data
    rng = np.random.RandomState(1)
    x = rng.rand(40) ** 2
    y = 10 - 1.0 / (x + 0.1) + rng.randn(40)
    source = pd.DataFrame({"x": x, "y": y})

    # Define the degree of the polynomial fits
    degree_list = [1, 3, 5]

    base = alt.Chart(source).mark_circle(color="black").encode(
            alt.X("x"), alt.Y("y")
    )

    polynomial_fit = [
        base.transform_regression(
            "x", "y", method="poly", order=order, as_=["x", str(order)]
        )
        .mark_line()
        .transform_fold([str(order)], as_=["degree", "y"])
        .encode(alt.Color("degree:N"))
        for order in degree_list
    ]

    chart = alt.layer(base, *polynomial_fit)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Qq
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.normal_2d.url

    base = alt.Chart(source).transform_quantile(
        'u',
        step=0.01,
        as_ = ['p', 'v']
    ).transform_calculate(
        uniform = 'quantileUniform(datum.p)',
        normal = 'quantileNormal(datum.p)'
    ).mark_point().encode(
        alt.Y('v:Q')
    )

    chart = base.encode(x='uniform:Q') | base.encode(x='normal:Q')

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Matrix
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    chart = alt.Chart(source).mark_circle().encode(
        alt.X(alt.repeat("column"), type='quantitative'),
        alt.Y(alt.repeat("row"), type='quantitative'),
        color='Origin:N'
    ).properties(
        width=150,
        height=150
    ).repeat(
        row=['Horsepower', 'Acceleration', 'Miles_per_Gallon'],
        column=['Miles_per_Gallon', 'Acceleration', 'Horsepower']
    ).interactive()
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Href
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    chart = alt.Chart(source).transform_calculate(
        url='https://www.google.com/search?q=' + alt.datum.Name
    ).mark_point().encode(
        x='Horsepower:Q',
        y='Miles_per_Gallon:Q',
        color='Origin:N',
        href='url:N',
        tooltip=['Name:N', 'url:N']
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter With Loess
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    import numpy as np

    np.random.seed(1)

    source = pd.DataFrame({
        'x': np.arange(100),
        'A': np.random.randn(100).cumsum(),
        'B': np.random.randn(100).cumsum(),
        'C': np.random.randn(100).cumsum(),
    })

    base = alt.Chart(source).mark_circle(opacity=0.5).transform_fold(
        fold=['A', 'B', 'C'],
        as_=['category', 'y']
    ).encode(
        alt.X('x:Q'),
        alt.Y('y:Q'),
        alt.Color('category:N')
    )

    chart = base + base.transform_loess('x', 'y', groupby=['category']).mark_line(size=4)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter With Minimap
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather()

    zoom = alt.selection_interval(encodings=["x", "y"])

    minimap = (
        alt.Chart(source)
        .mark_point()
        .add_selection(zoom)
        .encode(
            x="date:T",
            y="temp_max:Q",
            color=alt.condition(zoom, "weather", alt.value("lightgray")),
        )
        .properties(
            width=200,
            height=200,
            title="Minimap -- click and drag to zoom in the detail view",
        )
    )

    detail = (
        alt.Chart(source)
        .mark_point()
        .encode(
            x=alt.X(
                "date:T", scale=alt.Scale(domain={"selection": zoom.name, "encoding": "x"})
            ),
            y=alt.Y(
                "temp_max:Q",
                scale=alt.Scale(domain={"selection": zoom.name, "encoding": "y"}),
            ),
            color="weather",
        )
        .properties(width=600, height=400, title="Seattle weather -- detail view")
    )

    chart = detail | minimap
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter With Rolling Mean
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather()

    line = alt.Chart(source).mark_line(
        color='red',
        size=3
    ).transform_window(
        rolling_mean='mean(temp_max)',
        frame=[-15, 15]
    ).encode(
        x='date:T',
        y='rolling_mean:Q'
    )

    points = alt.Chart(source).mark_point().encode(
        x='date:T',
        y=alt.Y('temp_max:Q',
                axis=alt.Axis(title='Max Temp'))
    )

    chart = points + line
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Simple Scatter With Errorbars
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    import numpy as np

    # generate some data points with uncertainties
    np.random.seed(0)
    x = [1, 2, 3, 4, 5]
    y = np.random.normal(10, 0.5, size=len(x))
    yerr = 0.2

    # set up data frame
    source = pd.DataFrame({"x": x, "y": y, "yerr": yerr})

    # the base chart
    base = alt.Chart(source).transform_calculate(
        ymin="datum.y-datum.yerr",
        ymax="datum.y+datum.yerr"
    )

    # generate the points
    points = base.mark_point(
        filled=True,
        size=50,
        color='black'
    ).encode(
        x=alt.X('x', scale=alt.Scale(domain=(0, 6))),
        y=alt.Y('y', scale=alt.Scale(zero=False))
    )

    # generate the error bars
    errorbars = base.mark_errorbar().encode(
        x="x",
        y="ymin:Q",
        y2="ymax:Q"
    )

    chart = points + errorbars
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter With Labels
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame({
        'x': [1, 3, 5, 7, 9],
        'y': [1, 3, 5, 7, 9],
        'label': ['A', 'B', 'C', 'D', 'E']
    })

    points = alt.Chart(source).mark_point().encode(
        x='x:Q',
        y='y:Q'
    )

    text = points.mark_text(
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        text='label'
    )

    chart = points + text
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Stripplot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    stripplot =  alt.Chart(source, width=40).mark_circle(size=8).encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False),
            scale=alt.Scale(),
        ),
        y=alt.Y('IMDB_Rating:Q'),
        color=alt.Color('Major_Genre:N', legend=None),
        column=alt.Column(
            'Major_Genre:N',
            header=alt.Header(
                labelAngle=-90,
                titleOrient='top',
                labelOrient='bottom',
                labelAlign='right',
                labelPadding=3,
            ),
        ),
    ).transform_calculate(
        # Generate Gaussian jitter with a Box-Muller transform
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    )

    chart = stripplot
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Table Bubble Plot Github
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.github.url

    chart = alt.Chart(source).mark_circle().encode(
        x='hours(time):O',
        y='day(time):O',
        size='sum(count):Q'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Trellis Scatter Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    chart = alt.Chart(source).mark_point().encode(
        x='Horsepower:Q',
        y='Miles_per_Gallon:Q',
        row='Origin:N'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Wind Vector Map
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.windvectors()

    chart = alt.Chart(source).mark_point(shape="wedge", filled=True).encode(
        latitude="latitude",
        longitude="longitude",
        color=alt.Color(
            "dir", scale=alt.Scale(domain=[0, 360], scheme="rainbow"), legend=None
        ),
        angle=alt.Angle("dir", scale=alt.Scale(domain=[0, 360], range=[180, 540])),
        size=alt.Size("speed", scale=alt.Scale(rangeMax=500)),
    ).project("equalEarth")

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Histogram Responsive
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.flights_5k.url

    brush = alt.selection_interval(encodings=['x'])

    base = alt.Chart(source).transform_calculate(
        time="hours(datum.date) + minutes(datum.date) / 60"
    ).mark_bar().encode(
        y='count():Q'
    ).properties(
        width=600,
        height=100
    )

    chart = alt.vconcat(
      base.encode(
        alt.X('time:Q',
          bin=alt.Bin(maxbins=30, extent=brush),
          scale=alt.Scale(domain=brush)
        )
      ),
      base.encode(
        alt.X('time:Q', bin=alt.Bin(maxbins=30)),
      ).add_selection(brush)
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Histogram With A Global Mean Overlay
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    base = alt.Chart(source)

    bar = base.mark_bar().encode(
        x=alt.X('IMDB_Rating:Q', bin=True, axis=None),
        y='count()'
    )

    rule = base.mark_rule(color='red').encode(
        x='mean(IMDB_Rating):Q',
        size=alt.value(5)
    )

    chart = bar + rule
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Layered Histogram
<pre><code class="language-python">
import streamlit as st
    import pandas as pd
    import altair as alt
    import numpy as np
    np.random.seed(42)

    # Generating Data
    source = pd.DataFrame({
        'Trial A': np.random.normal(0, 0.8, 1000),
        'Trial B': np.random.normal(-2, 1, 1000),
        'Trial C': np.random.normal(3, 2, 1000)
    })

    chart = alt.Chart(source).transform_fold(
        ['Trial A', 'Trial B', 'Trial C'],
        as_=['Experiment', 'Measurement']
    ).mark_bar(
        opacity=0.3,
        binSpacing=0
    ).encode(
        alt.X('Measurement:Q', bin=alt.Bin(maxbins=100)),
        alt.Y('count()', stack=None),
        alt.Color('Experiment:N')
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Trellis Histogram
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    chart = alt.Chart(source).mark_bar().encode(
        alt.X("Horsepower:Q", bin=True),
        y='count()',
        row='Origin'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Choropleth
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    counties = alt.topo_feature(data.us_10m.url, 'counties')
    source = data.unemployment.url

    chart = alt.Chart(counties).mark_geoshape().encode(
        color='rate:Q'
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(source, 'id', ['rate'])
    ).project(
        type='albersUsa'
    ).properties(
        width=500,
        height=300
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Airports Count
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    airports = data.airports.url
    states = alt.topo_feature(data.us_10m.url, feature='states')

    # US states background
    background = alt.Chart(states).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=500,
        height=300
    ).project('albersUsa')

    # airport positions on background
    points = alt.Chart(airports).transform_aggregate(
        latitude='mean(latitude)',
        longitude='mean(longitude)',
        count='count()',
        groupby=['state']
    ).mark_circle().encode(
        longitude='longitude:Q',
        latitude='latitude:Q',
        size=alt.Size('count:Q', title='Number of Airports'),
        color=alt.value('steelblue'),
        tooltip=['state:N','count:Q']
    ).properties(
        title='Number of airports in US'
    )

    chart = background + points

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Choropleth Repeat
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    states = alt.topo_feature(data.us_10m.url, 'states')
    source = data.population_engineers_hurricanes.url
    variable_list = ['population', 'engineers', 'hurricanes']

    chart = alt.Chart(states).mark_geoshape().encode(
        alt.Color(alt.repeat('row'), type='quantitative')
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(source, 'id', variable_list)
    ).properties(
        width=500,
        height=300
    ).project(
        type='albersUsa'
    ).repeat(
        row=variable_list
    ).resolve_scale(
        color='independent'
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Us Incomebrackets By State Facet
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    states = alt.topo_feature(data.us_10m.url, 'states')
    source = data.income.url

    chart = alt.Chart(source).mark_geoshape().encode(
        shape='geo:G',
        color='pct:Q',
        tooltip=['name:N', 'pct:Q'],
        facet=alt.Facet('group:N', columns=2),
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(data=states, key='id'),
        as_='geo'
    ).properties(
        width=300,
        height=175,
    ).project(
        type='albersUsa'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## World Map
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = alt.topo_feature(data.world_110m.url, 'countries')

    base = alt.Chart(source).mark_geoshape(
        fill='#666666',
        stroke='white'
    ).properties(
        width=300,
        height=180
    )

    projections = ['equirectangular', 'mercator', 'orthographic', 'gnomonic']
    charts = [base.project(proj).properties(title=proj)
              for proj in projections]

    chart = alt.concat(*charts, columns=2)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## World Projections
<pre><code class="language-python">
import streamlit as st

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Selection Layer Bar Month
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather()
    brush = alt.selection(type='interval', encodings=['x'])

    bars = alt.Chart().mark_bar().encode(
        x='month(date):O',
        y='mean(precipitation):Q',
        opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7)),
    ).add_selection(
        brush
    )

    line = alt.Chart().mark_rule(color='firebrick').encode(
        y='mean(precipitation):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )

    chart = alt.layer(bars, line, data=source)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Interactive Cross Highlight
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    pts = alt.selection(type="single", encodings=['x'])

    rect = alt.Chart(data.movies.url).mark_rect().encode(
        alt.X('IMDB_Rating:Q', bin=True),
        alt.Y('Rotten_Tomatoes_Rating:Q', bin=True),
        alt.Color('count()',
            scale=alt.Scale(scheme='greenblue'),
            legend=alt.Legend(title='Total Records')
        )
    )

    circ = rect.mark_point().encode(
        alt.ColorValue('grey'),
        alt.Size('count()',
            legend=alt.Legend(title='Records in Selection')
        )
    ).transform_filter(
        pts
    )

    bar = alt.Chart(source).mark_bar().encode(
        x='Major_Genre:N',
        y='count()',
        color=alt.condition(pts, alt.ColorValue("steelblue"), alt.ColorValue("grey"))
    ).properties(
        width=550,
        height=200
    ).add_selection(pts)

    chart = alt.vconcat(
        rect + circ,
        bar
    ).resolve_legend(
        color="independent",
        size="independent"
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Interactive Layered Crossfilter
<pre><code class="language-python">
import streamlit as st

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Interactive Legend
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.unemployment_across_industries.url

    selection = alt.selection_multi(fields=['series'], bind='legend')

    chart = alt.Chart(source).mark_area().encode(
        alt.X('yearmonth(date):T', axis=alt.Axis(domain=False, format='%Y', tickSize=0)),
        alt.Y('sum(count):Q', stack='center', axis=None),
        alt.Color('series:N', scale=alt.Scale(scheme='category20b')),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        selection
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Interactive Brush
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()
    brush = alt.selection(type='interval')

    chart = alt.Chart(source).mark_point().encode(
        x='Horsepower:Q',
        y='Miles_per_Gallon:Q',
        color=alt.condition(brush, 'Cylinders:O', alt.value('grey')),
    ).add_selection(brush)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter With Layered Histogram
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    import numpy as np

    # generate fake data
    source = pd.DataFrame({'gender': ['M']*1000 + ['F']*1000,
                   'height':np.concatenate((np.random.normal(69, 7, 1000),
                                           np.random.normal(64, 6, 1000))),
                   'weight': np.concatenate((np.random.normal(195.8, 144, 1000),
                                            np.random.normal(167, 100, 1000))),
                   'age': np.concatenate((np.random.normal(45, 8, 1000),
                                            np.random.normal(51, 6, 1000)))
            })

    selector = alt.selection_single(empty='all', fields=['gender'])

    color_scale = alt.Scale(domain=['M', 'F'],
                            range=['#1FC3AA', '#8624F5'])

    base = alt.Chart(source).properties(
        width=250,
        height=250
    ).add_selection(selector)

    points = base.mark_point(filled=True, size=200).encode(
        x=alt.X('mean(height):Q',
                scale=alt.Scale(domain=[0,84])),
        y=alt.Y('mean(weight):Q',
                scale=alt.Scale(domain=[0,250])),
        color=alt.condition(selector,
                            'gender:N',
                            alt.value('lightgray'),
                            scale=color_scale),
    )

    hists = base.mark_bar(opacity=0.5, thickness=100).encode(
        x=alt.X('age',
                bin=alt.Bin(step=5), # step keeps bin size the same
                scale=alt.Scale(domain=[0,100])),
        y=alt.Y('count()',
                stack=None,
                scale=alt.Scale(domain=[0,350])),
        color=alt.Color('gender:N',
                        scale=color_scale)
    ).transform_filter(
        selector
    )chart = points | hists

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Multiline Highlight
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    highlight = alt.selection(type='single', on='mouseover',
                              fields=['symbol'], nearest=True)

    base = alt.Chart(source).encode(
        x='date:T',
        y='price:Q',
        color='symbol:N'
    )

    points = base.mark_circle().encode(
        opacity=alt.value(0)
    ).add_selection(
        highlight
    ).properties(
        width=600
    )

    lines = base.mark_line().encode(
        size=alt.condition(~highlight, alt.value(1), alt.value(3))
    )

    chart = points + lines

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Multiline Tooltip
<pre><code class="language-python">
import streamlit as st

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Linked Brush
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    brush = alt.selection(type='interval', resolve='global')

    base = alt.Chart(source).mark_point().encode(
        y='Miles_per_Gallon',
        color=alt.condition(brush, 'Origin', alt.ColorValue('gray')),
    ).add_selection(
        brush
    ).properties(
        width=250,
        height=250
    )

    chart = base.encode(x='Horsepower') | base.encode(x='Acceleration')
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Multiple Interactions
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    movies = alt.UrlData(
        data.movies.url,
        format=alt.DataFormat(parse={"Release_Date":"date"})
    )
    ratings = ['G', 'NC-17', 'PG', 'PG-13', 'R']
    genres = ['Action', 'Adventure', 'Black Comedy', 'Comedy',
           'Concert/Performance', 'Documentary', 'Drama', 'Horror', 'Musical',
           'Romantic Comedy', 'Thriller/Suspense', 'Western']

    base = alt.Chart(movies, width=200, height=200).mark_point(filled=True).transform_calculate(
        Rounded_IMDB_Rating = "floor(datum.IMDB_Rating)",
        Hundred_Million_Production =  "datum.Production_Budget > 100000000.0 ? 100 : 10",
        Release_Year = "year(datum.Release_Date)"
    ).transform_filter(
        alt.datum.IMDB_Rating > 0
    ).transform_filter(
        alt.FieldOneOfPredicate(field='MPAA_Rating', oneOf=ratings)
    ).encode(
        x=alt.X('Worldwide_Gross:Q', scale=alt.Scale(domain=(100000,10**9), clamp=True)),
        y='IMDB_Rating:Q',
        tooltip="Title:N"
    )

    # A slider filter
    year_slider = alt.binding_range(min=1969, max=2018, step=1)
    slider_selection = alt.selection_single(bind=year_slider, fields=['Release_Year'], name="Release Year_")filter_year = base.add_selection(
        slider_selection
    ).transform_filter(
        slider_selection
    ).properties(title="Slider Filtering")

    # A dropdown filter
    genre_dropdown = alt.binding_select(options=genres)
    genre_select = alt.selection_single(fields=['Major_Genre'], bind=genre_dropdown, name="Genre")

    filter_genres = base.add_selection(
        genre_select
    ).transform_filter(
        genre_select
    ).properties(title="Dropdown Filtering")

    #color changing marks
    rating_radio = alt.binding_radio(options=ratings)

    rating_select = alt.selection_single(fields=['MPAA_Rating'], bind=rating_radio, name="Rating")
    rating_color_condition = alt.condition(rating_select,
                          alt.Color('MPAA_Rating:N', legend=None),
                          alt.value('lightgray'))

    highlight_ratings = base.add_selection(
        rating_select
    ).encode(
        color=rating_color_condition
    ).properties(title="Radio Button Highlighting")

    # Boolean selection for format changes
    input_checkbox = alt.binding_checkbox()
    checkbox_selection = alt.selection_single(bind=input_checkbox, name="Big Budget Films")

    size_checkbox_condition = alt.condition(checkbox_selection,
                                            alt.SizeValue(25),
                                            alt.Size('Hundred_Million_Production:Q')
                                           )

    budget_sizing = base.add_selection(
        checkbox_selection
    ).encode(
        size=size_checkbox_condition
    ).properties(title="Checkbox Formatting")

    chart = ( filter_year | filter_genres) &  (highlight_ratings | budget_sizing  )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Select Detail
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    import numpy as np

    np.random.seed(0)

    n_objects = 20
    n_times = 50

    # Create one (x, y) pair of metadata per object
    locations = pd.DataFrame({
        'id': range(n_objects),
        'x': np.random.randn(n_objects),
        'y': np.random.randn(n_objects)
    })

    # Create a 50-element time-series for each object
    timeseries = pd.DataFrame(np.random.randn(n_times, n_objects).cumsum(0),
                              columns=locations['id'],
                              index=pd.RangeIndex(0, n_times, name='time'))

    # Melt the wide-form timeseries into a long-form view
    timeseries = timeseries.reset_index().melt('time')

    # Merge the (x, y) metadata into the long-form view
    timeseries['id'] = timeseries['id'].astype(int)  # make merge not complain
    data = pd.merge(timeseries, locations, on='id')

    # Data is prepared, now make a chart

    selector = alt.selection_single(empty='all', fields=['id'])

    base = alt.Chart(data).properties(
        width=250,
        height=250
    ).add_selection(selector)

    points = base.mark_point(filled=True, size=200).encode(
        x='mean(x)',
        y='mean(y)',
        color=alt.condition(selector, 'id:O', alt.value('lightgray'), legend=None),
    )

    timeseries = base.mark_line().encode(
        x='time',
        y=alt.Y('value', scale=alt.Scale(domain=(-15, 15))),
        color=alt.Color('id:O', legend=None)
    ).transform_filter(
        selector
    )

    chart = points | timeseries

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>


## Selection Histogram
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    brush = alt.selection(type='interval')

    points = alt.Chart(source).mark_point().encode(
        x='Horsepower:Q',
        y='Miles_per_Gallon:Q',
        color=alt.condition(brush, 'Origin:N', alt.value('lightgray'))
    ).add_selection(
        brush
    )

    bars = alt.Chart(source).mark_bar().encode(
        y='Origin:N',
        color='Origin:N',
        x='count(Origin):Q'
    ).transform_filter(
        brush
    )

    chart = points & bars

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Interactive Scatter Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.cars()

    chart = alt.Chart(source).mark_circle().encode(
        x='Horsepower',
        y='Miles_per_Gallon',
        color='Origin',
    ).interactive()
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Select Mark Area
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.unemployment_across_industries.url

    base = alt.Chart(source).mark_area(
        color='goldenrod',
        opacity=0.3
    ).encode(
        x='yearmonth(date):T',
        y='sum(count):Q',
    )

    brush = alt.selection_interval(encodings=['x'],empty='all')
    background = base.add_selection(brush)
    selected = base.transform_filter(brush).mark_area(color='goldenrod')

    chart = background + selected
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Anscombe Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.anscombe()

    chart = alt.Chart(source).mark_circle().encode(
        alt.X('X', scale=alt.Scale(zero=False)),
        alt.Y('Y', scale=alt.Scale(zero=False)),
        alt.Facet('Series', columns=2),
    ).properties(
        width=180,
        height=180,
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Co2 Concentration
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.co2_concentration.url

    base = alt.Chart(
        source,
        title="Carbon Dioxide in the Atmosphere"
    ).transform_calculate(
        year="year(datum.Date)"
    ).transform_calculate(
        decade="floor(datum.year / 10)"
    ).transform_calculate(
        scaled_date="(datum.year % 10) + (month(datum.Date)/12)"
    ).transform_window(
        first_date='first_value(scaled_date)',
        last_date='last_value(scaled_date)',
        sort=[{"field": "scaled_date", "order": "ascending"}],
        groupby=['decade'],
        frame=[None, None]
    ).transform_calculate(
      end="datum.first_date === datum.scaled_date ? 'first' : datum.last_date === datum.scaled_date ? 'last' : null"
    ).encode(
        x=alt.X(
            "scaled_date:Q",
            axis=alt.Axis(title="Year into Decade", tickCount=11)
        ),
        y=alt.Y(
            "CO2:Q",
            title="CO2 concentration in ppm",
            scale=alt.Scale(zero=False)
        )
    )

    line = base.mark_line().encode(
        color=alt.Color(
            "decade:O",
            scale=alt.Scale(scheme="magma"),
            legend=None
        )
    )

    text = base.encode(text="year:N")

    start_year = text.transform_filter(
      alt.datum.end == 'first'
    ).mark_text(baseline="top")

    end_year = text.transform_filter(
      alt.datum.end == 'last'
    ).mark_text(baseline="bottom")

    chart = (line + start_year + end_year).configure_text(
        align="left",
        dx=1,
        dy=3
    ).properties(width=600, height=375)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Beckers Barley Trellis Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    chart = alt.Chart(source, title="The Morris Mistake").mark_point().encode(
        alt.X(
            'yield:Q',
            title="Barley Yield (bushels/acre)",
            scale=alt.Scale(zero=False),
            axis=alt.Axis(grid=False)
        ),
        alt.Y(
            'variety:N',
            title="",
            sort='-x',
            axis=alt.Axis(grid=True)
        ),
        color=alt.Color('year:N', legend=alt.Legend(title="Year")),
        row=alt.Row(
            'site:N',
            title="",
            sort=alt.EncodingSortField(field='yield', op='sum', order='descending'),
        )
    ).properties(
        height=alt.Step(20)
    ).configure_view(stroke="transparent")

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Airport Connections
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    # Since these data are each more than 5,000 rows we'll import from the URLs
    airports = data.airports.url
    flights_airport = data.flights_airport.url

    states = alt.topo_feature(data.us_10m.url, feature="states")

    # Create mouseover selection
    select_city = alt.selection_single(
        on="mouseover", nearest=True, fields=["origin"], empty="none"
    )

    # Define which attributes to lookup from airports.csv
    lookup_data = alt.LookupData(
        airports, key="iata", fields=["state", "latitude", "longitude"]
    )

    background = alt.Chart(states).mark_geoshape(
        fill="lightgray",
        stroke="white"
    ).properties(
        width=750,
        height=500
    ).project("albersUsa")

    connections = alt.Chart(flights_airport).mark_rule(opacity=0.35).encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        latitude2="lat2:Q",
        longitude2="lon2:Q"
    ).transform_lookup(
        lookup="origin",
        from_=lookup_data
    ).transform_lookup(
        lookup="destination",
        from_=lookup_data,
        as_=["state", "lat2", "lon2"]
    ).transform_filter(
        select_city
    )

    points = alt.Chart(flights_airport).mark_circle().encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        size=alt.Size("routes:Q", scale=alt.Scale(range=[0, 1000]), legend=None),
        order=alt.Order("routes:Q", sort="descending"),
        tooltip=["origin:N", "routes:Q"]
    ).transform_aggregate(
        routes="count()",
        groupby=["origin"]
    ).transform_lookup(
        lookup="origin",
        from_=lookup_data
    ).transform_filter(
        (alt.datum.state != "PR") & (alt.datum.state != "VI")
    ).add_selection(
        select_city
    )

    chart = (background + connections + points).configure_view(stroke=None)
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Cumulative Wiki Donations
<pre><code class="language-python">
import streamlit as st
    import altair as alt

    source = "https://frdata.wikimedia.org/donationdata-vs-day.csv"

    chart = alt.Chart(source).mark_line().encode(
        alt.X('monthdate(date):T', title='Month', axis=alt.Axis(format='%B')),
        alt.Y('max(ytdsum):Q', title='Cumulative Donations', stack=None),
        alt.Color('year(date):O', legend=alt.Legend(title='Year')),
        alt.Order('year(data):O')
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Falkensee
<pre><code class="language-python">
import streamlit as st
    import altair as alt

    source = [
          {"year": "1875", "population": 1309},
          {"year": "1890", "population": 1558},
          {"year": "1910", "population": 4512},
          {"year": "1925", "population": 8180},
          {"year": "1933", "population": 15915},
          {"year": "1939", "population": 24824},
          {"year": "1946", "population": 28275},
          {"year": "1950", "population": 29189},
          {"year": "1964", "population": 29881},
          {"year": "1971", "population": 26007},
          {"year": "1981", "population": 24029},
          {"year": "1985", "population": 23340},
          {"year": "1989", "population": 22307},
          {"year": "1990", "population": 22087},
          {"year": "1991", "population": 22139},
          {"year": "1992", "population": 22105},
          {"year": "1993", "population": 22242},
          {"year": "1994", "population": 22801},
          {"year": "1995", "population": 24273},
          {"year": "1996", "population": 25640},
          {"year": "1997", "population": 27393},
          {"year": "1998", "population": 29505},
          {"year": "1999", "population": 32124},
          {"year": "2000", "population": 33791},
          {"year": "2001", "population": 35297},
          {"year": "2002", "population": 36179},
          {"year": "2003", "population": 36829},
          {"year": "2004", "population": 37493},
          {"year": "2005", "population": 38376},
          {"year": "2006", "population": 39008},
          {"year": "2007", "population": 39366},
          {"year": "2008", "population": 39821},
          {"year": "2009", "population": 40179},
          {"year": "2010", "population": 40511},
          {"year": "2011", "population": 40465},
          {"year": "2012", "population": 40905},
          {"year": "2013", "population": 41258},
          {"year": "2014", "population": 41777}
        ]

    source2 = [{
                "start": "1933",
                "end": "1945",
                "event": "Nazi Rule"
              },
              {
                "start": "1948",
                "end": "1989",
                "event": "GDR (East Germany)"
              }]source = alt.pd.DataFrame(source)
    source2 = alt.pd.DataFrame(source2)line = alt.Chart(source).mark_line(color='#333').encode(
        alt.X('year:T', axis=alt.Axis(format='%Y')),
        y='population'
    ).properties(
        width=500,
        height=300
    )

    point = line.mark_point(color='#333')

    rect = alt.Chart(source2).mark_rect().encode(
        x='start:T',
        x2='end:T',
        color='event:N'
    )

    chart = rect + line + point

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Gapminder Bubble Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.gapminder_health_income.url

    chart = alt.Chart(source).mark_circle().encode(
        alt.X('income:Q', scale=alt.Scale(type='log')),
        alt.Y('health:Q', scale=alt.Scale(zero=False)),
        size='population:Q'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Iowa Electricity
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iowa_electricity()

    chart = alt.Chart(source, title="Iowa's renewable energy boom").mark_area().encode(
        x=alt.X(
            "year:T",
            title="Year"
        ),
        y=alt.Y(
            "net_generation:Q",
            stack="normalize",
            title="Share of net generation",
            axis=alt.Axis(format=".0%"),
        ),
        color=alt.Color(
            "source:N",
            legend=alt.Legend(title="Electricity source"),
        )
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Isotype
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame([
          {'country': 'Great Britain', 'animal': 'cattle'},
          {'country': 'Great Britain', 'animal': 'cattle'},
          {'country': 'Great Britain', 'animal': 'cattle'},
          {'country': 'Great Britain', 'animal': 'pigs'},
          {'country': 'Great Britain', 'animal': 'pigs'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'}
        ])

    domains = ['person', 'cattle', 'pigs', 'sheep']

    shape_scale = alt.Scale(
        domain=domains,
        range=[
            'M1.7 -1.7h-0.8c0.3 -0.2 0.6 -0.5 0.6 -0.9c0 -0.6 -0.4 -1 -1 -1c-0.6 0 -1 0.4 -1 1c0 0.4 0.2 0.7 0.6 0.9h-0.8c-0.4 0 -0.7 0.3 -0.7 0.6v1.9c0 0.3 0.3 0.6 0.6 0.6h0.2c0 0 0 0.1 0 0.1v1.9c0 0.3 0.2 0.6 0.3 0.6h1.3c0.2 0 0.3 -0.3 0.3 -0.6v-1.8c0 0 0 -0.1 0 -0.1h0.2c0.3 0 0.6 -0.3 0.6 -0.6v-2c0.2 -0.3 -0.1 -0.6 -0.4 -0.6z',
            'M4 -2c0 0 0.9 -0.7 1.1 -0.8c0.1 -0.1 -0.1 0.5 -0.3 0.7c-0.2 0.2 1.1 1.1 1.1 1.2c0 0.2 -0.2 0.8 -0.4 0.7c-0.1 0 -0.8 -0.3 -1.3 -0.2c-0.5 0.1 -1.3 1.6 -1.5 2c-0.3 0.4 -0.6 0.4 -0.6 0.4c0 0.1 0.3 1.7 0.4 1.8c0.1 0.1 -0.4 0.1 -0.5 0c0 0 -0.6 -1.9 -0.6 -1.9c-0.1 0 -0.3 -0.1 -0.3 -0.1c0 0.1 -0.5 1.4 -0.4 1.6c0.1 0.2 0.1 0.3 0.1 0.3c0 0 -0.4 0 -0.4 0c0 0 -0.2 -0.1 -0.1 -0.3c0 -0.2 0.3 -1.7 0.3 -1.7c0 0 -2.8 -0.9 -2.9 -0.8c-0.2 0.1 -0.4 0.6 -0.4 1c0 0.4 0.5 1.9 0.5 1.9l-0.5 0l-0.6 -2l0 -0.6c0 0 -1 0.8 -1 1c0 0.2 -0.2 1.3 -0.2 1.3c0 0 0.3 0.3 0.2 0.3c0 0 -0.5 0 -0.5 0c0 0 -0.2 -0.2 -0.1 -0.4c0 -0.1 0.2 -1.6 0.2 -1.6c0 0 0.5 -0.4 0.5 -0.5c0 -0.1 0 -2.7 -0.2 -2.7c-0.1 0 -0.4 2 -0.4 2c0 0 0 0.2 -0.2 0.5c-0.1 0.4 -0.2 1.1 -0.2 1.1c0 0 -0.2 -0.1 -0.2 -0.2c0 -0.1 -0.1 -0.7 0 -0.7c0.1 -0.1 0.3 -0.8 0.4 -1.4c0 -0.6 0.2 -1.3 0.4 -1.5c0.1 -0.2 0.6 -0.4 0.6 -0.4z',
            'M1.2 -2c0 0 0.7 0 1.2 0.5c0.5 0.5 0.4 0.6 0.5 0.6c0.1 0 0.7 0 0.8 0.1c0.1 0 0.2 0.2 0.2 0.2c0 0 -0.6 0.2 -0.6 0.3c0 0.1 0.4 0.9 0.6 0.9c0.1 0 0.6 0 0.6 0.1c0 0.1 0 0.7 -0.1 0.7c-0.1 0 -1.2 0.4 -1.5 0.5c-0.3 0.1 -1.1 0.5 -1.1 0.7c-0.1 0.2 0.4 1.2 0.4 1.2l-0.4 0c0 0 -0.4 -0.8 -0.4 -0.9c0 -0.1 -0.1 -0.3 -0.1 -0.3l-0.2 0l-0.5 1.3l-0.4 0c0 0 -0.1 -0.4 0 -0.6c0.1 -0.1 0.3 -0.6 0.3 -0.7c0 0 -0.8 0 -1.5 -0.1c-0.7 -0.1 -1.2 -0.3 -1.2 -0.2c0 0.1 -0.4 0.6 -0.5 0.6c0 0 0.3 0.9 0.3 0.9l-0.4 0c0 0 -0.4 -0.5 -0.4 -0.6c0 -0.1 -0.2 -0.6 -0.2 -0.5c0 0 -0.4 0.4 -0.6 0.4c-0.2 0.1 -0.4 0.1 -0.4 0.1c0 0 -0.1 0.6 -0.1 0.6l-0.5 0l0 -1c0 0 0.5 -0.4 0.5 -0.5c0 -0.1 -0.7 -1.2 -0.6 -1.4c0.1 -0.1 0.1 -1.1 0.1 -1.1c0 0 -0.2 0.1 -0.2 0.1c0 0 0 0.9 0 1c0 0.1 -0.2 0.3 -0.3 0.3c-0.1 0 0 -0.5 0 -0.9c0 -0.4 0 -0.4 0.2 -0.6c0.2 -0.2 0.6 -0.3 0.8 -0.8c0.3 -0.5 1 -0.6 1 -0.6z',
            'M-4.1 -0.5c0.2 0 0.2 0.2 0.5 0.2c0.3 0 0.3 -0.2 0.5 -0.2c0.2 0 0.2 0.2 0.4 0.2c0.2 0 0.2 -0.2 0.5 -0.2c0.2 0 0.2 0.2 0.4 0.2c0.2 0 0.2 -0.2 0.4 -0.2c0.1 0 0.2 0.2 0.4 0.1c0.2 0 0.2 -0.2 0.4 -0.3c0.1 0 0.1 -0.1 0.4 0c0.3 0 0.3 -0.4 0.6 -0.4c0.3 0 0.6 -0.3 0.7 -0.2c0.1 0.1 1.4 1 1.3 1.4c-0.1 0.4 -0.3 0.3 -0.4 0.3c-0.1 0 -0.5 -0.4 -0.7 -0.2c-0.3 0.2 -0.1 0.4 -0.2 0.6c-0.1 0.1 -0.2 0.2 -0.3 0.4c0 0.2 0.1 0.3 0 0.5c-0.1 0.2 -0.3 0.2 -0.3 0.5c0 0.3 -0.2 0.3 -0.3 0.6c-0.1 0.2 0 0.3 -0.1 0.5c-0.1 0.2 -0.1 0.2 -0.2 0.3c-0.1 0.1 0.3 1.1 0.3 1.1l-0.3 0c0 0 -0.3 -0.9 -0.3 -1c0 -0.1 -0.1 -0.2 -0.3 -0.2c-0.2 0 -0.3 0.1 -0.4 0.4c0 0.3 -0.2 0.8 -0.2 0.8l-0.3 0l0.3 -1c0 0 0.1 -0.6 -0.2 -0.5c-0.3 0.1 -0.2 -0.1 -0.4 -0.1c-0.2 -0.1 -0.3 0.1 -0.4 0c-0.2 -0.1 -0.3 0.1 -0.5 0c-0.2 -0.1 -0.1 0 -0.3 0.3c-0.2 0.3 -0.4 0.3 -0.4 0.3l0.2 1.1l-0.3 0l-0.2 -1.1c0 0 -0.4 -0.6 -0.5 -0.4c-0.1 0.3 -0.1 0.4 -0.3 0.4c-0.1 -0.1 -0.2 1.1 -0.2 1.1l-0.3 0l0.2 -1.1c0 0 -0.3 -0.1 -0.3 -0.5c0 -0.3 0.1 -0.5 0.1 -0.7c0.1 -0.2 -0.1 -1 -0.2 -1.1c-0.1 -0.2 -0.2 -0.8 -0.2 -0.8c0 0 -0.1 -0.5 0.4 -0.8z'
        ]
    )

    color_scale = alt.Scale(
        domain=domains,
        range=['rgb(162,160,152)', 'rgb(194,81,64)', 'rgb(93,93,93)', 'rgb(91,131,149)']
    )

    chart = alt.Chart(source).mark_point(filled=True, opacity=1, size=100).encode(
        alt.X('x:O', axis=None),
        alt.Y('animal:O', axis=None),
        alt.Row('country:N', header=alt.Header(title='')),
        alt.Shape('animal:N', legend=None, scale=shape_scale),
        alt.Color('animal:N', legend=None, scale=color_scale),
    ).transform_window(
        x='rank()',
        groupby=['country', 'animal']
    ).properties(width=550, height=140)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Isotype Emoji
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame([
          {'country': 'Great Britain', 'animal': 'cattle'},
          {'country': 'Great Britain', 'animal': 'cattle'},
          {'country': 'Great Britain', 'animal': 'cattle'},
          {'country': 'Great Britain', 'animal': 'pigs'},
          {'country': 'Great Britain', 'animal': 'pigs'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'Great Britain', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'cattle'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'pigs'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'},
          {'country': 'United States', 'animal': 'sheep'}
        ])chart = alt.Chart(source).mark_text(size=45, baseline='middle').encode(
        alt.X('x:O', axis=None),
        alt.Y('animal:O', axis=None),
        alt.Row('country:N', header=alt.Header(title='')),
        alt.Text('emoji:N')
    ).transform_calculate(
        emoji="{'cattle': '🐄', 'pigs': '🐖', 'sheep': '🐏'}[datum.animal]"
    ).transform_window(
        x='rank()',
        groupby=['country', 'animal']
    ).properties(width=550, height=140)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Airports
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    airports = data.airports()
    states = alt.topo_feature(data.us_10m.url, feature='states')

    # US states background
    background = alt.Chart(states).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=500,
        height=300
    ).project('albersUsa')

    # airport positions on background
    points = alt.Chart(airports).mark_circle(
        size=10,
        color='steelblue'
    ).encode(
        longitude='longitude:Q',
        latitude='latitude:Q',
        tooltip=['name', 'city', 'state']
    )

    chart = background + points
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## London Tube
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    boroughs = alt.topo_feature(data.londonBoroughs.url, 'boroughs')
    tubelines = alt.topo_feature(data.londonTubeLines.url, 'line')
    centroids = data.londonCentroids.url

    background = alt.Chart(boroughs).mark_geoshape(
        stroke='white',
        strokeWidth=2
    ).encode(
        color=alt.value('#eee'),
    ).properties(
        width=700,
        height=500
    )

    labels = alt.Chart(centroids).mark_text().encode(
        longitude='cx:Q',
        latitude='cy:Q',
        text='bLabel:N',
        size=alt.value(8),
        opacity=alt.value(0.6)
    ).transform_calculate(
        "bLabel", "indexof (datum.name,' ') > 0  ? substring(datum.name,0,indexof(datum.name, ' ')) : datum.name"
    )

    line_scale = alt.Scale(domain=["Bakerloo", "Central", "Circle", "District", "DLR",
                                   "Hammersmith & City", "Jubilee", "Metropolitan", "Northern",
                                   "Piccadilly", "Victoria", "Waterloo & City"],
                           range=["rgb(137,78,36)", "rgb(220,36,30)", "rgb(255,206,0)",
                                  "rgb(1,114,41)", "rgb(0,175,173)", "rgb(215,153,175)",
                                  "rgb(106,114,120)", "rgb(114,17,84)", "rgb(0,0,0)",
                                  "rgb(0,24,168)", "rgb(0,160,226)", "rgb(106,187,170)"])

    lines = alt.Chart(tubelines).mark_geoshape(
        filled=False,
        strokeWidth=2
    ).encode(
        alt.Color(
            'id:N',
            legend=alt.Legend(
                title=None,
                orient='bottom-right',
                offset=0
            ),
            scale=line_scale
        )
    )

    chart = background + labels + lines

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Natural Disasters
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.disasters.url

    chart = alt.Chart(source).mark_circle(
        opacity=0.8,
        stroke='black',
        strokeWidth=1
    ).encode(
        alt.X('Year:O', axis=alt.Axis(labelAngle=0)),
        alt.Y('Entity:N'),
        alt.Size('Deaths:Q',
            scale=alt.Scale(range=[0, 4000]),
            legend=alt.Legend(title='Annual Global Deaths')
        ),
        alt.Color('Entity:N', legend=None)
    ).properties(
        width=450,
        height=320
    ).transform_filter(
        alt.datum.Entity != 'All natural disasters'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## One Dot Per Zipcode
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    # Since the data is more than 5,000 rows we'll import it from a URL
    source = data.zipcodes.url

    chart = alt.Chart(source).transform_calculate(
        "leading digit", alt.expr.substring(alt.datum.zip_code, 0, 1)
    ).mark_circle(size=3).encode(
        longitude='longitude:Q',
        latitude='latitude:Q',
        color='leading digit:N',
        tooltip='zip_code:N'
    ).project(
        type='albersUsa'
    ).properties(
        width=650,
        height=400
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>



## Weather Heatmap
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    # Since the data is more than 5,000 rows we'll import it from a URL
    source = data.seattle_temps.url

    chart = alt.Chart(
        source,
        title="2010 Daily High Temperature (F) in Seattle, WA"
    ).mark_rect().encode(
        x='date(date):O',
        y='month(date):O',
        color=alt.Color('max(temp):Q', scale=alt.Scale(scheme="inferno")),
        tooltip=[
            alt.Tooltip('monthdate(date):T', title='Date'),
            alt.Tooltip('max(temp):Q', title='Max Temp')
        ]
    ).properties(width=550)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Seattle Weather Interactive
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather()

    scale = alt.Scale(domain=['sun', 'fog', 'drizzle', 'rain', 'snow'],
                      range=['#e7ba52', '#a7a7a7', '#aec7e8', '#1f77b4', '#9467bd'])
    color = alt.Color('weather:N', scale=scale)

    # We create two selections:
    # - a brush that is active on the top panel
    # - a multi-click that is active on the bottom panel
    brush = alt.selection_interval(encodings=['x'])
    click = alt.selection_multi(encodings=['color'])

    # Top panel is scatter plot of temperature vs time
    points = alt.Chart().mark_point().encode(
        alt.X('monthdate(date):T', title='Date'),
        alt.Y('temp_max:Q',
            title='Maximum Daily Temperature (C)',
            scale=alt.Scale(domain=[-5, 40])
        ),
        color=alt.condition(brush, color, alt.value('lightgray')),
        size=alt.Size('precipitation:Q', scale=alt.Scale(range=[5, 200]))
    ).properties(
        width=550,
        height=300
    ).add_selection(
        brush
    ).transform_filter(
        click
    )

    # Bottom panel is a bar chart of weather type
    bars = alt.Chart().mark_bar().encode(
        x='count()',
        y='weather:N',
        color=alt.condition(click, color, alt.value('lightgray')),
    ).transform_filter(
        brush
    ).properties(
        width=550,
    ).add_selection(
        click
    )

    chart = alt.vconcat(
        points,
        bars,
        data=source,
        title="Seattle Weather: 2012-2015"
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Us Employment
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    from vega_datasets import data

    source = data.us_employment()
    presidents = pd.DataFrame([
        {
            "start": "2006-01-01",
            "end": "2009-01-19",
            "president": "Bush"
        },
        {
            "start": "2009-01-20",
            "end": "2015-12-31",
            "president": "Obama"
        }
    ])

    bars = alt.Chart(
        source,
        title="The U.S. employment crash during the Great Recession"
    ).mark_bar().encode(
        x=alt.X("month:T", title=""),
        y=alt.Y("nonfarm_change:Q", title="Change in non-farm employment (in thousands)"),
        color=alt.condition(
            alt.datum.nonfarm_change > 0,
            alt.value("steelblue"),
            alt.value("orange")
        )
    )

    rule = alt.Chart(presidents).mark_rule(
        color="black",
        strokeWidth=2
    ).encode(
        x='end:T'
    ).transform_filter(alt.datum.president == "Bush")

    text = alt.Chart(presidents).mark_text(
        align='left',
        baseline='middle',
        dx=7,
        dy=-135,
        size=11
    ).encode(
        x='start:T',
        x2='end:T',
        text='president',
        color=alt.value('#000000')
    )

    chart = (bars + rule + text).properties(width=600)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Top K Letters
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    import numpy as np

    # Excerpt from A Tale of Two Cities; public domain text
    text = """
    It was the best of times, it was the worst of times, it was the age of wisdom,
    it was the age of foolishness, it was the epoch of belief, it was the epoch of
    incredulity, it was the season of Light, it was the season of Darkness, it was
    the spring of hope, it was the winter of despair, we had everything before us,
    we had nothing before us, we were all going direct to Heaven, we were all going
    direct the other way - in short, the period was so far like the present period,
    that some of its noisiest authorities insisted on its being received, for good
    or for evil, in the superlative degree of comparison only.
    """

    source = pd.DataFrame(
        {'letters': np.array([c for c in text if c.isalpha()])}
    )

    chart = alt.Chart(source).transform_aggregate(
        count='count()',
        groupby=['letters']
    ).transform_window(
        rank='rank(count)',
        sort=[alt.SortField('count', order='descending')]
    ).transform_filter(
        alt.datum.rank < 10
    ).mark_bar().encode(
        y=alt.Y('letters:N', sort='-x'),
        x='count:Q',
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Top K With Others
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    chart = alt.Chart(source).mark_bar().encode(
        x=alt.X("aggregate_gross:Q", aggregate="mean", title=None),
        y=alt.Y(
            "ranked_director:N",
            sort=alt.Sort(op="mean", field="aggregate_gross", order="descending"),
            title=None,
        ),
    ).transform_aggregate(
        aggregate_gross='mean(Worldwide_Gross)',
        groupby=["Director"],
    ).transform_window(
        rank='row_number()',
        sort=[alt.SortField("aggregate_gross", order="descending")],
    ).transform_calculate(
        ranked_director="datum.rank < 10 ? datum.Director : 'All Others'"
    ).properties(
        title="Top Directors by Average Worldwide Gross",
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Us State Capitals
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    states = alt.topo_feature(data.us_10m.url, 'states')
    capitals = data.us_state_capitals.url

    # US states background
    background = alt.Chart(states).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        title='US State Capitols',
        width=650,
        height=400
    ).project('albersUsa')

    # Points and text
    hover = alt.selection(type='single', on='mouseover', nearest=True,
                          fields=['lat', 'lon'])

    base = alt.Chart(capitals).encode(
        longitude='lon:Q',
        latitude='lat:Q',
    )

    text = base.mark_text(dy=-5, align='right').encode(
        alt.Text('city', type='nominal'),
        opacity=alt.condition(~hover, alt.value(0), alt.value(1))
    )

    points = base.mark_point().encode(
        color=alt.value('black'),
        size=alt.condition(~hover, alt.value(30), alt.value(100))
    ).add_selection(hover)

    chart = background + points + text

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Us Population Over Time
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.population.url

    pink_blue = alt.Scale(domain=('Male', 'Female'),
                          range=["steelblue", "salmon"])

    slider = alt.binding_range(min=1900, max=2000, step=10)
    select_year = alt.selection_single(name="year", fields=['year'],
                                       bind=slider, init={'year': 2000})

    chart = alt.Chart(source).mark_bar().encode(
        x=alt.X('sex:N', title=None),
        y=alt.Y('people:Q', scale=alt.Scale(domain=(0, 12000000))),
        color=alt.Color('sex:N', scale=pink_blue),
        column='age:O'
    ).properties(
        width=20
    ).add_selection(
        select_year
    ).transform_calculate(
        "sex", alt.expr.if_(alt.datum.sex == 1, "Male", "Female")
    ).transform_filter(
        select_year
    ).configure_facet(
        spacing=8
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Wheat Wages
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import database_wheat = alt.Chart(data.wheat.url).transform_calculate(
        year_end="+datum.year + 5")

    base_monarchs = alt.Chart(data.monarchs.url).transform_calculate(
        offset="((!datum.commonwealth && datum.index % 2) ? -1: 1) * 2 + 95",
        off2="((!datum.commonwealth && datum.index % 2) ? -1: 1) + 95",
        y="95",
        x="+datum.start + (+datum.end - +datum.start)/2"
    )

    bars = base_wheat.mark_bar(**{"fill": "#aaa", "stroke": "#999"}).encode(
        x=alt.X("year:Q", axis=alt.Axis(format='d', tickCount=5)),
        y=alt.Y("wheat:Q", axis=alt.Axis(zindex=1)),
        x2=alt.X2("year_end")
    )

    area = base_wheat.mark_area(**{"color": "#a4cedb", "opacity": 0.7}).encode(
        x=alt.X("year:Q"),
        y=alt.Y("wages:Q")
    )

    area_line_1 = area.mark_line(**{"color": "#000", "opacity": 0.7})
    area_line_2 = area.mark_line(**{"yOffset": -2, "color": "#EE8182"})

    top_bars = base_monarchs.mark_bar(stroke="#000").encode(
        x=alt.X("start:Q"),
        x2=alt.X2("end"),
        y=alt.Y("y:Q"),
        y2=alt.Y2("offset"),
        fill=alt.Fill("commonwealth:N", legend=None, scale=alt.Scale(range=["black", "white"]))
    )

    top_text = base_monarchs.mark_text(**{"yOffset": 14, "fontSize": 9, "fontStyle": "italic"}).encode(
        x=alt.X("x:Q"),
        y=alt.Y("off2:Q"),
        text=alt.Text("name:N")
    )

    chart = (bars + area + area_line_1 + area_line_2 + top_bars + top_text).properties(
        width=900, height=400
    ).configure_axis(
        title=None, gridColor="white", gridOpacity=0.25, domain=False
    ).configure_view(
        stroke="transparent"
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Window Rank
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame(
        [
            {"team": "Germany", "matchday": 1, "point": 0, "diff": -1},
            {"team": "Germany", "matchday": 2, "point": 3, "diff": 0},
            {"team": "Germany", "matchday": 3, "point": 3, "diff": -2},
            {"team": "Mexico", "matchday": 1, "point": 3, "diff": 1},
            {"team": "Mexico", "matchday": 2, "point": 6, "diff": 2},
            {"team": "Mexico", "matchday": 3, "point": 6, "diff": -1},
            {"team": "South Korea", "matchday": 1, "point": 0, "diff": -1},
            {"team": "South Korea", "matchday": 2, "point": 0, "diff": -2},
            {"team": "South Korea", "matchday": 3, "point": 3, "diff": 0},
            {"team": "Sweden", "matchday": 1, "point": 3, "diff": 1},
            {"team": "Sweden", "matchday": 2, "point": 3, "diff": 0},
            {"team": "Sweden", "matchday": 3, "point": 6, "diff": 3},
        ]
    )

    color_scale = alt.Scale(
        domain=["Germany", "Mexico", "South Korea", "Sweden"],
        range=["#000000", "#127153", "#C91A3C", "#0C71AB"],
    )

    chart = alt.Chart(source).mark_line().encode(
        x="matchday:O", y="rank:O", color=alt.Color("team:N", scale=color_scale)
    ).transform_window(
        rank="rank()",
        sort=[
            alt.SortField("point", order="descending"),
            alt.SortField("diff", order="descending"),
        ],
        groupby=["matchday"],
    ).properties(title="World Cup 2018: Group F Rankings")

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Bar Chart With Highlighted Segment
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd
    from vega_datasets import data

    source = data.wheat()
    threshold = pd.DataFrame([{"threshold": 90}])

    bars = alt.Chart(source).mark_bar().encode(
        x="year:O",
        y="wheat:Q",
    )

    highlight = alt.Chart(source).mark_bar(color="#e45755").encode(
        x='year:O',
        y='baseline:Q',
        y2='wheat:Q'
    ).transform_filter(
        alt.datum.wheat > 90
    ).transform_calculate("baseline", "90")

    rule = alt.Chart(threshold).mark_rule().encode(
        y='threshold:Q'
    )

    chart = (bars + highlight + rule).properties(width=600)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Beckers Barley Wrapped Facet
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley.url

    chart = alt.Chart(source).mark_point().encode(
        alt.X('median(yield):Q', scale=alt.Scale(zero=False)),
        y='variety:O',
        color='year:N',
        facet=alt.Facet('site:O', columns=2),
    ).properties(
        width=200,
        height=100,
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Binned Heatmap
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.movies.url

    chart = alt.Chart(source).mark_rect().encode(
        alt.X('IMDB_Rating:Q', bin=alt.Bin(maxbins=60)),
        alt.Y('Rotten_Tomatoes_Rating:Q', bin=alt.Bin(maxbins=40)),
        alt.Color('count():Q', scale=alt.Scale(scheme='greenblue'))
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Boxplot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.population.url

    chart = alt.Chart(source).mark_boxplot(extent='min-max').encode(
        x='age:O',
        y='people:Q'
    )
    
st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Candlestick Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.ohlc()

    open_close_color = alt.condition("datum.open <= datum.close",
                                     alt.value("#06982d"),
                                     alt.value("#ae1325"))

    base = alt.Chart(source).encode(
        alt.X('date:T',
              axis=alt.Axis(
                  format='%m/%d',
                  labelAngle=-45,
                  title='Date in 2009'
              )
        ),
        color=open_close_color
    )

    rule = base.mark_rule().encode(
        alt.Y(
            'low:Q',
            title='Price',
            scale=alt.Scale(zero=False),
        ),
        alt.Y2('high:Q')
    )

    bar = base.mark_bar().encode(
        alt.Y('open:Q'),
        alt.Y2('close:Q')
    )

    chart = rule + bar

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Errorbars With Std
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    error_bars = alt.Chart(source).mark_errorbar(extent='stdev').encode(
      x=alt.X('yield:Q', scale=alt.Scale(zero=False)),
      y=alt.Y('variety:N')
    )

    points = alt.Chart(source).mark_point(filled=True, color='black').encode(
      x=alt.X('yield:Q', aggregate='mean'),
      y=alt.Y('variety:N'),
    )

    chart = error_bars + points

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Errorbars With Ci
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    error_bars = alt.Chart(source).mark_errorbar(extent='ci').encode(
      x=alt.X('yield:Q', scale=alt.Scale(zero=False)),
      y=alt.Y('variety:N')
    )

    points = alt.Chart(source).mark_point(filled=True, color='black').encode(
      x=alt.X('yield:Q', aggregate='mean'),
      y=alt.Y('variety:N'),
    )

    chart = error_bars + points

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Scatter Marginal Hist
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iris()

    base = alt.Chart(source)

    xscale = alt.Scale(domain=(4.0, 8.0))
    yscale = alt.Scale(domain=(1.9, 4.55))

    bar_args = {'opacity': .3, 'binSpacing': 0}

    points = base.mark_circle().encode(
        alt.X('sepalLength', scale=xscale),
        alt.Y('sepalWidth', scale=yscale),
        color='species',
    )

    top_hist = base.mark_bar(**bar_args).encode(
        alt.X('sepalLength:Q',
              # when using bins, the axis scale is set through
              # the bin extent, so we do not specify the scale here
              # (which would be ignored anyway)
              bin=alt.Bin(maxbins=20, extent=xscale.domain),
              stack=None,
              title=''
             ),
        alt.Y('count()', stack=None, title=''),
        alt.Color('species:N'),
    ).properties(height=60)

    right_hist = base.mark_bar(**bar_args).encode(
        alt.Y('sepalWidth:Q',
              bin=alt.Bin(maxbins=20, extent=yscale.domain),
              stack=None,
              title='',
             ),
        alt.X('count()', stack=None, title=''),
        alt.Color('species:N'),
    ).properties(width=60)

    chart = top_hist & (points | right_hist)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Gantt Chart
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame([
        {"task": "A", "start": 1, "end": 3},
        {"task": "B", "start": 3, "end": 8},
        {"task": "C", "start": 8, "end": 10}
    ])

    chart = alt.Chart(source).mark_bar().encode(
        x='start',
        x2='end',
        y='task'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Hexbins
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather()

    # Size of the hexbins
    size = 15
    # Count of distinct x features
    xFeaturesCount = 12
    # Count of distinct y features
    yFeaturesCount = 7
    # Name of the x field
    xField = 'date'
    # Name of the y field
    yField = 'date'

    # the shape of a hexagon
    hexagon = "M0,-2.3094010768L2,-1.1547005384 2,1.1547005384 0,2.3094010768 -2,1.1547005384 -2,-1.1547005384Z"

    chart = alt.Chart(source).mark_point(size=size**2, shape=hexagon).encode(
        x=alt.X('xFeaturePos:Q', axis=alt.Axis(title='Month',
                                               grid=False, tickOpacity=0, domainOpacity=0)),
        y=alt.Y('day(' + yField + '):O', axis=alt.Axis(title='Weekday',
                                                       labelPadding=20, tickOpacity=0, domainOpacity=0)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.2),
        fill=alt.Color('mean(temp_max):Q', scale=alt.Scale(scheme='darkblue')),
        tooltip=['month(' + xField + '):O', 'day(' + yField + '):O', 'mean(temp_max):Q']
    ).transform_calculate(
        # This field is required for the hexagonal X-Offset
        xFeaturePos='(day(datum.' + yField + ') % 2) / 2 + month(datum.' + xField + ')'
    ).properties(
        # Exact scaling factors to make the hexbins fit
        width=size * xFeaturesCount * 2,
        height=size * yFeaturesCount * 1.7320508076,  # 1.7320508076 is approx. sin(60°)*2
    ).configure_view(
        strokeWidth=0
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Isotype Grid
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    data = pd.DataFrame([dict(id=i) for i in range(1, 101)])

    person = (
        "M1.7 -1.7h-0.8c0.3 -0.2 0.6 -0.5 0.6 -0.9c0 -0.6 "
        "-0.4 -1 -1 -1c-0.6 0 -1 0.4 -1 1c0 0.4 0.2 0.7 0.6 "
        "0.9h-0.8c-0.4 0 -0.7 0.3 -0.7 0.6v1.9c0 0.3 0.3 0.6 "
        "0.6 0.6h0.2c0 0 0 0.1 0 0.1v1.9c0 0.3 0.2 0.6 0.3 "
        "0.6h1.3c0.2 0 0.3 -0.3 0.3 -0.6v-1.8c0 0 0 -0.1 0 "
        "-0.1h0.2c0.3 0 0.6 -0.3 0.6 -0.6v-2c0.2 -0.3 -0.1 "
        "-0.6 -0.4 -0.6z"
    )

    chart = alt.Chart(data).transform_calculate(
        row="ceil(datum.id/10)"
    ).transform_calculate(
        col="datum.id - datum.row*10"
    ).mark_point(
        filled=True,
        size=50
    ).encode(
        x=alt.X("col:O", axis=None),
        y=alt.Y("row:O", axis=None),
        shape=alt.ShapeValue(person)
    ).properties(
        width=400,
        height=400
    ).configure_view(
        strokeWidth=0
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Layered Chart With Dual Axis
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather()

    base = alt.Chart(source).encode(
        alt.X('month(date):T', axis=alt.Axis(title=None))
    )

    area = base.mark_area(opacity=0.3, color='#57A44C').encode(
        alt.Y('average(temp_max)',
              axis=alt.Axis(title='Avg. Temperature (°C)', titleColor='#57A44C')),
        alt.Y2('average(temp_min)')
    )

    line = base.mark_line(stroke='#5276A7', interpolate='monotone').encode(
        alt.Y('average(precipitation)',
              axis=alt.Axis(title='Precipitation (inches)', titleColor='#5276A7'))
    )

    chart = alt.layer(area, line).resolve_scale(
        y = 'independent'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Multiple Marks
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.stocks()

    chart = alt.Chart(source).mark_line(point=True).encode(
        x='date:T',
        y='price:Q',
        color='symbol:N'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Normed Parallel Coordinates
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data
    from altair import datum

    source = data.iris()

    chart = alt.Chart(source).transform_window(
        index='count()'
    ).transform_fold(
        ['petalLength', 'petalWidth', 'sepalLength', 'sepalWidth']
    ).transform_joinaggregate(
         min='min(value)',
         max='max(value)',
         groupby=['key']
    ).transform_calculate(
        minmax_value=(datum.value-datum.min)/(datum.max-datum.min),
        mid=(datum.min+datum.max)/2
    ).mark_line().encode(
        x='key:N',
        y='minmax_value:Q',
        color='species:N',
        detail='index:N',
        opacity=alt.value(0.5)
    ).properties(width=500)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Parallel Coordinates
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.iris()

    chart = alt.Chart(source).transform_window(
        index='count()'
    ).transform_fold(
        ['petalLength', 'petalWidth', 'sepalLength', 'sepalWidth']
    ).mark_line().encode(
        x='key:N',
        y='value:Q',
        color='species:N',
        detail='index:N',
        opacity=alt.value(0.5)
    ).properties(width=500)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Pyramid
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    category = ['Sky', 'Shady side of a pyramid', 'Sunny side of a pyramid']
    color = ["#416D9D", "#674028", "#DEAC58"]
    df = pd.DataFrame({'category': category, 'value': [75, 10, 15]})

    chart = alt.Chart(df).mark_arc(outerRadius=80).encode(
        alt.Theta('value:Q', scale=alt.Scale(range=[2.356, 8.639])),
        alt.Color('category:N',
            scale=alt.Scale(domain=category, range=color),
            legend=alt.Legend(title=None, orient='none', legendX=160, legendY=50)),
        order='value:Q'
    ).properties(width=150, height=150).configure_view(strokeOpacity=0)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Ranged Dot Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.countries.url

    chart = alt.layer(
        data=source
    ).transform_filter(
        filter={"field": 'country',
                "oneOf": ["China", "India", "United States", "Indonesia", "Brazil"]}
    ).transform_filter(
        filter={'field': 'year',
                "oneOf": [1955, 2000]}
    )

    chart += alt.Chart().mark_line(color='#db646f').encode(
        x='life_expect:Q',
        y='country:N',
        detail='country:N'
    )
    # Add points for life expectancy in 1955 & 2000
    chart += alt.Chart().mark_point(
        size=100,
        opacity=1,
        filled=True
    ).encode(
        x='life_expect:Q',
        y='country:N',
        color=alt.Color('year:O',
            scale=alt.Scale(
                domain=['1955', '2000'],
                range=['#e6959c', '#911a24']
            )
        )
    ).interactive()

    chart = chart

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Ridgeline Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.seattle_weather.url

    step = 20
    overlap = 1

    chart = alt.Chart(source, height=step).transform_timeunit(
        Month='month(date)'
    ).transform_joinaggregate(
        mean_temp='mean(temp_max)', groupby=['Month']
    ).transform_bin(
        ['bin_max', 'bin_min'], 'temp_max'
    ).transform_aggregate(
        value='count()', groupby=['Month', 'mean_temp', 'bin_min', 'bin_max']
    ).transform_impute(
        impute='value', groupby=['Month', 'mean_temp'], key='bin_min', value=0
    ).mark_area(
        interpolate='monotone',
        fillOpacity=0.8,
        stroke='lightgray',
        strokeWidth=0.5
    ).encode(
        alt.X('bin_min:Q', bin='binned', title='Maximum Daily Temperature (C)'),
        alt.Y(
            'value:Q',
            scale=alt.Scale(range=[step, -step * overlap]),
            axis=None
        ),
        alt.Fill(
            'mean_temp:Q',
            legend=None,
            scale=alt.Scale(domain=[30, 5], scheme='redyellowblue')
        )
    ).facet(
        row=alt.Row(
            'Month:T',
            title=None,
            header=alt.Header(labelAngle=0, labelAlign='right', format='%B')
        )
    ).properties(
        title='Seattle Weather',
        bounds='flush'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    ).configure_title(
        anchor='end'
    )

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Sorted Error Bars With Ci
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    from vega_datasets import data

    source = data.barley()

    points = alt.Chart(source).mark_point(
        filled=True,
        color='black'
    ).encode(
        x=alt.X('mean(yield)', title='Barley Yield'),
        y=alt.Y(
            'variety',
             sort=alt.EncodingSortField(
                 field='yield',
                 op='mean',
                 order='descending'
             )
        )
    ).properties(
        width=400,
        height=250
    )

    error_bars = points.mark_rule().encode(
        x='ci0(yield)',
        x2='ci1(yield)',
    )

    chart = points + error_bars

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>

## Wilkinson Dot Plot
<pre><code class="language-python">
import streamlit as st
    import altair as alt
    import pandas as pd

    source = pd.DataFrame(
        {"data":[1,1,1,1,1,1,1,1,1,1,
                 2,2,2,
                 3,3,
                 4,4,4,4,4,4]
        }
    )

    chart = alt.Chart(source).mark_circle(opacity=1).transform_window(
        id='rank()',
        groupby=['data']
    ).encode(
        alt.X('data:O'),
        alt.Y('id:O',
              axis=None,
              sort='descending')
    ).properties(height=100)

st.altair_chart(chart, theme="streamlit", use_container_width=True)
</code></pre>


