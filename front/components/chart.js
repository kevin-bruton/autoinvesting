import { BaseComponent } from '../base-component.js'
import * as echarts from '../node_modules/echarts/dist/echarts.esm.js'


/**
 * EquityChart
 * 
 * Attributes:
 * width - Width of the chart as a CSS property
 * height - Height of the chart as a CSS property
 * [title] - The title to be displayed on the chart
 * 
 * Properties:
 * data - The data to be displayed. The chart will not show until the data property is set
 * eg. [
    ['2018-04-10T20:40:33Z', 1],
    ['2018-04-10T20:40:53Z', 2],
    ['2018-04-10T20:41:03Z', 4],
    ['2018-04-10T20:44:03Z', 5],
    ['2018-04-10T20:45:03Z', 6]
  ]
 */
class EquityChart extends BaseComponent {
  constructor () {
    super()
    this.render = this.render.bind(this)
  }
/*   
  static get observedAttributes() {
    return ['data'];
  } */

  async connectedCallback () {
    super.connectedCallback()
    this.render()
  }
/* 
  attributeChangedCallback(name, oldValue, newValue) {
    console.log('attrib changed. name:', name, '; oldValue:', oldValue, '; newValue:', newValue)
  } */

  disconnectedCallback () {
  }

  render () {
    this.getEl('chart').style.width = this.getAttribute('chart-width') || '600px'
    this.getEl('chart').style.height = this.getAttribute('chart-height') || '300px'
    const data = JSON.parse(this.getAttribute('data'))

    const echart = echarts.init(this.getEl('chart'))
    const title = this.getAttribute('title')
    const options = {
      grid: {
        containLabel: true,
        left: 8,
        right: 8,
        top: 50,
        bottom: 0
      },
      tooltip: { trigger: 'axis' },
      dataset: {
        source: data,
        dimensions: ['timestamp', 'balance'],
      },
      xAxis: { type: 'time' },
      yAxis: {
        name: '% Return',
        type: 'value'
      },
      series: [
        {
          name: 'trades',
          type: 'line',
          showSymbol: false,
          encode: {
            x: 'timestamp',
            y: 'balance'
          }
        }
      ]
    }
    if (title) {
      options.title = { text: title }
    }
    echart.setOption(options)
  }

  get css () {
    return `
      .chart-box {
        display: flex;
        justify-content: center;
      }
    `
  }

  get html () {
    return `
        <div class="chart-box">
          <div id="chart"></div>
        </div>
      `
  }
}

window.customElements.define('equity-chart', EquityChart)
