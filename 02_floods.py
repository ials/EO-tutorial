import ee
import geemap

import solara


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_ee_data()


    def add_ee_data(self):
        # Select the eight NLCD epochs after 2000.
        years = ['2001_01_01', '2004_01_01', '2007_01_01', '2010_01_01', 
         '2013_01_01', '2016_01_01', '2019_01_01', '2022_01_01']

        # select country
        colombia = (
           ee.FeatureCollection("FAO/GAUL/2015/level0")
          .filter("ADM0_NAME == 'Colombia'")
          .filter(ee.Filter.eq('ADM0_NAME', 'Colombia'))
        )

        # Set year
        def getLC(year):
            data = ee.ImageCollection('MODIS/061/MCD12Q1').filterBounds(colombia)
            LCCOL = data.map(lambda img: img.clip(colombia))
            nlcd = LCCOL.filter(ee.Filter.eq('system:index', year)).first()
            lc = nlcd.select('LC_Type1')
            return lc

        ## Create an NLCD image collection for the selected years.
        collection = ee.ImageCollection(ee.List(years).map(lambda year: getLC(year)))

        # Create a list of labels to populate the dropdown list.
        labels = [f"Cobertura {year}" for year in years]

        # Zoom into Colombia
        #self.center_Object(colombia,9)

        # Define estilo
        LC_estilo = {
          'min': 1.0,
          'max': 17.0,
          'palette': [
                '05450a', '086a10', '54a708', '78d203', '009900', 'c6b044', 'dcd159',
                'dade48', 'fbff13', 'b6ff05', '27ff87', 'c24f44', 'a5a5a5', 'ff6d4c',
                '69fff8', 'f9ffa4', '1c0dff'
                    ],
        }

        # Add a split-panel map for visualizing NLCD land cover change.
        self.ts_inspector(
            left_ts=collection,
            right_ts=collection,
            left_names=labels,
            right_names=labels,
            left_vis= LC_estilo,  right_vis= LC_estilo
        )

        # Add the NLCD legend to the map.
        self.add_legend(
            title="Cobertura del suelo",
            builtin_legend="MODIS/006/MCD12Q1",
            height="460px",
            add_header=False,
        )


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        Map.element(
            center=[6, -75],
            zoom=6,
            height="600px",
        )
