import { BaseComponent } from './base-component.js'
import getRandomName from './getRandomName.js'

class AddStrategy extends BaseComponent {
  constructor () {
    super()
    this.strategyName = getRandomName()
  }

  connectedCallback () {
    super.connectedCallback()
    this.shadowRoot.querySelector('#save').addEventListener('click', this.save.bind(this))
  }

  async save () {
    const textInputIds = ['strategyName', 'symbols', 'timeframes', 'generatedDate', 'demoDate', 'liveDate']
    const fileInputIds = ['mt4StrategyFile', 'sqxStrategyFile', 'sqxTradesFile']
    const textInputEls = textInputIds.map(id => this.getEl(id))
    const textDetails = textInputIds.reduce((det, id) => ({ ...det, ...{ [id]: this.getEl(id).value }}), {})
    const fileDetails = fileInputIds.reduce((det, id) => {
      const files = this.getEl(id).files
      return { ...det, ...{ [id]: files.length ? files[0].name : '' } }
    }, {})

    // Send strategy details and report the status in the input boxes
    const detailsResp = await this.httpPost('/api/strategy', { ...textDetails, ...fileDetails })
    const detailsStatus = (detailsResp.status >= 200 && detailsResp) ? 'success' : 'error'
    textInputEls.forEach(el => el.setAttribute('status', detailsStatus))

    // Send files and report result for each
    for await (const id of Object.keys(fileDetails)) {
      const filename = fileDetails[id]
      if (!filename) {
        this.getEl(id).setAttribute('status', 'warning')
      } else {
        const resp = await this.httpPostFile(filename)
        this.getEl(id).setAttribute('status', (resp.status >= 200 && resp.status <= 209) ? 'success' : 'error')
      }
    }
  }

  get css () {
    return `
      .add-strategy-page {
        display: grid;
        grid-template-columns: 1fr 10fr 1fr;
        grid-template-rows: 1fr 10fr 1fr;
        grid-template-areas:
            ". . ."
            ". addBox ."
            ". . .";
      }

      .add-box {
        grid-area: addBox;
      }
    `
  }

  get html () {
    return `
      <div class="add-strategy-page">
        <kor-card class="add-box" icon="login" label="Addchart">
          <kor-input type="text" label="Strategy Name" id="strategyName" value="${this.strategyName}"></kor-input>
          <kor-input type="text" label="Symbols that the strategy operates on (separated by commas)" id="symbols"></kor-input>
          <kor-input type="text" label="Timeframes that the strategy operates on (separated by commas)" id="timeframes"></kor-input>
          <kor-input type="text" label="Generated date (format YYYY-MM-DD)" id="generatedDate"></kor-input>
          <kor-input type="text" label="Demo date (format YYYY-MM-DD)" id="demoDate"></kor-input>
          <kor-input type="text" label="Live date (format YYYY-MM-DD)" id="liveDate"></kor-input>
          <!-- <kor-textarea label="Paste MT4 code here" rows="5" value=""></kor-textarea> -->
          <kor-text size="body-1">MT4 strategy file: <input type="file" label="MT4 strategy file" id="mt4StrategyFile"></input></kor-text>
          <kor-text size="body-1">SQX strategy file: <input type="file" label="SQX strategy file" id="sqxStrategyFile"></input></kor-text>
          <kor-text size="body-1">SQX trades CSV file: <input type="file" label="SQX strategy file" id="sqxTradesFile"></input></kor-text>
          <kor-button id="save" label="Save"></kor-button>
        </kor-card>
      </div>
      `
  }
}

window.customElements.define('add-strategy', AddStrategy)
