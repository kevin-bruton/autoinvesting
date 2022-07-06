import { BaseComponent } from '../base-component.js'
import getRandomName from '../getRandomName.js'
import { getMetrics } from '../utils/metrics.js'

class AddStrategyPage extends BaseComponent {
  constructor () {
    super()
    this.strategyName = getRandomName()
  }

  connectedCallback () {
    super.connectedCallback()
    this.shadowRoot.querySelector('#saveStrategy').addEventListener('click', this.saveStrategy.bind(this))
    this.shadowRoot.querySelector('#saveBacktest').addEventListener('click', this.saveBacktest.bind(this))
  }

  disconnectedCallback () {
    // super.disconnectedCallback()
    this.shadowRoot.querySelector('#saveStrategy').removeEventListener('click', this.saveStrategy.bind(this))
    this.shadowRoot.querySelector('#saveBacktest').removeEventListener('click', this.saveBacktest.bind(this))
  }

  async saveStrategy () {
    const textInputIds = ['strategyName', 'magic', 'symbols', 'timeframes', 'demoStart']
    const fileInputIds = ['mq4StrategyFile', 'sqxStrategyFile']
    const textInputEls = textInputIds.map(id => this.getEl(id))
    const textDetails = textInputIds.reduce((det, id) => ({ ...det, ...{ [id]: id === 'magic' ? Number(this.getEl(id).value) : this.getEl(id).value }}), {})
    const fileDetails = fileInputIds.reduce((det, id) => {
      const files = this.getEl(id).files
      return { ...det, ...{ [id]: files.length ? files[0].name : '' } }
    }, {})

    // Send strategy details and report the status in the input boxes
    const detailsResp = await this.httpPost('/api/strategies', { ...textDetails, ...fileDetails })
    const detailsStatus = (detailsResp.status >= 200 && detailsResp.status <= 209) ? 'success' : 'error'
    textInputEls.forEach(el => el.setAttribute('status', detailsStatus))
    this.setAttrib('saveStrategyResultBadge', 'status', detailsResp.error ? 'error' : 'success')
    this.setInnerHtml('saveStrategyResultText', detailsResp.error ? detailsResp.error : detailsResp.message)
    
    // Send files and report result for each
    const files = fileInputIds.reduce((det, id) => {
      const inputFiles = this.getEl(id).files
      return { ...det, ...{ [id]: inputFiles.length ? inputFiles[0] : '' } }
    }, {})

    for await (const id of Object.keys(files)) {
      const file = files[id]
      if (!file) {
        this.setAttrib(id, 'status', 'warning')
      } else {
        const resp = await this.httpPostFile(file)
        this.setAttrib(id + 'Badge', 'status', resp.error ? 'error' : 'success')
        this.setInnerHtml(id + 'Result', resp.error ? resp.error : resp.message)
      }
    }
  }

