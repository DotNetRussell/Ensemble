import BingMaps from 'ol/source/BingMaps';
import Map from 'ol/Map';
import TileLayer from 'ol/layer/Tile';
import View from 'ol/View';

const styles = [
  'RoadOnDemand',
  'Aerial',
  'AerialWithLabelsOnDemand',
  'CanvasDark',
  'OrdnanceSurvey',
];
const layers = [];
let i, ii;
for (i = 0, ii = styles.length; i < ii; ++i) {
  layers.push(
    new TileLayer({
      visible: false,
      preload: Infinity,
      source: new BingMaps({
        key: 'Your Bing Maps Key from https://www.bingmapsportal.com/ here',
        imagerySet: styles[i],
        // use maxZoom 19 to see stretched tiles instead of the BingMaps
        // "no photos at this zoom level" tiles
        // maxZoom: 19
      }),
    })
  );
}
const map = new Map({
  layers: layers,
  target: 'map',
  view: new View({
    center: [-6655.5402445057125, 6709968.258934638],
    zoom: 13,
  }),
});

const select = document.getElementById('layer-select');
function onChange() {
  const style = select.value;
  for (let i = 0, ii = layers.length; i < ii; ++i) {
    layers[i].setVisible(styles[i] === style);
  }
}
select.addEventListener('change', onChange);
onChange();
