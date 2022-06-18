import { BaseComponent } from './base-component.js'
import getRandomName from './getRandomName.js'

class AddStrategy extends BaseComponent {
  constructor () {
    super()
    this.strategyName = getRandomName()
  }

  connectedCallback () {
    super.connectedCallback()
    this.shadowRoot.querySelector('#saveStrategy').addEventListener('click', this.saveStrategy.bind(this))
    this.shadowRoot.querySelector('#saveTrades').addEventListener('click', this.saveTrades.bind(this))
  }

  disconnectedCallback () {
    super.disconnectedCallback()
    this.shadowRoot.querySelector('#saveStrategy').removeEventListener('click', this.saveStrategy.bind(this))
    this.shadowRoot.querySelector('#saveTrades').removeEventListener('click', this.saveTrades.bind(this))
  }

  async saveStrategy () {
    const textInputIds = ['strategyName', 'magic', 'symbols', 'timeframes', 'generatedDate', 'demoDate', 'liveDate']
    const fileInputIds = ['mt4StrategyFile', 'sqxStrategyFile']
    const textInputEls = textInputIds.map(id => this.getEl(id))
    const textDetails = textInputIds.reduce((det, id) => ({ ...det, ...{ [id]: id === 'magic' ? Number(this.getEl(id).value) : this.getEl(id).value }}), {})
    const fileDetails = fileInputIds.reduce((det, id) => {
      const files = this.getEl(id).files
      return { ...det, ...{ [id]: files.length ? files[0].name : '' } }
    }, {})

    // Send strategy details and report the status in the input boxes
    const detailsResp = await this.httpPost('/api/strategy', { ...textDetails, ...fileDetails })
    const detailsStatus = (detailsResp.status >= 200 && detailsResp.status <= 209) ? 'success' : 'error'
    textInputEls.forEach(el => el.setAttribute('status', detailsStatus))

    // Send files and report result for each
    const files = fileInputIds.reduce((det, id) => {
      const inputFiles = this.getEl(id).files
      return { ...det, ...{ [id]: inputFiles.length ? inputFiles[0] : '' } }
    }, {})

    for await (const id of Object.keys(files)) {
      const file = files[id]
      if (!file) {
        this.setAttribute(id, 'status', 'warning')
      } else {
        const resp = await this.httpPostFile(file)
        if (resp.success) {
          this.setAttribute(id + 'Badge', 'status', 'success')
        } else {
          this.setAttribute(id + 'Badge', 'status', 'error')
        }
        this.setInnerHtml(id + 'Result', resp.message)
      }
    }
  }

  async saveTrades () {
    const strategyName = this.getVal('strategyNameTrades')
    const symbol = this.getVal('symbolTrades')
    const environment = this.getVal('environmentTrades')
    const platform = this.getVal('platformTrades')
    const tradesFilename = this.getInputFilename('tradesFile')
    const tradesFile = this.getInputFile('tradesFile')
    const resp = await this.httpPostTrades(tradesFile, strategyName, symbol, environment, platform)
    if (resp.success) {
      this.setAttribute('tradesBadge', 'status', 'success')
    } else {
      this.setAttribute('tradesBadge', 'status', 'error')
    }
    this.setInnerHtml('tradesResult', resp.message)
  }

  get css () {
    return `
      .add-strategy-page {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        gap: 30px;
        margin: 30px;
        overflow: scroll;
      }

      .fileUpload {
        display: flex;
        align-items: baseline;
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
          <kor-input type="text" label="Generated date (format YYYY-MM-DD)" id="generatedDate"></kor-input>
          <kor-input type="text" label="Demo date (format YYYY-MM-DD)" id="demoDate"></kor-input>
          <kor-input type="text" label="Live date (format YYYY-MM-DD)" id="liveDate"></kor-input>
          <!-- <kor-textarea label="Paste MT4 code here" rows="5" value=""></kor-textarea> -->
          <div class="fileUpload"><kor-text size="body-1">MT4 strategy file: <input type="file" label="MT4 strategy file" id="mt4StrategyFile"></input></kor-text><kor-badge id="mt4StrategyFileBadge" status=""></kor-badge><kor-text size="body-2" id="mt4StrategyFileResult"></kor-text></div>
          <div class="fileUpload"><kor-text size="body-1">SQX strategy file: <input type="file" label="SQX strategy file" id="sqxStrategyFile"></input></kor-text><kor-badge id="sqxStrategyFileBadge" status=""></kor-badge><kor-text size="body-2" id="sqxStrategyFileResult"></kor-text></div>
          <kor-button id="saveStrategy" label="Save"></kor-button>
        </kor-card>
        <kor-card icon="add_chart" label="Add Trades Report">
          <kor-input type="select" label="Environment" id="environmentTrades">
            <kor-menu-item label="Backtest" toggle></kor-menu-item>
            <kor-menu-item label="Demo" toggle></kor-menu-item>
            <kor-menu-item label="Live" toggle></kor-menu-item>
          </kor-input>
          <kor-input label="Platform" type="select" id="platformTrades" value="SQX">
            <kor-menu-item label="SQX"></kor-menu-item>
            <kor-menu-item label="MT4"></kor-menu-item>
            <kor-menu-item label="MT5"></kor-menu-item>
            <kor-menu-item label="Tradestation"></kor-menu-item>
          </kor-input>
          <kor-input type="text" label="Strategy Name" id="strategyNameTrades" value="${this.strategyName}"></kor-input>
          <kor-input type="text" label="Symbol" id="symbolTrades"></kor-input>
          <div class="fileUpload"><kor-text size="body-1">Trades CSV file: <input type="file" label="SQX strategy file" id="tradesFile"></input></kor-text><kor-badge id="tradesBadge" status=""></kor-badge><kor-text size="body-2" id="tradesResult"></kor-text></div>
          <kor-button id="saveTrades" label="Save"></kor-button>
        </kor-card>
      </div>
      `
  }
}

window.customElements.define('add-strategy', AddStrategy)
