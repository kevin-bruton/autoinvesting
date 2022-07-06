import { BaseComponent } from '../base-component.js'
import { getMetrics } from '../utils/metrics.js'
import { dec2 } from '../utils/index.js'

class HomePage extends BaseComponent {
  constructor () {
    super()
  }

  async connectedCallback () {
    // await this.getBacktests()
    await this.getStrategies()
    super.connectedCallback()/* 
    const chartData = [
      ['2018-04-10T20:40:33Z', 1],
      ['2018-04-10T20:40:53Z', 2],
      ['2018-04-10T20:41:03Z', 4],
      ['2018-04-10T20:44:03Z', 5],
      ['2018-04-10T20:45:03Z', 6]
    ]
    this.getEl('equityChart').data = chartData */
  }

  disconnectedCallback () {
  }

  async getStrategies () {

    const grossProfitReducer = (gp, tr) => {
      return tr.profit > 0 ? gp + tr.profit : gp
    }
    const grossLossReducer = (gl, tr) => tr.profit < 0 ? gl - tr.profit : gl
    
    const { success, data: strategies } = await this.httpGet('/api/strategies')
    console.log('strategies:', strategies)
    if (success) {
      this.strategyHtml = !strategies.length
        ? `No strategies found`
        : strategies.map(s => {
          const btDeposit = Number(s.btDeposit)
          const showBacktest = s.btKpis && s.btTrades
          const btKpis = showBacktest ? JSON.parse(s.btKpis) : {}
          const btChartPctRet = showBacktest ? this.getChartPctReturn(s.btTrades, s.btStart, btDeposit) : null
          const demoDeposit = 1000
          const showDemo = s.demoKpis && s.demoTrades
          const demoKpis = showDemo ? JSON.parse(s.demoKpis) : {}
          const demoChartPctRet = showDemo ? this.getChartPctReturn(s.demoTrades, s.demoStart, demoDeposit) : null
          const demoEnd = (new Date()).toISOString().substring(0, 10)

          return `
            <kor-card class="strat-card" label="${s.strategyName}">
              <article class="strat-info">
                <kor-input type="text" readonly label="Symbols" value="${s.symbols}"></kor-input>
                <kor-input type="text" readonly label="Timeframes" value="${s.timeframes}"></kor-input>
              </article>
              ${showBacktest
                ? `<kor-card class="mini-report">
                    <kor-text size="header-2">Backtest</kor-text>
                    <article class="test-info">
                      <kor-input type="text" readonly label="Start date" value="${s.btStart}"></kor-input>
                      <kor-input type="text" readonly label="End date" value="${s.btEnd}"></kor-input>
                      <kor-input type="text" readonly label="Initial capital" value="${s.btDeposit}"></kor-input>
                      <kor-input type="text" readonly label="Profit factor" value="${btKpis.profitFactor}"></kor-input>
                      <kor-input type="text" readonly label="Ann%Ret/DD%" value="${btKpis.annPctRetVsDdPct}"></kor-input>
                      <kor-input type="text" readonly label="Win %" value="${btKpis.winPct}"></kor-input>
                      <equity-chart class="chart" id="equityChart" chart-width="280px" chart-height="150px" data='${JSON.stringify(btChartPctRet)}'></equity-chart>
                    </article>
                  </kor-card>`
                : ``}
              <kor-card class="mini-report">
                <kor-text size="header-2">Demo</kor-text>
                <article class="test-info">
                  <kor-input type="text" readonly label="Demo start" value="${s.demoStart}"></kor-input>
                  <kor-input type="text" readonly label="Demo end" value="${demoEnd}"></kor-input>
                  <kor-input type="text" readonly label="Based on capital" value="${demoDeposit}"></kor-input>
                  <kor-input type="text" readonly label="Profit factor" value="${demoKpis.profitFactor}"></kor-input>
                  <kor-input type="text" readonly label="Ann%Ret/DD%" value="${demoKpis.annPctRetVsDdPct}"></kor-input>
                  <kor-input type="text" readonly label="Win %" value="${demoKpis.winPct}"></kor-input>
                  <equity-chart class="chart" id="equityChart" chart-width="280px" chart-height="150px" data='${JSON.stringify(demoChartPctRet)}'></equity-chart>
                </article>
              </kor-card>
            </kor-card>
          `
        }).join('')
    }
  }

  getChartPctReturn (btTradesJson, btStart, deposit) {
    const btTrades = JSON.parse(btTradesJson)
    const balances = btTrades.map(trade => ([trade.closeTime, trade.balance]))
    balances.unshift([btStart, deposit])
    const equityByMonths = balances.reduce((byMth, pt) => {
      const [ptDate, ptVal] = pt
      const mth = ptDate.substring(0, 7)
      byMth[mth] ? byMth[mth].push(ptVal) : byMth[mth] = [ptVal]
      return byMth
    }, {})
    const chartPts = Object.keys(equityByMonths).reduce((pts, mth) => {
      const ptVal = equityByMonths[mth].reduce((sum, val) => sum+val, 0) / equityByMonths[mth].length
      pts.push([`${mth}-01 00:00:00`, ptVal])
      return pts
    }, [])
    const chartPctRet = chartPts.map(pt => [pt[0], Math.round(pt[1] / deposit * 100)])
    // const { annPctRetVsDdPct, sortino } = getMetrics(deposit, s.btStart, s.btEnd, balances.map(b => b[1]), btTrades.map(t => t.profit))
    return chartPctRet
  }

  async getTrades () {
    const { success, data: trades } = await this.httpGet('/api/trades')
    this.trades = trades
  }

  get css () {
    return `
      .home-page {
        margin: 30px;
        display: flex;
        gap: 30px;
        justify-content: flex-start;
        flex-wrap: wrap;
      }

      .strat-card {
        max-width: 350px;
        min-width: 350px;
        height: 800px;
      }

      .strat-info {
        display: grid;
        grid-template-columns: 140px 140px;
        justify-content: center;
      }

      .test-info {
        display: grid;
        grid-template-columns: 90px 100px 90px;
        grid-template-rows: 1fr 1fr 1fr;
        grid-template-areas: 
          "input1 input2 input3"
          "input4 input5 input6"
          "chart chart chart";
        height: 120px;
      }
      .test-info:nth-child(1) {
        grid-area: input1;
      }
      .test-info:nth-child(2) {
        grid-area: input2;
      }
      .test-info:nth-child(3) {
        grid-area: input3;
      }
      .test-info:nth-child(4) {
        grid-area: input4;
      }

      .test-info equity-chart {
        grid-area: chart;
      }

      .mini-report {
        margin-bottom: 5px;
      }
    `
  }

  get html () {
    const chartData = JSON.stringify([
      ['2018-04-10T20:40:33Z', 40000],
      ['2018-04-10T20:40:53Z', 45000],
      ['2018-04-10T20:41:03Z', 51000],
      ['2018-04-10T20:44:03Z', 41000],
      ['2018-04-10T20:45:03Z', 57000]
    ])
    return `
      <div class="home-page">
        ${this.strategyHtml}
      </div>
      <!-- <equity-chart id="equityChart" chart-width="300px" chart-height="300px" data='${chartData}'></equity-chart> -->
      `
  }
}

window.customElements.define('home-page', HomePage)