  async saveBacktest () {
    const strategyName = this.getVal('btStrategyName')
    const magic = this.getVal('btMagic')
    const startDate = this.getVal('btStart')
    const endDate = this.getVal('btEnd')
    const deposit = this.getVal('btDeposit')
    const tradesFilename = this.getInputFilename('btTradesFile')
    const fileContent = await this.getInputFileContent('btTradesFile')
    const saniDate = d => d.replace(/\./g, '-')
    const csvTradesToJs = csvStr => {
      const trades = []
      const lines = csvStr.split('\n')
      for (const line of lines.splice(1)) {
        const cells = line.split(';').map(c => c.replace(/"/g, ''))
        if (cells.length === 16) {
          const trade = {
            symbol: cells[1],
            direction: cells[2], 
            openTime: saniDate(cells[3]),
            openPrice: Number(cells[4]),
            size: Number(cells[5]),
            closeTime: saniDate(cells[6]),
            closePrice: Number(cells[7]),
            profit: Number(cells[8]),
            balance: Number(cells[9]),
            closeType: cells[11],
            comment: cells[15].trim()
          }
          trades.push(trade)
        }
      }
      return trades
    }
    const trades = csvTradesToJs(fileContent)
    const balances = trades.map(t => t.balance)
    balances.unshift(deposit)
    const profit = trades.map(t => t.profit)
    const kpis = getMetrics(deposit, startDate, endDate, balances, profit)
    const data = {
      strategyName,
      magic,
      startDate,
      endDate,
      deposit,
      trades,
      kpis
    }
    const resp = await this.httpPost('/api/backtest', data)
    /* const tradesFile = this.getInputFile('btTradesFile')
    const resp = await this.httpPostBacktest(tradesFile, strategyName, btStart, btEnd, btDeposit) */

    this.setAttrib('saveBacktestResultBadge', 'status', resp.error ? 'error' : 'success')
    this.setInnerHtml('saveBacktestResultText', resp.error ? resp.error : resp.message)
  }

  get css () {
    return `
      .add-strategy-page {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 30px;
        margin: 30px;
      }

      .fileUpload {
        display: flex;
        align-items: baseline;
      }

      .saveStrategyBox {
        display: flex; 
      }
    `
  }

  get html () {
    return `
      <div class="add-strategy-page">
        <kor-card icon="add_chart" label="Add Strategy Details">
          <kor-input type="text" label="Strategy Name" id="strategyName" value="${this.strategyName}"></kor-input>
          <kor-input type="text" label="Magic number" id="magic"></kor-input>
          <kor-input type="text" label="Symbols that the strategy operates on (separated by commas)" id="symbols"></kor-input>
          <kor-input type="text" label="Timeframes that the strategy operates on (separated by commas)" id="timeframes"></kor-input>
          <kor-input type="text" label="Demo start date (format YYYY-MM-DD)" id="demoStart"></kor-input>
          <div class="fileUpload"><kor-text size="body-1">MT4 strategy file: <input type="file" label="MT4 strategy file" id="mq4StrategyFile"></input></kor-text><kor-badge id="mq4StrategyFileBadge" status=""></kor-badge><kor-text size="body-2" id="mq4StrategyFileResult"></kor-text></div>
          <div class="fileUpload"><kor-text size="body-1">SQX strategy file: <input type="file" label="SQX strategy file" id="sqxStrategyFile"></input></kor-text><kor-badge id="sqxStrategyFileBadge" status=""></kor-badge><kor-text size="body-2" id="sqxStrategyFileResult"></kor-text></div>
          <div class="saveStrategyBox">
            <kor-button id="saveStrategy" label="Save"></kor-button>
            <kor-badge id="saveStrategyResultBadge" status=""></kor-badge>
            <kor-text size="body-2" id="saveStrategyResultText"></kor-text>
          </div>
        </kor-card>
        <kor-card icon="add_chart" label="Save SQX Backtest">
          <kor-input type="text" label="Strategy Name" id="btStrategyName" value="${this.strategyName}"></kor-input>
          <kor-input type="number" label="magic" id="btMagic" value=""></kor-input>
          <kor-input type="text" label="Backtest start date (format YYYY-MM-DD)" id="btStart"></kor-input>
          <kor-input type="text" label="Backtest end date (format YYYY-MM-DD)" id="btEnd"></kor-input>
          <kor-input type="text" label="Backtest inicial capital" id="btDeposit" value="10000"></kor-input>
          <div class="fileUpload"><kor-text size="body-1">Trades CSV file: <input type="file" label="SQX strategy file" id="btTradesFile"></input></kor-text><kor-badge id="tradesBadge" status=""></kor-badge><kor-text size="body-2" id="tradesResult"></kor-text></div>
          <div class="saveStrategyBox">
            <kor-button id="saveBacktest" label="Save"></kor-button>
            <kor-badge id="saveBacktestResultBadge" status=""></kor-badge>
            <kor-text size="body-2" id="saveBacktestResultText"></kor-text>
          </div>
        </kor-card>
      </div>
      `
  }
}

window.customElements.define('add-strategy-page', AddStrategyPage)
