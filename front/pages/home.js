import { BaseComponent } from '../base-component.js'

const dec2 = num => Math.round(num * 100)  / 100

class HomePage extends BaseComponent {
  constructor () {
    super()
  }

  async connectedCallback () {
    // await this.getBacktests()
    await this.getStrategies()
    super.connectedCallback()
  }

  disconnectedCallback () {
  }

  async getStrategies () {

    const grossProfitReducer = (gp, tr) => {
      return tr.profit > 0 ? gp + tr.profit : gp
    }
    const grossLossReducer = (gl, tr) => tr.profit < 0 ? gl - tr.profit : gl
    
    const { success, data: strategies } = await this.httpGet('/api/strategies')
    if (success) {
      this.strategyHtml = !strategies.length
        ? `No strategies found`
        : strategies.map(s => {
          const kpis = JSON.parse(s.btKpis)
          return `
            <kor-card class="strat-card" label="${s.strategyName}">
              <article class="strat-info">
                <kor-input type="text" readonly label="Symbols" value="${s.symbols}"></kor-input>
                <kor-input type="text" readonly label="Timeframes" value="${s.timeframes}"></kor-input>
              </article>
              <kor-card class="mini-report">
                <kor-text size="header-2">Backtest</kor-text>
                <article class="backtest-info">
                  <kor-input type="text" readonly label="Start date" value="${s.btStart}"></kor-input>
                  <kor-input type="text" readonly label="End date" value="${s.btEnd}"></kor-input>
                  <kor-input type="text" readonly label="Initial capital" value="${s.btDeposit}"></kor-input>
                  <kor-input type="text" readonly label="Profit factor" value="${dec2(kpis.profitFactor)}"></kor-input>
                </article>
              </kor-card>
              <kor-card class="mini-report">
                <kor-text size="header-2">Demo</kor-text>
                <article class="demo-info">
                  <kor-input type="text" readonly label="Demo start" value="${s.demoStart}"></kor-input>
                </article>
              </kor-card>
            </kor-card>
          `
        }).join('')
    }
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
      }

      .strat-info {
        display: grid;
        grid-template-columns: 140px 140px;
        justify-content: center;
      }

      .backtest-info {
        display: grid;
        grid-template-columns: 90px 90px 90px;
        height: 120px;
      }

      .demo-info {
        display: grid;
        grid-template-columns: 90px 90px 90px;
        grid-template-rows: 1fr;
      }

      .mini-report {
        margin-bottom: 5px;
      }
    `
  }

  get html () {
    return `
      <div class="home-page">
        ${this.strategyHtml}
      </div>
      `
  }
}

window.customElements.define('home-page', HomePage)
